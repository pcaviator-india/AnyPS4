content = '''
def build_notimplemented_stub_dll(dll_name, export_names, output_path, nid_db=None):
    export_entries = []
    if nid_db:
        for name in export_names:
            real = nid_db.resolve_name(name)
            export_entries.append((name, real if real != name else name))
        if resolved_map := {n: r for n, r in export_entries if n != r}:
            print(f"  NID resolution: {len(resolved_map)} of {len(export_entries)} names resolved")
    else:
        export_entries = [(n, n) for n in export_names]

    thunk = b"\x48\x31\xc0\xc3"
    text_data = bytearray()
    thunk_offsets = {}
    for name in export_names:
        thunk_offsets[name] = len(text_data)
        text_data.extend(thunk)
    while len(text_data) % 16 != 0:
        text_data.append(0)

    rdata = bytearray()
    name_offsets = {}
    rdata.extend(dll_name.encode("ascii") + b"\x00")
    for name in sorted(export_names):
        name_offsets[name] = len(rdata)
        rdata.extend(name.encode("ascii") + b"\0")
    while len(rdata) % 4 != 0:
        rdata.append(0)

    rdata_vsize = len(rdata)
    num_exp = len(export_names)
    sorted_names = sorted(export_names)

    text_vsize = len(text_data)
    text_vaddr = 0x1000
    text_vend = text_vaddr + text_vsize
    rdata_vaddr = ((text_vend + 0xfff) & ~0xfff)
    rdata_vend = rdata_vaddr + rdata_vsize
'''