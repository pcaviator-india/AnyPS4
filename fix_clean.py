p = 'c:/PersonalProjects/AnyPs4/tools-fetch/main_app.py'
with open(p, 'r') as f:
    data = f.read()
start = data.find('def _validate_setup(self):')
end = data.find('    @staticmethod', start)
old = data[start:end]
new = '''def _validate_setup(self):
    """Validate all required tools and paths before processing."""
    self._log("=== Validating setup ===")
    ok = True

    checks = [
        ("PKG folder", self.pkg_folder.get().strip(), lambda p: os.path.isdir(p)),
        ("Export folder", self.output_folder.get().strip(), lambda p: os.path.isdir(p) or self._try_mkdir(p)),
        ("Temp folder", self.temp_folder.get().strip(), lambda p: os.path.isdir(p) or self._try_mkdir(p)),
        ("PkgTool.exe", PKGTOOL_EXE, os.path.isfile),
        ("ps4_unfself.py", UNFSELF_PY, os.path.isfile),
        ("Relinker", self.relinker_path.get().strip(), os.path.isfile),
        ("NID patcher", self.nid_patcher_path.get().strip(), os.path.isfile),
    ]

    if self.copy_prx.get():
        prx_src = self.prx_source_dir.get().strip()
        checks.append(("PRX source dir", prx_src, lambda p: os.path.isdir(p) and any(Path(p).glob("*.prx"))))

    for name, path, check_fn in checks:
        if not path:
            self._log(f"  FAIL: {name} - not set")
            ok = False
        elif not check_fn(path):
            self._log(f"  FAIL: {name} - not found: {path}")
            ok = False
        else:
            self._log(f"  OK: {name} - {path}")

    # Check MinGW runtime DLLs
    self._log("  Checking MinGW runtime DLLs...")
    dll_found = False
    for dll_dir in [
        r"C:/msys64/ucrt64/bin",
        os.path.join(BASE_DIR, "mingw15", "mingw64", "bin"),
        os.path.join(BASE_DIR, "mingw16", "mingw64", "bin"),
        os.path.abspath(os.path.join(BASE_DIR, "..", "mingw16", "mingw64", "bin")),
        r"C:/PersonalProjects/AnyPs4/mingw16/mingw64/bin",
        r"C:/PersonalProjects/AnyPs4/mingw15/mingw64/bin",
    ]:
        if os.path.isdir(dll_dir):
            dlls = ["libgcc_s_seh-1.dll", "libstdc++-6.dll", "libwinpthread-1.dll"]
            missing = [d for d in dlls if not os.path.isfile(os.path.join(dll_dir, d))]
            if not missing:
                self._log(f"  OK: MinGW runtime at {dll_dir}")
                dll_found = True
                break
            else:
                self._log(f"  WARN: {dll_dir} missing: {', '.join(missing)}")
    if not dll_found:
        self._log("  WARN: No complete MinGW runtime DLL directory found")

    if ok:
        self._log("Setup validation PASSED")
        self.status.set("Validation passed")
    else:
        self._log("Setup validation FAILED - fix issues above")
        self.status.set("Validation failed")
    return ok

'''
data = data[:start] + new + data[end:]
with open(p, 'w') as f:
    f.write(data)
print('Fixed _validate_setup!')
