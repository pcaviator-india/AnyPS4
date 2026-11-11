$path = 'C:\PersonalProjects\AnyPs4\AnyPS4\core\relinker\elfpatcher\src\windows\WindowsEntryStubBuilder.cpp'
$content = Get-Content -Path $path -Raw

$startMarker = 'call("GetEnvironmentVariableW");'
$endMarker = 'code.Emit({0x31, 0xc9});'

$start = $content.IndexOf($startMarker)
$end = $content.IndexOf($endMarker, $start) + $endMarker.Length

$before = $content.Substring(0, $start)
$after = $content.Substring($end)

$replacement = @"
call("GetEnvironmentVariableW");

// ---- Log: GetEnvVar called ----
    code.Emit({0x48, 0x8D, 0x0D});                      // lea rcx, [rip + disp32]
    code.PatchBranch(code.Branch({}), stepGetEnv);
    code.Rip({0xff, 0x15}, nativeImports.Functions.at("OutputDebugStringA"));

    // ---- Parent process handling skipped (standalone execution) ----
    code.Emit({0x31, 0xc9});  // xor ecx, ecx
"@

$newContent = $before + $replacement + $after
Set-Content -Path $path -Value $newContent -Encoding UTF8
Write-Host "Replacement done"