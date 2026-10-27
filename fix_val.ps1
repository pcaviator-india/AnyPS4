$p = 'c:/PersonalProjects/AnyPs4/tools-fetch/main_app.py'
$data = [System.IO.File]::ReadAllText($p)
$idx = $data.IndexOf('        if self.copy_prx.get():')
$endIdx = $data.IndexOf('        # Patch NIDs', $idx)
$old = $data.Substring($idx, $endIdx - $idx)
$new = "        if self.copy_prx.get():`n            prx_src = self.prx_source_dir.get().strip()`n            checks.append((""PRX source dir"", prx_src, lambda p: os.path.isdir(p) and any(Path(p).glob(""*.prx""))))`n`n`n"
$data = $data.Replace($old, $new)
[System.IO.File]::WriteAllText($p, $data)
Write-Host "Fixed!"
