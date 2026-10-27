$p = 'c:/PersonalProjects/AnyPs4/tools-fetch/main_app.py'
$data = [System.IO.File]::ReadAllText($p)
$start = $data.IndexOf('def _validate_setup(self):')
$end = $data.IndexOf('    @staticmethod', $start)
$old = $data.Substring($start, $end - $start)
$new = @"
def _validate_setup(self):
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
    dll_found = $false
    for dll_dir in @(
        "C:/msys64/ucrt64/bin",
        (Join-Path $BASE_DIR "mingw15/mingw64/bin"),
        (Join-Path $BASE_DIR "mingw16/mingw64/bin"),
        (Resolve-Path (Join-Path $BASE_DIR "../mingw16/mingw64/bin")) -ErrorAction SilentlyContinue,
        "C:/PersonalProjects/AnyPs4/mingw16/mingw64/bin",
        "C:/PersonalProjects/AnyPs4/mingw15/mingw64/bin"
    ) {
        if ($null -ne $dll_dir -and (Test-Path $dll_dir)) {
            $dlls = @("libgcc_s_seh-1.dll", "libstdc++-6.dll", "libwinpthread-1.dll")
            $missing = @()
            foreach ($d in $dlls) {
                if (-not (Test-Path (Join-Path $dll_dir $d))) { $missing += $d }
            }
            if ($missing.Count -eq 0) {
                $this._log("  OK: MinGW runtime at $dll_dir")
                $dll_found = $true
                break
            } else {
                $this._log("  WARN: $dll_dir missing: $($missing -join ', ')")
            }
        }
    }
    if (-not $dll_found) {
        $this._log("  WARN: No complete MinGW runtime DLL directory found")
    }

    if ($ok) {
        $this._log("Setup validation PASSED")
        $this.status.set("Validation passed")
    } else {
        $this._log("Setup validation FAILED - fix issues above")
        $this.status.set("Validation failed")
    }
    return $ok
"@
# This is a PowerShell script that generates Python - not going to work
Write-Host "Need to use Python for this fix"
