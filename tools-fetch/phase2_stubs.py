"""Phase 2: Build NotImplemented stub PRX DLLs for unresolved NID imports."""
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

    # Build per-export log strings: "NID=<orig> NAME=<disp>\n"
    log_strings = {}  # name -> (offset_in_log_string_data, length)
    log_string_data = bytearray()
    for orig_name, disp_name in export_entries:
        log_str = f"NID={orig_name} NAME={disp_name}\n".encode("ascii")
        log_strings[orig_name] = (len(log_string_data), len(log_str))
        log_string_data.extend(log_str)

    # Pre-compute log string offsets within .rdata (after DLL name + export names)
    log_string_offsets = {}
    rdata_offset = len(dll_name.encode("ascii") + b"\x00")
    for name in sorted(export_names):
        rdata_offset += len(name.encode("ascii") + b"\0")
    for orig_name in sorted(export_names):
        log_string_offsets[orig_name] = rdata_offset
        rdata_offset += log_strings[orig_name][1]

    # Thunk: lea rcx, [rip+disp32] -> log string; call OutputDebugStringA; xor rax, rax; ret
    text_data = bytearray()
    thunk_offsets = {}
    thunk_fixups = []  # (text_offset_for_disp32, kind, export_name)
    for orig_name, disp_name in export_entries:
        thunk_start = len(text_data)
        thunk_offsets[orig_name] = thunk_start
        # lea rcx, [rip + disp32] -> log string
        text_data.extend(b"\x48\x8d\x0d")
        fixup_str = len(text_data)
        text_data.extend(b"\x00\x00\x00\x00")
        thunk_fixups.append((fixup_str, 'log_string', orig_name))
        # call OutputDebugStringA (IAT[0])
        text_data.extend(b"\xff\x15")
        fixup_ods = len(text_data)
        text_data.extend(b"\x00\x00\x00\x00")
        thunk_fixups.append((fixup_ods, 'ods_iat', orig_name))
        # xor rax, rax
        text_data.extend(b"\x48\x31\xc0")
        # ret
        text_data.extend(b"\xc3")
    while len(text_data) % 16 != 0:
        text_data.append(0)

    text_vsize = len(text_data)
    text_vaddr = 0x1000
    text_vend = text_vaddr + text_vsize
    rdata_vaddr = ((text_vend + 0xfff) & ~0xfff)

    rdata = bytearray()
    name_offsets = {}
    rdata.extend(dll_name.encode("ascii") + b"\x00")
    for name in sorted(export_names):
        name_offsets[name] = len(rdata)
        rdata.extend(name.encode("ascii") + b"\0")
    # Append log strings after export names (offsets pre-computed above)
    for orig_name in sorted(export_names):
        rdata.extend(log_string_data[log_strings[orig_name][0]:log_strings[orig_name][0] + log_strings[orig_name][1]])
    while len(rdata) % 4 != 0:
        rdata.append(0)

    rdata_vsize = len(rdata)
    num_exp = len(export_names)
    sorted_names = sorted(export_names)

    rdata_vend = rdata_vaddr + rdata_vsize

    eat = bytearray()
    for name in sorted_names:
        eat.extend(struct.pack("<I", text_vaddr + thunk_offsets[name]))

    nt = bytearray()
    for name in sorted_names:
        nt.extend(struct.pack("<I", rdata_vaddr + name_offsets[name]))

    ot = bytearray()
    for i in range(num_exp):
        ot.extend(struct.pack("<H", i))

    image_base = 0x180000000

    dll_name_bytes = dll_name.encode("ascii") + b"\x00"
    edata_raw_size = 40 + len(dll_name_bytes) + len(eat) + len(nt) + len(ot)
    edata_vsize = (edata_raw_size + 15) & ~15
    edata_vaddr = ((rdata_vend + 0xfff) & ~0xfff)

    exp_dir = bytearray(40)
    struct.pack_into("<I", exp_dir, 0, 0)
    struct.pack_into("<I", exp_dir, 4, 0)
    struct.pack_into("<H", exp_dir, 8, 0)
    struct.pack_into("<H", exp_dir, 10, 0)
    struct.pack_into("<I", exp_dir, 12, rdata_vaddr)
    struct.pack_into("<I", exp_dir, 16, 0)
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
    # ------------------------------------------------------------------
    # .idata section: OutputDebugStringA import from kernel32.dll
    # ------------------------------------------------------------------
    idata = bytearray()
    # Import Lookup Table: 1 entry + null terminator
    ilt_start = len(idata)
    idata.extend(struct.pack("<Q", 0))  # placeholder
    # Import Address Table: 1 entry + null terminator
    iat_start = len(idata)
    idata.extend(struct.pack("<Q", 0))  # placeholder
    # Hint/Name Table: WORD hint + "OutputDebugStringA\x00"
    hint_name_start = len(idata)
    idata.extend(struct.pack("<H", 0))
    idata.extend(b"OutputDebugStringA\x00")
    while len(idata) % 2 != 0:
        idata.append(0)
    # DLL name: "KERNEL32.dll\x00"
    dll_name_start = len(idata)
    idata.extend(b"KERNEL32.dll\x00")
    while len(idata) % 2 != 0:
        idata.append(0)
    # Import Descriptor (20 bytes)
    import_desc_start = len(idata)
    idata.extend(struct.pack("<IIIII", 0, 0, 0, 0, 0))  # placeholder
    # Null import descriptor (terminator)
    idata.extend(struct.pack("<IIIII", 0, 0, 0, 0, 0))
    idata_vsize = len(idata)
    idata_vaddr = ((edata_vaddr + edata_vsize + 0xfff) & ~0xfff)
    # Fix up idata entries
    struct.pack_into("<Q", idata, ilt_start, idata_vaddr + hint_name_start)
    struct.pack_into("<Q", idata, iat_start, idata_vaddr + hint_name_start)
    struct.pack_into("<I", idata, import_desc_start + 0, idata_vaddr + ilt_start)
    struct.pack_into("<I", idata, import_desc_start + 16, idata_vaddr + dll_name_start)
    struct.pack_into("<I", idata, import_desc_start + 20, idata_vaddr + iat_start)

    # Fix up thunk disp32 placeholders
    for text_offset, kind, orig_name in thunk_fixups:
        thunk_va = text_vaddr + text_offset
        if kind == 'log_string':
            target_rva = rdata_vaddr + log_string_offsets[orig_name]
        elif kind == 'ods_iat':
            target_rva = idata_vaddr + iat_start
        else:
            raise ValueError(f"Unknown fixup kind: {kind}")
        disp32 = target_rva - (text_vaddr + text_offset + 4)
        struct.pack_into("<i", text_data, text_offset, disp32)

    dos = bytearray(64)
    dos[0:2] = b"MZ"
    dos_stub = b"This program cannot be run in DOS mode\r\n\x00"
    dos[64:64 + len(dos_stub)] = dos_stub
    dos_end = 64 + len(dos_stub)
    while dos_end % 16 != 0:
        dos_end += 1
        dos.append(0)
    struct.pack_into("<I", dos, 0x3C, dos_end)

    pe_offset = dos_end
    coff_offset = pe_offset + 4
    opt_offset = coff_offset + 20
    sec_offset = opt_offset + 240

    text_raw = sec_offset + 4 * 40
    text_raw_aligned = text_raw
    while text_raw_aligned % 0x200 != 0:
        text_raw_aligned += 1

    rdata_raw = text_raw_aligned + ((len(text_data) + 0x1ff) & ~0x1ff)
    rdata_raw_aligned = rdata_raw
    while rdata_raw_aligned % 0x200 != 0:
        rdata_raw_aligned += 1

    edata_raw_final = rdata_raw_aligned + ((len(rdata) + 0x1ff) & ~0x1ff)
    edata_raw_aligned = edata_raw_final
    while edata_raw_aligned % 0x200 != 0:
        edata_raw_aligned += 1

    idata_raw = edata_raw_aligned + len(edata)
    while idata_raw % 0x200 != 0:
        idata_raw += 1

    file_size = idata_raw + len(idata)
    while file_size % 0x200 != 0:
        file_size += 1

    sec_text = bytearray(40)
    sec_text[0:8] = b".text\x00\x00\x00"
    text_raw_size = ((len(text_data) + 0x1ff) & ~0x1ff)
    struct.pack_into("<I", sec_text, 8, len(text_data))
    struct.pack_into("<I", sec_text, 12, text_vaddr)
    struct.pack_into("<I", sec_text, 16, text_raw_size)
    struct.pack_into("<I", sec_text, 20, text_raw_aligned)
    struct.pack_into("<I", sec_text, 36, 0x60000020)

    sec_rdata = bytearray(40)
    sec_rdata[0:8] = b".rdata\x00\x00"
    rdata_raw_size = ((len(rdata) + 0x1ff) & ~0x1ff)
    struct.pack_into("<I", sec_rdata, 8, rdata_vsize)
    struct.pack_into("<I", sec_rdata, 12, rdata_vaddr)
    struct.pack_into("<I", sec_rdata, 16, rdata_raw_size)
    struct.pack_into("<I", sec_rdata, 20, rdata_raw_aligned)
    struct.pack_into("<I", sec_rdata, 36, 0x40000040)

    sec_edata = bytearray(40)
    sec_edata[0:8] = b".edata\x00\x00"
    edata_raw_size_sec = ((len(edata) + 0x1ff) & ~0x1ff)
    struct.pack_into("<I", sec_edata, 8, edata_vsize)
    struct.pack_into("<I", sec_edata, 12, edata_vaddr)
    struct.pack_into("<I", sec_edata, 16, edata_raw_size_sec)
    struct.pack_into("<I", sec_edata, 20, edata_raw_aligned)
    struct.pack_into("<I", sec_edata, 36, 0x40000040)

    sec_idata = bytearray(40)
    sec_idata[0:8] = b".idata\x00\x00"
    struct.pack_into("<I", sec_idata, 8, idata_vsize)
    struct.pack_into("<I", sec_idata, 12, idata_vaddr)
    struct.pack_into("<I", sec_idata, 16, idata_vsize)
    struct.pack_into("<I", sec_idata, 20, idata_raw)
    struct.pack_into("<I", sec_idata, 36, 0x40000040)

    struct.pack_into("<I", dos, 0x3C, dos_end)
    file_data = bytearray(file_size)
    file_data[0:len(dos)] = dos
    file_data[pe_offset:pe_offset + 4] = b"PE\x00\x00"

    coff = bytearray(20)
    struct.pack_into("<H", coff, 0, 0x8664)
    struct.pack_into("<H", coff, 2, 4)
    struct.pack_into("<I", coff, 4, 0)
    struct.pack_into("<I", coff, 8, 0)
    struct.pack_into("<I", coff, 12, 0)
    struct.pack_into("<H", coff, 16, 240)
    struct.pack_into("<H", coff, 18, 0x2002 | 0x2000)
    file_data[coff_offset:coff_offset + 20] = coff

    opt_header = bytearray(240)
    struct.pack_into("<H", opt_header, 0, 0x20B)
    struct.pack_into("<B", opt_header, 2, 14)
    struct.pack_into("<I", opt_header, 4, len(text_data))
    struct.pack_into("<I", opt_header, 8, len(rdata))
    struct.pack_into("<I", opt_header, 12, 0)
    struct.pack_into("<I", opt_header, 16, 0)
    struct.pack_into("<I", opt_header, 20, 0x1000)
    struct.pack_into("<Q", opt_header, 24, image_base)
    struct.pack_into("<I", opt_header, 32, 0x1000)
    struct.pack_into("<I", opt_header, 36, 0x200)
    struct.pack_into("<H", opt_header, 40, 0)
    struct.pack_into("<H", opt_header, 42, 0)
    struct.pack_into("<H", opt_header, 44, 0)
    struct.pack_into("<H", opt_header, 46, 0)
    struct.pack_into("<H", opt_header, 48, 4)
    struct.pack_into("<H", opt_header, 50, 0)
    struct.pack_into("<I", opt_header, 52, 0)
    struct.pack_into("<I", opt_header, 56, 0x4000)
    struct.pack_into("<I", opt_header, 60, 0x400)
    struct.pack_into("<H", opt_header, 64, 2)
    struct.pack_into("<H", opt_header, 66, 0x2000)
    struct.pack_into("<I", opt_header, 68, 16)
    size_of_headers = sec_offset + 4 * 40
    struct.pack_into("<I", opt_header, 60, size_of_headers)
    size_of_image = ((idata_vaddr + idata_vsize + 0xfff) & ~0xfff)
    struct.pack_into("<I", opt_header, 56, size_of_image)
    dd_start = 112
    struct.pack_into("<I", opt_header, dd_start + 0, edata_vaddr)
    struct.pack_into("<I", opt_header, dd_start + 4, len(edata))
    struct.pack_into("<I", opt_header, dd_start + 8, idata_vaddr)
    struct.pack_into("<I", opt_header, dd_start + 12, idata_vsize)
    file_data[opt_offset:opt_offset + 240] = opt_header

    file_data[sec_offset:sec_offset + 40] = sec_text
    file_data[sec_offset + 40:sec_offset + 80] = sec_rdata
    file_data[sec_offset + 80:sec_offset + 120] = sec_edata
    file_data[sec_offset + 120:sec_offset + 160] = sec_idata

    file_data[text_raw_aligned:text_raw_aligned + len(text_data)] = text_data
    file_data[rdata_raw_aligned:rdata_raw_aligned + len(rdata)] = rdata
    file_data[edata_raw_aligned:edata_raw_aligned + len(edata)] = edata
    file_data[idata_raw:idata_raw + len(idata)] = idata

    with open(output_path, "wb") as f:
        f.write(file_data)


def find_unresolved_imports(export_dir, libs_dir):
    app_exe = os.path.join(export_dir, "app.exe")
    if not os.path.isfile(app_exe):
        return {}

    all_exports = set()
    for prx_file in Path(libs_dir).glob("*.prx"):
        all_exports |= prx_export_names(str(prx_file))

    tool_dir = os.path.dirname(os.path.abspath(__file__))
    missing_txt = os.path.join(tool_dir, "missing.txt")
    missing_names = []
    if os.path.isfile(missing_txt):
        with open(missing_txt, "r", encoding="ascii", errors="replace") as f:
            missing_names = [line.strip() for line in f if line.strip()]

    import re
    with open(app_exe, "rb") as f:
        data = f.read()
    candidate_names = set()
    for match in re.finditer(rb"[\x21-\x7e]{6,32}\x00", data):
        raw = match.group(0)[:-1]
        try:
            name = raw.decode("ascii")
        except UnicodeDecodeError:
            continue
        if " " in name or "%" in name or name.startswith("##") or name.startswith("#"):
            continue
        has_digit = any(c.isdigit() for c in name)
        has_letter = any(c.isalpha() for c in name)
        if not (has_digit and has_letter):
            continue
        has_symbol = any(c in "+-_.=/" for c in name)
        is_mixed_case = any(c.isupper() for c in name) and any(c.islower() for c in name)
        if not (has_symbol or is_mixed_case):
            continue
        candidate_names.add(name)
    for name in candidate_names:
        if name not in missing_names:
            missing_names.append(name)

    missing = sorted(n for n in missing_names if n not in all_exports)

    if not missing:
        return {}

    return {"unresolved_imports.prx": missing}


def create_missing_prx_stubs(export_dir, log_cb=print, nid_db_path=None):
    libs_dir = os.path.join(export_dir, "libs")
    if not os.path.isdir(libs_dir):
        log_cb("  SKIP Phase 2: export/libs/ not found")
        return

    nid_db = None
    if nid_db_path:
        try:
            nid_db = NidDatabase()
            count = nid_db.load(nid_db_path)
            log_cb(f"  NID database loaded: {count} entries from {nid_db_path}")
        except Exception as exc:
            log_cb(f"  WARN: could not load NID database {nid_db_path}: {exc}")
            nid_db = None

    unresolved = find_unresolved_imports(export_dir, libs_dir)
    if not unresolved:
        log_cb("  Phase 2: all imports resolved, no stubs needed")
        return

    log_cb(f"  Phase 2: found {len(unresolved)} library(ies) with unresolved imports")

    created = 0
    for dll_name, missing_names in sorted(unresolved.items()):
        stub_name = dll_name if dll_name.endswith(".prx") else dll_name + ".prx"
        stub_path = os.path.join(libs_dir, stub_name)

        if os.path.exists(stub_path):
            log_cb(f"  SKIP (stub exists): {stub_name}")
            continue

        log_cb(f"  Creating NotImplemented stub: {stub_name} ({len(missing_names)} export(s))")
        try:
            build_notimplemented_stub_dll(dll_name, missing_names, stub_path, nid_db=nid_db)
            created += 1
        except Exception as exc:
            log_cb(f"  WARN: failed to create stub {stub_name}: {exc}")

    log_cb(f"  Phase 2 complete: {created} stub(s) created")
