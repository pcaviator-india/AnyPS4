p = 'c:/PersonalProjects/AnyPs4/tools-fetch/main_app.py'
with open(p, 'r') as f:
    data = f.read()

# Append the missing code after _validate_setup
missing = '''

    @staticmethod
    def _try_mkdir(path):
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except OSError:
            return False

    # -------------------------------------------------------------- pipeline
    def _run_command(self, cmd, description):
        self._log("$ " + subprocess.list2cmdline(cmd))
        try:
            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, errors="replace", bufsize=1
            )
            if proc.stdout is not None:
                for line in proc.stdout:
                    self._log(line.rstrip())
            rc = proc.wait()
        except OSError as exc:
            raise RuntimeError(f"Could not start {description}: {exc}") from exc
        if rc != 0:
            raise RuntimeError(f"{description} exited with code {rc}")

    def _extract_pkg(self, pkg_path, out_dir):
        if not os.path.isfile(PKGTOOL_EXE):
            raise RuntimeError(f"PkgTool.exe not found: {PKGTOOL_EXE}")
        os.makedirs(out_dir, exist_ok=True)
        cmd = [
            PKGTOOL_EXE, "pkg_extract", "--passcode",
            self.passcode.get().strip() or ("0" * 32), pkg_path, out_dir
        ]
        self._run_command(cmd, "PkgTool extraction")

    def _unwrap_self(self, self_path, elf_path=None):
        if not os.path.isfile(UNFSELF_PY):
            raise RuntimeError(f"ps4_unfself.py not found: {UNFSELF_PY}")
        sys.path.insert(0, os.path.dirname(UNFSELF_PY))
        import ps4_unfself as unfself
        try:
            unfself.unwrap_self(self_path, elf_path, log=self._log)
        except Exception as exc:
            raise RuntimeError(f"SELF unwrap failed for {self_path}: {exc}") from exc
        if elf_path is not None and not os.path.isfile(elf_path):
            raise RuntimeError(f"ps4_unfself.py did not produce expected output: {elf_path}")

    def _find_eboot(self, extract_dir):
        """Find eboot.elf anywhere under uroot, with flexible search."""
        uroot = os.path.join(extract_dir, "uroot")
        if not os.path.isdir(uroot):
            return None
        eboot = os.path.join(uroot, "eboot.elf")
        if os.path.isfile(eboot):
            return eboot
        for p in Path(uroot).rglob("eboot.elf"):
            return str(p)
        for p in Path(uroot).rglob("*.elf"):
            return str(p)
        return None

    def _relink_eboot(self, extract_dir, out_dir):
        relinker = self.relinker_path.get().strip() or RELINKER_EXE
        if not os.path.isfile(relinker):
            raise RuntimeError(f"Relinker not found: {relinker}")

        eboot = self._find_eboot(extract_dir)
        if not eboot:
            raise RuntimeError(f"eboot.elf not found in {extract_dir}")

        os.makedirs(out_dir, exist_ok=True)
        out_exe = os.path.join(out_dir, "app.exe")
        cmd = [relinker, "--ps4", "--lazy-binding"]
        if self.skip_sce_module.get():
            cmd.append("--skip-sce-module")
        cmd += ["--windows", eboot, out_exe]
        self._run_command(cmd, "Relinker (Windows)")
        if not os.path.isfile(out_exe):
            raise RuntimeError(f"Relinker reported success but output is missing: {out_exe}")

        targets = self.settings.get("targets", ["windows"])
        if "linux" in targets:
            out_elf = os.path.join(out_dir, "app.elf")
            cmd_linux = [relinker, "--ps4", "--lazy-binding"]
            cmd_linux += [eboot, out_elf]
            self._run_command(cmd_linux, "Relinker (Linux)")

        return out_exe

    def _patch_nids(self, export_dir, log_cb=print):
        """Patch NIDs in the exported app.exe using our libSceGnm.prx NID mapping."""
        nid_patcher = self.nid_patcher_path.get().strip() or NID_PATCHER_EXE
        if not os.path.isfile(nid_patcher):
            log_cb(f"  SKIP NID patching: nid_patcher not found at {nid_patcher}")
            return

        libs_dir = os.path.join(export_dir, "libs")
        gnm_prx = os.path.join(libs_dir, "libSceGnm.prx")
        if not os.path.isfile(gnm_prx):
            log_cb("  SKIP NID patching: libSceGnm.prx not found in export/libs/")
            return

        export_list = os.path.join(export_dir, "libSceGnm_exports.txt")
        cmd = [nid_patcher, "--write-export-list", gnm_prx, export_list]
        try:
            self._run_command(cmd, "NID export list generation")
        except RuntimeError as exc:
            log_cb(f"  WARN: NID export list generation failed: {exc}")
            return

        app_exe = os.path.join(export_dir, "app.exe")
        if not os.path.isfile(app_exe):
            log_cb("  SKIP NID patching: app.exe not found in export dir")
            return

        cmd = [nid_patcher, "libSceGnm", "--preserve-export-list", export_list, app_exe]
        try:
            self._run_command(cmd, "NID patching")
            log_cb("  NID patching complete")
        except RuntimeError as exc:
            log_cb(f"  WARN: NID patching failed: {exc}")

    def _process_single_pkg(self, pkg_path):
        pkg_name = Path(pkg_path).name
        safe_name = Path(pkg_name).stem
        for char in "[] ":
            safe_name = safe_name.replace(char, "_")
        extract_dir = os.path.join(self.temp_folder.get(), f"temp_{safe_name}")
        export_dir = os.path.join(self.output_folder.get(), f"export_{safe_name}")

        self._log(f"=== Processing: {pkg_name} ===")
        self._log(f"  extract dir: {extract_dir}")
        self._log(f"  export dir:  {export_dir}")

        self._log("[1/5] Extracting PKG...")
        self._extract_pkg(pkg_path, extract_dir)

        self._log("[2/5] Unwrapping SELF/ELF files...")
        uroot = os.path.join(extract_dir, "uroot")
        if not os.path.isdir(uroot):
            raise RuntimeError(f"No uroot directory after extraction in {uroot}")

        self_files = sorted(
            p for p in Path(uroot).rglob("*")
            if p.is_file() and p.suffix.lower() in (".elf", ".bin", ".prx", ".sprx")
        )
        if not self_files:
            raise RuntimeError(f"No SELF/ELF files found after extraction in {uroot}")

        elf_files = []
        for src_file in self_files:
            if src_file.suffix.lower() == ".elf":
                elf_files.append(src_file)
                self._log(f"  already ELF: {src_file.name}")
            else:
                elf_path = str(src_file.with_suffix(".elf"))
                self._log(f"  unwrapping {src_file.name} -> {Path(elf_path).name}...")
                self._unwrap_self(str(src_file), elf_path)
                elf_files.append(Path(elf_path))

        if not elf_files:
            raise RuntimeError(f"No .elf files found after unwrapping in {uroot}")
        self._log(f"  Unwrap done: {len(elf_files)} ELF file(s) ready")

        self._log("[3/5] Relinking to final binary...")
        out_exe = self._relink_eboot(extract_dir, export_dir)
        self._log(f"Output file: {out_exe}")

        # Deploy app0/ game assets and metadata
        self._log("  Deploying game assets to app0/...")
        app0_dir = os.path.join(export_dir, "app0")
        populate_app0(uroot, app0_dir, log_cb=self._log)

        # Detect Title ID & Name from PKG name
        tid_match = re.search(r'(CUSA\d{5})', pkg_name, re.IGNORECASE)
        title_id = tid_match.group(1).upper() if tid_match else None
        title_name = safe_name.replace("_", " ").strip()
        ensure_param_json(app0_dir, title_id=title_id, title_name=title_name, log_cb=self._log)

        if self.copy_prx.get():
            # Step 4a: Copy original game PRX files from uroot to export/libs/
            self._log("[4a/5] Copying original game PRX stubs from extraction...")
            libs_dir = os.path.join(export_dir, "libs")
            os.makedirs(libs_dir, exist_ok=True)
            orig_copied = 0
            for src_file in Path(uroot).rglob("*.prx"):
                dst = os.path.join(libs_dir, src_file.name)
                try:
                    shutil.copy2(str(src_file), dst)
                    orig_copied += 1
                except OSError as exc:
                    self._log(f"  WARN: could not copy {src_file.name}: {exc}")
            self._log(f"  Copied {orig_copied} original PRX stub(s) from uroot")

            # Step 4b: Overlay our custom PRX stubs on top
            prx_src = find_prx_source_dir(self.prx_source_dir.get().strip())
            if prx_src:
                self._log("[4b/5] Overlaying custom .prx stubs from build...")
                self._log(f"  source: {prx_src}")
                copied, skipped, errors = copy_prx_stubs(
                    prx_src, export_dir, log_cb=self._log
                )
                if errors:
                    raise RuntimeError(
                        f"{len(errors)} .prx copy error(s): " + "; ".join(errors)
                    )
                self._log(
                    f"  Copied {copied} custom .prx stub(s), {skipped} already up to date "
                    f"-> {os.path.join(export_dir, 'libs')}"
                )
            else:
                self._log("  WARN: No custom PRX build source found; skipping overlay")
        else:
            self._log("[4/5] Skipping .prx stub copy (disabled in options)")

        # Patch NIDs so the game calls our libSceGnm implementation
        if self.patch_nids.get():
            self._log("[4.5/5] Patching NIDs in app.exe...")
            self._patch_nids(export_dir, log_cb=self._log)

        # Copy toolchain runtime DLLs needed by .prx stubs (PE/DLL) to load.
        self._log("[5/5] Copying runtime DLLs...")
        mingw_candidates = [
            r"C:/winlibs/mingw64/bin",
            os.path.join(BASE_DIR, "mingw15", "mingw64", "bin"),
            os.path.join(BASE_DIR, "mingw16", "mingw64", "bin"),
            os.path.abspath(os.path.join(BASE_DIR, "..", "mingw16", "mingw64", "bin")),
            r"C:/PersonalProjects/AnyPs4/mingw16/mingw64/bin",
            r"C:/PersonalProjects/AnyPs4/mingw15/mingw64/bin",
        ]
        mingw_bin = None
        for c in mingw_candidates:
            if os.path.isdir(c):
                mingw_bin = c
                break
        if mingw_bin:
            self._log(f"  using runtime DLL source: {mingw_bin}")
            for dll in ("libgcc_s_seh-1.dll", "libstdc++-6.dll", "libwinpthread-1.dll"):
                src = os.path.join(mingw_bin, dll)
                dst = os.path.join(export_dir, dll)
                if os.path.isfile(src):
                    try:
                        shutil.copy2(src, dst)
                        self._log(f"  copied {dll}")
                    except OSError as exc:
                        self._log(f"  WARN: could not copy {dll}: {exc}")
        else:
            self._log("  WARN: runtime DLL directory not found; .prx stubs may fail to load")

        self._log(f"[OK] {pkg_name} complete -> {export_dir}")
        return export_dir

    def _start_processing(self):
        if self.worker_thread and self.worker_thread.is_alive():
            return
        if not self.selected_pkgs:
            messagebox.showwarning("No PKGs selected", "Select one or more PKG files first.")
            return
        if not self.output_folder.get().strip():
            messagebox.showerror("Missing output folder", "Please set an export folder.")
            return
        if not self.temp_folder.get().strip():
            messagebox.showerror("Missing temp folder", "Please set a temp folder.")
            return

        if not self._validate_setup():
            messagebox.showerror("Setup validation failed", "See log for details.")
            return

        self._save_settings(silent=True)
        self.stop_requested = False
        self.btn_process.config(state=tk.DISABLED)
        total = len(self.selected_pkgs)
        self._set_progress(0, total)
        self.worker_thread = threading.Thread(
            target=self._process_pipeline,
            args=(sorted(self.selected_pkgs),),
            daemon=True,
        )
        self.worker_thread.start()

    def _request_stop(self):
        self.stop_requested = True
        self._log("Stop requested; will stop before the next PKG.")

    def _process_pipeline(self, selected_pkgs):
        total = len(selected_pkgs)
        failures = 0
        for index, pkg_path in enumerate(selected_pkgs, 1):
            if self.stop_requested:
                self._log("Stopped by user.")
                break
            self._set_status(f"[{index}/{total}] {Path(pkg_path).name}")
            self._set_progress(index - 1, total)
            try:
                self._process_single_pkg(pkg_path)
            except Exception as exc:
                failures += 1
                self._log(f"FAIL: {pkg_path}: {exc}")
        if self.stop_requested:
            final_status = "Stopped"
        elif failures:
            final_status = f"Done with {failures} failure(s)"
        else:
            final_status = "Done"
        self._set_progress(total, total)
        self._ui(self._processing_finished, final_status)

    def _processing_finished(self, final_status):
        self.status.set(final_status)
        self.btn_process.config(state=tk.NORMAL)
        self.worker_thread = None

    def _save_settings(self, silent=False):
        self.settings.update({
            "pkg_folder": self.pkg_folder.get(),
            "output_folder": self.output_folder.get(),
            "temp_folder": self.temp_folder.get(),
            "relinker_path": self.relinker_path.get(),
            "nid_patcher_path": self.nid_patcher_path.get(),
            "passcode": self.passcode.get(),
            "skip_sce_module": self.skip_sce_module.get(),
            "copy_prx": self.copy_prx.get(),
            "patch_nids": self.patch_nids.get(),
            "prx_source_dir": self.prx_source_dir.get(),
        })
        save_settings(self.settings)
        if not silent:
            self._log("Settings saved.")


def main():
    if "--no-gui" in sys.argv:
        args = [arg for arg in sys.argv[1:] if arg != "--no-gui"]
        if not args:
            print("Usage: main_app.py --no-gui <export_dir>", file=sys.stderr)
            return 2
        export_dir = args[0]
        try:
            prx_src = find_prx_source_dir()
            if not prx_src:
                raise RuntimeError(
                    f"No .prx stub source found (tried {PRX_SOURCE_DIR} "
                    f"and {PRX_SOURCE_DIR_ALT})"
                )
            copied, skipped, errors = copy_prx_stubs(prx_src, export_dir)
            if errors:
                print(f"FAIL: {len(errors)} copy error(s): " + "; ".join(errors),
                      file=sys.stderr)
                return 1
            print(
                f"Copied {copied} .prx stub(s), {skipped} already up to date "
                f"-> {os.path.join(export_dir, 'libs')}"
            )
            return 0
        except RuntimeError as exc:
            print(f"FAIL: {exc}", file=sys.stderr)
            return 1

    root = tk.Tk()
    App(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
'''
data = data + missing
with open(p, 'w') as f:
    f.write(data)
print('Restored missing code!')
