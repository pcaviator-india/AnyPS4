#!/usr/bin/env python3
"""Minimal PE export-name reader (no external deps).

Usage: python pe_exports.py <file.pe> [<file2> ...]
"""
import os
import struct
import sys


def pe_export_names(path):
    with open(path, "rb") as handle:
        data = handle.read()
    if data[:2] != b"MZ":
        raise ValueError("not a PE file: " + path)
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe:pe + 4] != b"PE\x00\x00":
        raise ValueError("bad PE signature: " + path)
    num_sections = struct.unpack_from("<H", data, pe + 6)[0]
    opt_size = struct.unpack_from("<H", data, pe + 20)[0]
    opt = pe + 24
    magic = struct.unpack_from("<H", data, opt)[0]
    dd_off = opt + (112 if magic == 0x20B else 96)
    exp_rva, exp_size = struct.unpack_from("<II", data, dd_off)

    sections = []
    sec_off = opt + opt_size
    for index in range(num_sections):
        base = sec_off + index * 40
        vsize, vaddr, rsize, raddr = struct.unpack_from("<IIII", data, base + 8)
        sections.append((vaddr, max(vsize, rsize), raddr))

    def rva_to_offset(rva):
        for vaddr, span, raddr in sections:
            if vaddr <= rva < vaddr + span:
                return raddr + (rva - vaddr)
        return None

    if not exp_rva:
        return []
    exp_off = rva_to_offset(exp_rva)
    if exp_off is None:
        return []
    fields = struct.unpack_from("<IIHHIIIIII", data, exp_off)
    # IMAGE_EXPORT_DIRECTORY layout:
    #   0 Characteristics, 1 TimeDateStamp, 2 MajorVersion, 3 MinorVersion,
    #   4 Name, 5 Base, 6 NumberOfFunctions, 7 NumberOfNames,
    #   8 AddressOfFunctions, 9 AddressOfNames, 10 AddressOfNameOrdinals
    num_names = fields[7]
    names_rva = fields[9]
    names_off = rva_to_offset(names_rva)
    if names_off is None:
        return []
    names = []
    for index in range(num_names):
        rva = struct.unpack_from("<I", data, names_off + index * 4)[0]
        off = rva_to_offset(rva)
        if off is None:
            continue
        end = data.find(b"\x00", off)
        names.append(data[off:end].decode("ascii", "replace"))
    return names


def pe_imports(path):
    """Return {dll_name: [imported function names]} for a PE file."""
    with open(path, "rb") as handle:
        data = handle.read()
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    num_sections = struct.unpack_from("<H", data, pe + 6)[0]
    opt_size = struct.unpack_from("<H", data, pe + 20)[0]
    opt = pe + 24
    magic = struct.unpack_from("<H", data, opt)[0]
    dd_off = opt + (112 if magic == 0x20B else 96)
    import_rva, import_size = struct.unpack_from("<II", data, dd_off + 8)

    sections = []
    sec_off = opt + opt_size
    for index in range(num_sections):
        base = sec_off + index * 40
        vsize, vaddr, rsize, raddr = struct.unpack_from("<IIII", data, base + 8)
        sections.append((vaddr, max(vsize, rsize), raddr))

    def rva_to_offset(rva):
        for vaddr, span, raddr in sections:
            if vaddr <= rva < vaddr + span:
                return raddr + (rva - vaddr)
        return None

    def read_cstr(offset):
        end = data.find(b"\x00", offset)
        return data[offset:end].decode("ascii", "replace")

    if not import_rva:
        return {}
    desc_off = rva_to_offset(import_rva)
    if desc_off is None:
        return {}
    is64 = magic == 0x20B
    thunk_size = 8 if is64 else 4
    ordinal_flag = (1 << 63) if is64 else (1 << 31)
    result = {}
    while True:
        fields = struct.unpack_from("<IIIII", data, desc_off)
        if fields[0] == 0 and fields[4] == 0:
            break
        name_off = rva_to_offset(fields[3])
        dll = read_cstr(name_off) if name_off is not None else "?"
        thunk_rva = fields[0] or fields[4]
        thunk_off = rva_to_offset(thunk_rva)
        names = []
        if thunk_off is not None:
            while True:
                if is64:
                    thunk = struct.unpack_from("<Q", data, thunk_off)[0]
                else:
                    thunk = struct.unpack_from("<I", data, thunk_off)[0]
                if thunk == 0:
                    break
                if not thunk & ordinal_flag:
                    hint_off = rva_to_offset(thunk & 0x7FFFFFFF)
                    if hint_off is not None:
                        names.append(read_cstr(hint_off + 2))
                else:
                    names.append("ordinal:%d" % (thunk & 0xFFFF))
                thunk_off += thunk_size
        result.setdefault(dll, []).extend(names)
        desc_off += 20
    return result


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    for path in argv:
        try:
            names = pe_export_names(path)
        except (OSError, ValueError, struct.error) as exc:
            print(f"{path}: ERROR {exc}")
            continue
        print(f"{len(names)}\t{path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
