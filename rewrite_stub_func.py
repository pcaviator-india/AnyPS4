import re

with open('c:/PersonalProjects/AnyPs4/tools-fetch/phase2_stubs.py', 'r') as f:
    lines = f.readlines()

# Find function boundaries
func_start = None
func_end = None
for i, line in enumerate(lines):
    if line.startswith('def build_notimplemented_stub_dll('):
        func_start = i
    if func_start is not None and line.startswith('def create_missing_prx_stubs'):
        func_end = i
        break

if func_start is None or func_end is None:
    print(f"Could not find boundaries: start={func_start}, end={func_end}")
    exit(1)

print(f"Replacing lines {func_start+1} to {func_end}")

new_func = '''def build_notimplemented_stub_dll(dll_name, export_names, output_path, nid_db=None):
    """Build a minimal x64 PE DLL that exports each name in export_names.

    Exports return a pointer to a fake vtable in .rdata (32 entries,
    each pointing to a "return 0" thunk), so virtual method calls on
    stub-returned objects safely return 0 instead of crashing on a NULL
    vtable dereference.

    If *nid_db* is provided, NID names are resolved to human-readable
    names.
    """
    export_entries = []
    if nid_db:
        for name in export_names:
            real = nid_db.resolve_name(name)
            export_entries.append((name, real if real != name else name))
        if resolved_map := {n: r for n, r in export_entries if n != r}:
            print(f"  NID resolution: {len(resolved_map)} of {len(export_entries)} "
                  f"names resolved from database")
    else:
        export_entries = [(n, n) for n in export_names]

    ret_zero_thunk = b"\\x48\\x31\\xc0\\xc3"
    text_data = bytearray()
    thunk_offsets = {}
    ret_zero_offset = len(text_data)
    text_data.extend(ret_zero_thunk)

    for orig_name, disp_name in export_entries:
        thunk_offsets[orig_name] = len(text_data)
        text_data.extend(b"\\x48\\xb8")
        text_data.extend(b"\\x00" * 8)
        text_data.extend(b"\\xc3")

    while len(text_data) % 16 != 0:
        text_data.append(0)

    rdata = bytearray()
    name_offsets = {}
    rdata.extend(dll_name.encode("ascii") + b"\\x00")
    fake_vtable_offset_in_rdata = len(rdata)
    for _ in range(32):
        rdata.extend(struct.pack("<Q", 0))

    for orig_name, disp_name in sorted(export_entries):
        name_offsets[orig_name] = len(rdata)
        rdata.extend(orig_name.encode("ascii") + b"\\0")
    while len(rdata) % 4 != 0:
        rdata.append(0)

    rdata_vsize = len(rdata)
    num_exp = len(export_entries)
    sorted_orig_names = sorted([e[0] for e in export_entries])

    text_vsize = len(text_data)
    text_vaddr = 0x1000
    text_vend = text_vaddr + text_vsize
    rdata_vaddr = ((text_vend + 0xfff) & ~0xfff)
    rdata_vend = rdata_vaddr + rdata_vsize

    eat = bytearray()
    for orig_name in sorted_orig_names:
        eat.extend(struct.pack("<I", text_vaddr + thunk_offsets[orig_name]))

    nt = bytearray()
    for orig_name in sorted_orig_names:
        nt.extend(struct.pack("<I", rdata_vaddr + name_offsets[orig_name]))

    ot = bytearray()
    for i in range(num_exp):
        ot.extend(struct.pack("<H", i))

    image_base = 0x180000000
    ret_zero_rva = text_vaddr + ret_zero_offset
    ret_zero_va = image_base + ret_zero_rva

    for i in range(32):
        struct.pack_into("<Q", rdata, fake_vtable_offset_in_rdata + i * 8, ret_zero_va)

    fake_vtable_rva = rdata_vaddr + fake_vtable_offset_in_rdata
    for orig_name in sorted_orig_names:
        thunk_off = thunk_offsets[orig_name]
        struct.pack_into("<Q", text_data, thunk_off + 2, fake_vtable_rva)

    dll_name_bytes = dll_name.encode("ascii") + b"\\x00"
    edata_raw_size = 40 + len(dll_name_bytes) + len(eat) + len(nt) + len(ot)
    edata_vsize = (edata_raw_size + 15) & ~15
    edata_vaddr = ((rdata_vend + 0xfff) & ~0xfff)

    exp_dir = bytearray(40)
    struct.pack_into("<I", exp_dir, 0, 0)
    struct.pack_into("<I", exp_dir, 4, 0)
    struct.pack_into("<H", exp_dir, 8, 0)
    struct.pack_into("<H", exp_dir, 10, 0)
    struct.pack_into("<I", exp_dir, 12, rdata_vaddr)
    struct.pack_into("<I", exp_dir, 16, 1)
    struct.pack_into("<I", exp_dir, 20, num_exp)
    struct.pack_into("<I", exp_dir, 24, num_exp)
    eat_rva = edata_vaddr + 40 + len(dll_name_bytes)
    nt_rva = eat_rva + len(eat)
    ot_rva = nt_rva + len(nt)
    struct.pack_into("<I", exp_dir, 28, eat_rva)
    struct.pack_into("<I", exp_dir, 32, nt_rva)
    struct.pack_into("<I", exp_dir, 36, ot_rva)

    edata = bytearray()
    edata.extend(exp_dir)
    edata.extend(dll_name_bytes)
    edata.extend(eat)
    edata.extend(nt)
    edata.extend(ot)
    while len(edata) % 16 != 0:
        edata.append(0)
'''

new_lines = lines[:func_start] + [new_func] + lines[func_end:]

with open('c:/PersonalProjects/AnyPs4/tools-fetch/phase2_stubs.py', 'w') as f:
    f.writelines(new_lines)

print(f"Replaced {func_end - func_start} lines with {len(new_func.split(chr(10)))} lines")