with open(r'C:\PersonalProjects\AnyPs4\AnyPS4\core\relinker\elfpatcher\src\windows\WindowsEntryStubBuilder.cpp', 'r') as f:
    content = f.read()

old = '''    // Check faulting address < 0x1000 (NULL page access)
    code.Emit({0x41, 0x81, 0xF9, 0x00, 0x10, 0x00, 0x00});        // cmp r9, 0x1000
    auto nullPageJump = code.Branch({0x0F, 0x83});                // jae .log_and_search

    // Skip faulting instruction: RIP += 7 (covers mov [reg+disp], reg patterns)
    code.Emit({0x48, 0x8B, 0x41, 0x08});                          // mov rax, [rcx + 8]      ; ContextRecord = ExceptionInfo[8]
    code.Emit({0x48, 0x83, 0x80, 0xA8, 0x0A, 0x00, 0x00, 0x07});  // add qword ptr [rax + 0xA8], 7 ; RIP += 7
    code.Emit({0xB8, 0xFF, 0xFF, 0xFF, 0xFF});                    // mov eax, -1             ; EXCEPTION_CONTINUE_EXECUTION
    auto doneJump = code.Branch({0xEB});                          // jmp .done (short jump)

    // .log_and_search:
    const auto logAndSearchRva = code.GetRva();
    code.Emit({0x48, 0x8D, 0x0D});                                // lea rcx, [rip + disp32]
    code.PatchBranch(code.Branch({}), exceptionInElf);
    code.Rip({0xff, 0x15}, nativeImports.Functions.at("OutputDebugStringA"));
    code.Emit({0x31, 0xC0});                                      // xor eax, eax (EXCEPTION_CONTINUE_SEARCH)

    // .done:
    const auto doneRva = code.GetRva();
    code.Emit({0x48, 0x89, 0xEC});                                // mov rsp, rbp
    code.Emit({0x5D});                                            // pop rbp
    code.Emit({0xC3});                                            // ret

    // Patch forward branches
    code.PatchBranch(avCheckJump, logAndSearchRva);
    code.PatchBranch(nullPageJump, logAndSearchRva);
    code.PatchBranch(doneJump, doneRva);'''

new = '''    // Check faulting address < 0x1000 (NULL page access) -> skip instruction
    code.Emit({0x41, 0x81, 0xF9, 0x00, 0x10, 0x00, 0x00});        // cmp r9, 0x1000
    auto nullPageJump = code.Branch({0x0F, 0x83});                // jae .try_commit_page

    // Skip faulting instruction: RIP += 7 (covers mov [reg+disp], reg patterns)
    code.Emit({0x48, 0x8B, 0x41, 0x08});                          // mov rax, [rcx + 8]      ; ContextRecord = ExceptionInfo[8]
    code.Emit({0x48, 0x83, 0x80, 0xA8, 0x0A, 0x00, 0x00, 0x07});  // add qword ptr [rax + 0xA8], 7 ; RIP += 7
    code.Emit({0xB8, 0xFF, 0xFF, 0xFF, 0xFF});                    // mov eax, -1             ; EXCEPTION_CONTINUE_EXECUTION
    auto doneJump = code.Branch({0xEB});                          // jmp .done (short jump)

    // .try_commit_page: try to commit the faulting page
    const auto tryCommitRva = code.GetRva();
    // Page-align faulting address: r9 &= ~0xFFF
    code.Emit({0x49, 0x81, 0xE1, 0xFF, 0xFF, 0xFF, 0xF0});        // and r9, 0xFFFFFFFFFFFFF000
    // VirtualAlloc(lpAddress, dwSize, flAllocationType, flProtect)
    code.Emit({0x48, 0x89, 0xC9});                                // mov rcx, r9             ; lpAddress = page-aligned faulting address
    code.Emit({0x48, 0xC7, 0xC2, 0x00, 0x10, 0x00, 0x00});        // mov rdx, 0x1000         ; dwSize = 4KB
    code.Emit({0x49, 0xC7, 0xC0, 0x00, 0x10, 0x00, 0x00});        // mov r8, 0x3000          ; flAllocationType = MEM_RESERVE|MEM_COMMIT
    code.Emit({0x49, 0xC7, 0xC1, 0x04, 0x00, 0x00, 0x00});        // mov r9, 0x4             ; flProtect = PAGE_READWRITE
    code.Rip({0xff, 0x15}, nativeImports.Functions.at("VirtualAlloc"));  // call VirtualAlloc
    code.Emit({0xB8, 0xFF, 0xFF, 0xFF, 0xFF});                    // mov eax, -1             ; EXCEPTION_CONTINUE_EXECUTION
    auto commitDoneJump = code.Branch({0xEB});                    // jmp .done

    // .log_and_search:
    const auto logAndSearchRva = code.GetRva();
    code.Emit({0x48, 0x8D, 0x0D});                                // lea rcx, [rip + disp32]
    code.PatchBranch(code.Branch({}), exceptionInElf);
    code.Rip({0xff, 0x15}, nativeImports.Functions.at("OutputDebugStringA"));
    code.Emit({0x31, 0xC0});                                      // xor eax, eax (EXCEPTION_CONTINUE_SEARCH)

    // .done:
    const auto doneRva = code.GetRva();
    code.Emit({0x48, 0x89, 0xEC});                                // mov rsp, rbp
    code.Emit({0x5D});                                            // pop rbp
    code.Emit({0xC3});                                            // ret

    // Patch forward branches
    code.PatchBranch(avCheckJump, logAndSearchRva);
    code.PatchBranch(nullPageJump, tryCommitRva);
    code.PatchBranch(doneJump, doneRva);
    code.PatchBranch(commitDoneJump, doneRva);'''

if old in content:
    content = content.replace(old, new)
    with open(r'C:\PersonalProjects\AnyPs4\AnyPS4\core\relinker\elfpatcher\src\windows\WindowsEntryStubBuilder.cpp', 'w') as f:
        f.write(content)
    print('Replacement successful')
else:
    print('OLD TEXT NOT FOUND')
    # Debug: show what's actually there
    start = content.find('// Check faulting address')
    end = content.find('// Patch forward branches')
    if start >= 0 and end >= 0:
        print('Actual content:')
        print(repr(content[start:end]))