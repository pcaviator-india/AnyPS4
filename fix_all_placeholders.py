import re

with open('c:/PersonalProjects/AnyPs4/tools-fetch/phase2_stubs.py', 'r') as f:
    lines = f.readlines()

# Find the log_stub_call section boundaries
start_line = None
end_line = None
for i, line in enumerate(lines):
    if 'log_stub_call_offset = len(text_data)' in line:
        start_line = i
    if 'log_stub_call_size = len(text_data) - log_stub_call_offset' in line:
        end_line = i
        break

if start_line is None or end_line is None:
    print("Could not find log_stub_call section boundaries")
    exit(1)

print(f"log_stub_call section: lines {start_line+1} to {end_line+1}")

# Collect all fixup targets we'll need after RVAs are known
# These will be added as fixup entries after section layout

# Replace all manual placeholder patterns within log_stub_call section
# Pattern 1: lea rcx, [rip + disp32] -> add_lea_rcx_disp32() + fixup tracking
# Pattern 2: lea rdx, [rip + disp32] -> add_lea_rdx_disp32() + fixup tracking  
# Pattern 3: lea r9, [rip + disp32] -> add_lea_r9_disp32() + fixup tracking
# Pattern 4: call [rip + disp32] -> add_call_iat() + fixup tracking
# Pattern 5: mov [rip + disp32], rax -> add_mov_rip_disp32() + fixup tracking

# We need to track which target each fixup refers to. Let's do this by examining
# the comments on each line to determine the target kind.

new_lines = []
fixup_counter = 0

for i in range(start_line, end_line + 1):
    line = lines[i]
    
    # Check for lea rcx [rip] pattern followed by zero disp32
    if 'text_data.extend(b"\\x48\\x8d\\x0d")' in line and i+1 < len(lines) and 'text_data.extend(b"\\x00\\x00\\x00\\x00")' in lines[i+1]:
        # Determine target from comment
        comment = line.split('#')[-1] if '#' in line else ''
        if 'filename' in comment.lower() or 'stub_calls' in comment.lower():
            target = 'filename'
        elif 'hFile' in comment or 'handle' in comment.lower():
            target = 'hfile_global'
        else:
            target = 'unknown_rcx'
        
        new_lines.append(f'    fixup_{fixup_counter} = add_lea_rcx_disp32()\n')
        new_lines.append(f'    log_stub_fixups.append((fixup_{fixup_counter}, \\'{target}\\'))\n')
        fixup_counter += 1
        # Skip the next line (the zero disp32 placeholder)
        i += 1
        continue
    
    # Check for lea rdx [rip] pattern
    if 'text_data.extend(b"\\x48\\x8d\\x15")' in line and i+1 < len(lines) and 'text_data.extend(b"\\x00\\x00\\x00\\x00")' in lines[i+1]:
        comment = line.split('#')[-1] if '#' in line else ''
        if 'NID=' in comment:
            target = 'nid_prefix'
        elif 'NAME=' in comment or 'name' in comment.lower():
            target = 'name_prefix'
        elif 'RET=' in comment:
            target = 'ret_prefix'
        elif '\\\\n' in comment or 'newline' in comment.lower():
            target = 'newline'
        else:
            target = 'unknown_rdx'
        
        new_lines.append(f'    fixup_{fixup_counter} = add_lea_rdx_disp32()\n')
        new_lines.append(f'    log_stub_fixups.append((fixup_{fixup_counter}, \\'{target}\\'))\n')
        fixup_counter += 1
        i += 1
        continue
    
    # Check for lea r9 [rip] pattern (&written)
    if 'text_data.extend(b"\\x48\\x8d\\x0d")' in line and 'r9' in line.lower() and i+1 < len(lines) and 'text_data.extend(b"\\x00\\x00\\x00\\x00")' in lines[i+1]:
        new_lines.append(f'    fixup_{fixup_counter} = add_lea_r9_disp32()\n')
        new_lines.append(f'    log_stub_fixups.append((fixup_{fixup_counter}, \\'written_var\\'))\n')
        fixup_counter += 1
        i += 1
        continue
    
    # Check for call [rip] pattern (IAT calls)
    if 'text_data.extend(b"\\xff\\x15")' in line and i+1 < len(lines) and 'text_data.extend(b"\\x00\\x00\\x00\\x00")' in lines[i+1]:
        comment = line.split('#')[-1] if '#' in line else ''
        if 'CreateFile' in comment:
            target = 'createfile_iat'
        elif 'WriteFile' in comment:
            target = 'writefile_iat'
        elif 'CloseHandle' in comment:
            target = 'closehandle_iat'
        else:
            target = 'unknown_iat'
        
        new_lines.append(f'    fixup_{fixup_counter} = add_call_iat()\n')
        new_lines.append(f'    log_stub_fixups.append((fixup_{fixup_counter}, \\'{target}\\'))\n')
        fixup_counter += 1
        i += 1
        continue
    
    # Check for mov [rip + disp32], rax pattern (hFile_global store)
    if 'text_data.extend(b"\\x48\\x89\\x05")' in line and i+1 < len(lines) and 'text_data.extend(b"\\x00\\x00\\x00\\x00")' in lines[i+1]:
        new_lines.append(f'    fixup_{fixup_counter} = add_mov_rip_disp32()\n')
        new_lines.append(f'    log_stub_fixups.append((fixup_{fixup_counter}, \\'hfile_global\\'))\n')
        fixup_counter += 1
        i += 1
        continue
    
    new_lines.append(line)

# Replace the section
new_content = lines[:start_line] + new_lines + lines[end_line+1:]

with open('c:/PersonalProjects/AnyPs4/tools-fetch/phase2_stubs.py', 'w') as f:
    f.writelines(new_content)

print(f"Replaced {fixup_counter} placeholders with tracked fixups")
print(f"Total lines changed: {len(new_lines)} vs {end_line - start_line + 1}")