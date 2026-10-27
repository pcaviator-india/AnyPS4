import re

with open('c:/PersonalProjects/AnyPs4/tools-fetch/phase2_stubs.py', 'r') as f:
    content = f.read()

# Replace all remaining manual placeholder patterns in log_stub_call
# Pattern: lea rdx, [rip + disp32] followed by 4 zero bytes -> use add_lea_rdx_disp32()
# Pattern: lea r9, [rip + disp32] followed by 4 zero bytes -> use add_lea_r9_disp32()
# Pattern: call [rip + disp32] followed by 4 zero bytes -> use add_call_iat()
# Pattern: mov [rip + disp32], rax followed by 4 zero bytes -> use add_mov_rip_disp32()

# We need to be careful: only replace patterns inside log_stub_call function
# (between "log_stub_call_offset = len(text_data)" and "log_stub_call_size = len(text_data)")

# Find the log_stub_call section
start_marker = "log_stub_call_offset = len(text_data)"
end_marker = "log_stub_call_size = len(text_data) - log_stub_call_offset"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx < 0 or end_idx < 0:
    print("Could not find log_stub_call section")
    exit(1)

section = content[start_idx:end_idx + len(end_marker)]

# Replace manual placeholders with tracked versions inside this section
# We need to track fixups for each replacement

# First, let's replace the lea rcx [rip] patterns (for filename string)
# These appear as: text_data.extend(b"\x48\x8d\x0d") + text_data.extend(b"\x00\x00\x00\x00")
# We need to replace with: fixup_X = add_lea_rcx_disp32(); log_stub_fixups.append((fixup_X, 'target'))

# Actually, this is too complex for regex. Let me just manually verify the current state
# and add the fixup code at the end.

print(f"Section length: {end_idx - start_idx}")
print(f"Section starts at line {content[:start_idx].count(chr(10)) + 1}")
print(f"Section ends at line {content[:end_idx].count(chr(10)) + 1}")

# Count remaining manual placeholders in the section
lea_rcx_count = section.count('text_data.extend(b"\\x48\\x8d\\x0d")')
lea_rdx_count = section.count('text_data.extend(b"\\x48\\x8d\\x15")')
call_count = section.count('text_data.extend(b"\\xff\\x15")')
mov_rip_count = section.count('text_data.extend(b"\\x48\\x89\\x05")')

print(f"Remaining lea rcx [rip] patterns: {lea_rcx_count}")
print(f"Remaining lea rdx [rip] patterns: {lea_rdx_count}")
print(f"Remaining call [rip] patterns: {call_count}")
print(f"Remaining mov [rip] patterns: {mov_rip_count}")