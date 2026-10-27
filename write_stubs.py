import os

content = r'''"""Phase 2: Build NotImplemented stub PRX DLLs for unresolved NID imports."""
import os
import re
import struct
from pathlib import Path

from nid_db import NidDatabase


def pe_imports(path):
    with open(path, "rb") as f:
        data = f.read()
    pe_off = struct.unpack_from("<I", data, 0x3C)[0]
    opt_off = pe_off + 24
    size_opt_header = struct.unpack_from("<H", data, pe_off + 20)[0]
    num_sections = struct.unpack_from("<H", data, pe_off + 6)[0]
    sec_off = opt_off + size_opt_header

    def rva_to_offset(rva):
        for i in range(num_sections):
            base = sec_off + i * 40
            vsize, vaddr, rsize, raddr = struct.unpack_from("<IIII", data, base + 8)
            if vaddr <= rva < vaddr + max(vsize, rsize):
                return raddr + (rva - vaddr)
        return None

    magic = struct.unpack_from("<H", data, opt_off)[0]
    dd_start = opt_off + (112 if magic == 0x20B else 96)
    imp_rva, imp_size = struct.unpack_from("<II", data, dd_start + 1 * 8)
    if not imp_rva:
        return {}

    result = {}
    imp_off = rva_to_offset(imp_rva)
    if not imp_off:
        return result

    i = 0
    while True:
        entry_off = imp_off + i * 20
        if entry_off + 20 > len(data):
            break
        orig_thunk, timestamp, fwd_chain, name_rva, iat_rva = struct.unpack_from(
            "<IIIII", data, entry_off
        )
        if name_rva == 0:
            break
        name_off = rva_to_offset(name_rva)
        dll_name = data[name_off:data.find(b"\x00", name_off)].decode("ascii", "replace") if name_off else ""

        iat_off = rva_to_offset(iat_rva)
        imports = []
        j = 0
        while iat_off is not None:
            val_off = iat_off + j * 8
            val = struct.unpack_from("<Q", data, val_off)[0] if val_off + 8 <= len(data) else 0
            if val == 0:
                break
            if not (val & 0x8000000000000000):
                hint_off = rva_to_offset(val & 0xFFFFFFFFFFFFFFFF)
                if hint_off:
                    fn_off = hint_off + 2
                    end = data.find(b"\x00", fn_off)
                    if end > fn_off:
                        imports.append(data[fn_off:end].decode("ascii", "replace"))
            j += 1
        if dll_name:
            result[dll_name] = imports
        i += 1
    return result


def prx_export_names(prx_path):
    with open(prx_path, "rb") as f:
        data = f.read()
    pe_off = struct.unpack_from("<I", data, 0x3C)[0]
    opt_off = pe_off + 24
    size_opt_header = struct.unpack_from("<H", data, pe_off + 20)[0]
    num_sections = struct.unpack_from("<H", data, pe_off + 6)[0]
    sec_off = opt_off + size_opt_header

    def rva_to_offset(rva):
        for i in range(num_sections):
            base = sec_off + i * 40
            vsize, vaddr, rsize, raddr = struct.unpack_from("<IIII", data, base + 8)
            if vaddr <= rva < vaddr + max(vsize, rsize):
                return raddr + (rva - vaddr)
        return None

    magic = struct.unpack_from("<H", data, opt_off)[0]
    dd_start = opt_off + (112 if magic == 0x20B else 96)
    exp_rva, exp_size = struct.unpack_from("<II", data, dd_start)
    if not exp_rva:
        return set()

    exp_off = rva_to_offset(exp_rva)
    if not exp_off:
        return set()

    fields = struct.unpack_from("<IIHHIIIIIII", data, exp_off)
    num_names = fields[7]
    aon_rva = fields[9]
    aon_off = rva_to_offset(aon_rva)
    if not aon_off:
        return set()

    names = set()
    for i in range(num_names):
        nrva = struct.unpack_from("<I", data, aon_off + i * 4)[0]
        noff = rva_to_offset(nrva)
        if noff:
            end = data.find(b"\x00", noff)
            names.add(data[noff:end].decode("ascii", "replace"))
    return names
'''

with open('c:/PersonalProjects/AnyPs4/tools-fetch/phase2_stubs.py', 'w') as f:
    f.write(content)

print("Part 1 written")
