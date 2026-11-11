import struct

with open(r'C:\PS4\export_Limbo.PS4-PRELUDE\app.exe', 'rb') as f:
    f.seek(0x3c)
    pe_off = struct.unpack('<I', f.read(4))[0]
    f.seek(pe_off + 4 + 2)
    num_sections = struct.unpack('<H', f.read(2))[0]
    f.seek(pe_off + 4 + 16)
    opt_size = struct.unpack('<H', f.read(2))[0]
    sec_off = pe_off + 4 + 20 + opt_size
    sections = []
    for i in range(num_sections):
        f.seek(sec_off + i * 40)
        name = f.read(8).rstrip(b'\x00').decode('latin1', 'ignore')
        vsize, vrva, rsize, roff = struct.unpack('<IIII', f.read(16))
        sections.append({'name': name, 'vrva': vrva, 'vsize': vsize, 'roff': roff, 'rsize': rsize})

    def rva_to_file(rva):
        for s in sections:
            if s['vrva'] <= rva < s['vrva'] + max(s['vsize'], s['rsize']):
                return s['roff'] + (rva - s['vrva'])
        return None

    procpar_sec = next(s for s in sections if s['name'] == '.procpar')
    f.seek(procpar_sec['roff'])
    addr, sz = struct.unpack('<II', f.read(8))
    print(f".procpar points to RVA 0x{addr:x}, sz 0x{sz:x}")

    proc_file_off = rva_to_file(addr)
    f.seek(proc_file_off)
    hdr = f.read(0x40)
    sz64, magic = struct.unpack('<QI', hdr[:12])
    print(f"ProcParams: size=0x{sz64:x}, magic=0x{magic:x}")
    libc_params_va = struct.unpack('<Q', hdr[0x38:0x40])[0]
    print(f"libc_params_va: 0x{libc_params_va:x}")

    libc_file_off = rva_to_file(libc_params_va - 0x140000000)
    print(f"libc_params file offset: {hex(libc_file_off) if libc_file_off else 'None'}")
    if libc_file_off:
        f.seek(libc_file_off)
        lhdr = f.read(0x38)
        lsz = struct.unpack('<Q', lhdr[:8])[0]
        repl_va = struct.unpack('<Q', lhdr[0x30:0x38])[0]
        print(f"libc_params: size=0x{lsz:x}, repl_va=0x{repl_va:x}")
        repl_file_off = rva_to_file(repl_va - 0x140000000)
        print(f"replacement table file offset: {hex(repl_file_off) if repl_file_off else 'None'}")
        if repl_file_off:
            f.seek(repl_file_off)
            repl_hdr = f.read(0x20 + 80)
            rsz, rver, rinit, rfini = struct.unpack('<QQQQ', repl_hdr[:0x20])
            print(f"repl: size=0x{rsz:x}, ver=0x{rver:x}, init=0x{rinit:x}, fini=0x{rfini:x}")
            api = struct.unpack('<10Q', repl_hdr[0x20:0x20+80])
            for idx, a in enumerate(api):
                print(f"  api[{idx}] = 0x{a:016x}")
