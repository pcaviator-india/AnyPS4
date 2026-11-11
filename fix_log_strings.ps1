$path = 'C:\PersonalProjects\AnyPs4\AnyPS4\core\relinker\elfpatcher\src\windows\WindowsEntryStubBuilder.cpp'
$content = Get-Content -Path $path -Raw

$old1 = "    // ---- Log: Before SetCurrentDirectory ----\n    code.Emit({0x48, 0x8D, 0x0D});                      // lea rcx, [rip + disp32]\n    code.PatchBranch(code.Branch({}), stepGetMod);\n    code.Rip({0xff, 0x15}, nativeImports.Functions.at(\"OutputDebugStringA\"));\n\n    code.Rip({0x48, 0x8d, 0x0d}, modulePath);\n    call(\"SetCurrentDirectoryW\");\n\n    // ---- Log: After SetCurrentDirectory ----\n    code.Emit({0x48, 0x8D, 0x0D});                      // lea rcx, [rip + disp32]\n    code.PatchBranch(code.Branch({}), stepGetMod);"

$new1 = "    // ---- Log: Before SetCurrentDirectory ----\n    code.Emit({0x48, 0x8D, 0x0D});                      // lea rcx, [rip + disp32]\n    code.PatchBranch(code.Branch({}), stepBeforeSetDir);\n    code.Rip({0xff, 0x15}, nativeImports.Functions.at(\"OutputDebugStringA\"));\n\n    code.Rip({0x48, 0x8d, 0x0d}, modulePath);\n    call(\"SetCurrentDirectoryW\");\n\n    // ---- Log: After SetCurrentDirectory ----\n    code.Emit({0x48, 0x8D, 0x0D});                      // lea rcx, [rip + disp32]\n    code.PatchBranch(code.Branch({}), stepAfterSetDir);"

$newContent = $content.Replace($old1, $new1)
Set-Content -Path $path -Value $newContent -Encoding UTF8
Write-Host "Done"