#!/usr/bin/env python3
"""Phase 2: NotImplemented PRX stub generation for unresolved imports.

Scans app.exe PE imports after NID patching and creates minimal PE DLL
stubs exporting any function names not resolved by existing PRX stubs.
"""

import os
import struct
from pathlib import Path

from nid_db import NidDatabase, is_nid, resolve_nid


def pe_imports(path):
    """Return {dll_name: [imported function names]} for a PE file (no external deps)."""
    with open(path, "rb") as handle:
        data = handle.read()
    if data[:2] != b"MZ":
        return {}
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe:pe + 4] != b"PE\x00\x00":
        return {}
    num_sections = struct.unpack_from("<H", data, pe + 6)[0]
    opt_size = struct.unpack_from("<H", data, pe + 20)[0]
    opt = pe + 24
    magic = struct.unpack_from("<H", data, opt)[0]
    dd_off = opt + (112 if magic == 0x20B else 96)
    import_rva, _ = struct.unpack_from("<II", data, dd_off + 8)

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
        if offset is None:
            return ""
        end = data.find(b"\x00", offset)
        if end == -1:
            return ""
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
        if desc_off + 20 > len(data):
            break
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
                if thunk_off + thunk_size > len(data):
                    break
                if is64:
                    thunk = struct.unpack_from("<Q", data, thunk_off)[0]
                else:
                    thunk = struct.unpack_from("<I", data, thunk_off)[0]
                if thunk == 0:
                    break
                if not thunk & ordinal_flag:
                    mask = 0x7FFFFFFFFFFFFFFF if is64 else 0x7FFFFFFF
                    hint_off = rva_to_offset(thunk & mask)
                    if hint_off is not None:
                        names.append(read_cstr(hint_off + 2))
                else:
                    names.append("ordinal:%d" % (thunk & 0xFFFF))
                thunk_off += thunk_size
        result.setdefault(dll, []).extend(names)
        desc_off += 20
    return result


def prx_export_names(prx_path):
    """Return set of exported function names from a PE/DLL PRX stub."""
    with open(prx_path, "rb") as handle:
        data = handle.read()
    if data[:2] != b"MZ":
        return set()
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe:pe + 4] != b"PE\x00\x00":
        return set()
    num_sections = struct.unpack_from("<H", data, pe + 6)[0]
    opt_size = struct.unpack_from("<H", data, pe + 20)[0]
    opt = pe + 24
    magic = struct.unpack_from("<H", data, opt)[0]
    dd_off = opt + (112 if magic == 0x20B else 96)
    exp_rva, _ = struct.unpack_from("<II", data, dd_off)

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
        return set()
    exp_off = rva_to_offset(exp_rva)
    if exp_off is None or exp_off + 40 > len(data):
        return set()
    fields = struct.unpack_from("<IIHHIIIIIII", data, exp_off)
    num_names = fields[7]
    names_rva = fields[9]
    names_off = rva_to_offset(names_rva)
    if names_off is None:
        return set()
    names = set()
    for index in range(num_names):
        if names_off + index * 4 + 4 > len(data):
            break
        rva = struct.unpack_from("<I", data, names_off + index * 4)[0]
        off = rva_to_offset(rva)
        if off is None:
            continue
        end = data.find(b"\x00", off)
        if end == -1:
            continue
        names.add(data[off:end].decode("ascii", "replace"))
    return names


def build_notimplemented_stub_dll(dll_name, export_names, output_path, nid_db=None):
    """Build a minimal x64 PE DLL that exports each name in export_names.

    Instead of returning 0 (NULL) from all stubs, exports return a pointer to
    a fake vtable in .rdata. The fake vtable contains pointers to "return 0"
    thunks, so any virtual method call on a stub-returned object safely
    returns 0 instead of crashing on a NULL vtable dereference.

    If *nid_db* is provided, export names that look like PS4 NIDs are resolved
    to their human-readable names before building the stub. Stubs then export
    the real name (e.g. ``sceGnmRegisterMemory``) instead of the raw NID
    (e.g. ``+AFvOEXrKJk``). Names that cannot be resolved are kept unchanged.
    """
    # Resolve NIDs to human-readable names when a database is provided
    resolved_names = []
    resolved_map = {}  # raw_nid -> real_name
    if nid_db:
        for name in export_names:
            real = nid_db.resolve_name(name)
            resolved_names.append(real)
            if real != name:
                resolved_map[name] = real
        export_names = resolved_names
        if resolved_map:
            print(f"  NID resolution: {len(resolved_map)} of {len(resolved_names)} "
                  f"names resolved from database")
    # "return 0" thunk used for fake vtable entries
    ret_zero_thunk = b"\x48\x31\xc0\xc3"  # xor rax, rax; ret

    # "return fake_vtable_addr" thunk for each export:
    # lea rax, [rip + disp32]; ret  (position-independent, works with ASLR)
    ret_ptr_thunk = b"\x48\x8d\x05" + b"\x00" * 4 + b"\xc3"  # 7 bytes

    text_data = bytearray()
    thunk_offsets = {}
    fake_vtable_addr = None

    # Build fake vtable: array of QWORD pointers, each pointing to ret_zero_thunk
    # 32 entries = 256 bytes, covers vtable offsets 0x00 through 0x18 and beyond
    fake_vtable_entries = 32
    fake_vtable = bytearray()
    for _ in range(fake_vtable_entries):
        fake_vtable.extend(struct.pack("<Q", 0))  # placeholder, fixed up later

    # First, place the ret_zero_thunk in .text
    ret_zero_offset = len(text_data)
    text_data.extend(ret_zero_thunk)

    # Now we know ret_zero_thunk's address relative to .text start
    # But we need the final RVA, which depends on section layout
    # We'll fix up fake_vtable entries after computing addresses

    for name in export_names:
        thunk_offsets[name] = len(text_data)
        text_data.extend(ret_ptr_thunk)

    while len(text_data) % 16 != 0:
        text_data.append(0)

    rdata = bytearray()
    name_offsets = {}
    rdata.extend(dll_name.encode("ascii") + b"\x00")
    for name in sorted(export_names):
        name_offsets[name] = len(rdata)
        rdata.extend(name.encode("ascii") + b"\x00")
    while len(rdata) % 4 != 0:
        rdata.append(0)

    num_exp = len(export_names)
    sorted_names = sorted(export_names)

    # Compute non-overlapping virtual addresses
    text_vsize = len(text_data)
    text_vaddr = 0x1000
    text_vend = text_vaddr + text_vsize
    rdata_vaddr = ((text_vend + 0xfff) & ~0xfff)

    # Append fake vtable to .rdata: array of QWORD pointers to ret_zero_thunk
    fake_vtable_offset_in_rdata = len(rdata)
    for _ in range(fake_vtable_entries):
        rdata.extend(struct.pack("<Q", 0))  # placeholder, fixed up below
    rdata_vsize = len(rdata)
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

    # Fix up addresses now that all RVAs are known
    ret_zero_rva = text_vaddr + ret_zero_offset
    fake_vtable_rva = rdata_vaddr + fake_vtable_offset_in_rdata

    image_base = 0x180000000  # Must match ImageBase in optional header

    # Fix up fake vtable entries: each QWORD points to ret_zero_thunk VA
    # Use VA (not RVA) so base relocations correctly adjust when loaded at non-preferred base
    ret_zero_va = image_base + ret_zero_rva
    for i in range(fake_vtable_entries):
        struct.pack_into("<Q", rdata, fake_vtable_offset_in_rdata + i * 8, ret_zero_va)

    # Fix up export thunks: lea rax, [rip + disp32]; ret
    # disp32 = fake_vtable_rva - (thunk_VA + 7)
    for name in export_names:
        thunk_off = thunk_offsets[name]
        thunk_va = text_vaddr + thunk_off
        disp32 = fake_vtable_rva - (thunk_va + 7)
        struct.pack_into("<i", text_data, thunk_off + 3, disp32)

    dll_name_bytes = dll_name.encode("ascii") + b"\x00"
    edata_raw_size = 40 + len(dll_name_bytes) + len(eat) + len(nt) + len(ot)
    edata_vsize = (edata_raw_size + 15) & ~15
    edata_vaddr = ((rdata_vend + 0xfff) & ~0xfff)

    exp_dir = bytearray(40)
    struct.pack_into("<I", exp_dir, 0, 0)
    struct.pack_into("<I", exp_dir, 4, 0)
    struct.pack_into("<H", exp_dir, 8, 0)
    struct.pack_into("<H", exp_dir, 10, 0)
    struct.pack_into("<I", exp_dir, 12, rdata_vaddr)  # Name RVA -> .rdata
    struct.pack_into("<I", exp_dir, 16, 1)       # Base
    struct.pack_into("<I", exp_dir, 20, num_exp)  # NumberOfFunctions
    struct.pack_into("<I", exp_dir, 24, num_exp)  # NumberOfNames

    eat_rva = edata_vaddr + 40 + len(dll_name_bytes)
    nt_rva = eat_rva + len(eat)
    ot_rva = nt_rva + len(nt)

    struct.pack_into("<I", exp_dir, 28, eat_rva)   # AddressOfFunctions
    struct.pack_into("<I", exp_dir, 32, nt_rva)    # AddressOfNames
    struct.pack_into("<I", exp_dir, 36, ot_rva)    # AddressOfNameOrdinals

    edata = bytearray()
    edata.extend(exp_dir)
    edata.extend(dll_name_bytes)
    edata.extend(eat)
    edata.extend(nt)
    edata.extend(ot)
    while len(edata) % 16 != 0:
        edata.append(0)

    sec_text = bytearray(40)
    sec_text[0:8] = b".text\x00\x00\x00"
    struct.pack_into("<I", sec_text, 8, len(text_data))
    struct.pack_into("<I", sec_text, 12, text_vaddr)
    struct.pack_into("<I", sec_text, 16, len(text_data))
    struct.pack_into("<I", sec_text, 20, 0x200)
    struct.pack_into("<I", sec_text, 36, 0x60000020)

    sec_rdata = bytearray(40)
    sec_rdata[0:8] = b".rdata\x00\x00"
    struct.pack_into("<I", sec_rdata, 8, rdata_vsize)
    struct.pack_into("<I", sec_rdata, 12, rdata_vaddr)
    struct.pack_into("<I", sec_rdata, 16, rdata_vsize)
    sec_rdata_raw = 0x200 + ((text_vsize + 0x1ff) & ~0x1ff)
    struct.pack_into("<I", sec_rdata, 20, sec_rdata_raw)
    struct.pack_into("<I", sec_rdata, 36, 0x40000040)

    sec_edata = bytearray(40)
    sec_edata[0:8] = b".edata\x00\x00"
    struct.pack_into("<I", sec_edata, 8, edata_vsize)
    struct.pack_into("<I", sec_edata, 12, edata_vaddr)
    edata_raw = sec_rdata_raw + ((rdata_vsize + 0x1ff) & ~0x1ff)
    struct.pack_into("<I", sec_edata, 16, edata_vsize)
    # PointerToRawData will be set later with edata_raw_aligned (file-aligned)
    struct.pack_into("<I", sec_edata, 36, 0x40000040)

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

    num_sections = 4  # .text, .rdata, .edata, .reloc

    text_raw = sec_offset + num_sections * 40
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

    # Compute .reloc section raw offset early for file_size
    sec_reloc_raw = edata_raw_aligned + len(edata)
    while sec_reloc_raw % 0x200 != 0:
        sec_reloc_raw += 1
    # Estimate reloc block size (header + entries)
    reloc_block_est = 8 + fake_vtable_entries * 2
    while reloc_block_est % 4 != 0:
        reloc_block_est += 1

    file_size = sec_reloc_raw + reloc_block_est
    while file_size % 0x200 != 0:
        file_size += 1

    struct.pack_into("<I", sec_text, 20, text_raw_aligned)
    struct.pack_into("<I", sec_rdata, 20, rdata_raw_aligned)
    struct.pack_into("<I", sec_edata, 20, edata_raw_aligned)

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
    struct.pack_into("<H", coff, 18, 0x1000 | 0x2000 | 0x2)  # Characteristics: DLL + EXECUTABLE_IMAGE
    file_data[coff_offset:coff_offset + 20] = coff

    opt_header = bytearray(240)
    struct.pack_into("<H", opt_header, 0, 0x20B)
    struct.pack_into("<B", opt_header, 2, 14)
    struct.pack_into("<I", opt_header, 4, len(text_data))
    struct.pack_into("<I", opt_header, 8, len(rdata))
    struct.pack_into("<I", opt_header, 12, 0)
    struct.pack_into("<I", opt_header, 16, 0)  # No entry point (DllMain not needed)
    struct.pack_into("<I", opt_header, 20, 0x1000)
    struct.pack_into("<Q", opt_header, 24, 0x180000000)
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
    struct.pack_into("<H", opt_header, 64, 2)   # Subsystem: Windows GUI
    struct.pack_into("<H", opt_header, 66, 0x2000)  # DllCharacteristics: NX compat, etc.
    # SizeOfHeaders: DOS stub + PE sig + COFF + Optional + Section headers
    size_of_headers = sec_offset + num_sections * 40  # sec_offset already includes dos+pe+coff+opt, + section headers
    struct.pack_into("<I", opt_header, 60, size_of_headers)
    # SizeOfImage already updated above to include .reloc section
    # struct.pack_into("<I", opt_header, 56, size_of_image)
    struct.pack_into("<I", opt_header, 68, 16)  # NumberOfRvaAndSizes
    struct.pack_into("<Q", opt_header, 72, 0x10000)
    struct.pack_into("<Q", opt_header, 80, 0x1000)
    struct.pack_into("<Q", opt_header, 88, 0x10000)
    struct.pack_into("<Q", opt_header, 96, 0x1000)
    struct.pack_into("<I", opt_header, 104, 0)
    struct.pack_into("<I", opt_header, 108, 16)
    dd_start = 108  # Data Directory starts at offset 108 in PE32+ optional header
    struct.pack_into("<I", opt_header, dd_start + 0, edata_vaddr)
    struct.pack_into("<I", opt_header, dd_start + 4, len(edata))

    # ---- .reloc section: base relocations for fake_vtable entries ----
    reloc_entries = bytearray()
    reloc_page_rva = rdata_vaddr & ~0xFFF
    for i in range(fake_vtable_entries):
        entry_offset = fake_vtable_offset_in_rdata + i * 8
        entry_offset_in_page = entry_offset & 0xFFF
        reloc_type = 0x0A  # IMAGE_REL_BASED_DIR64
        reloc_word = (reloc_type << 12) | entry_offset_in_page
        reloc_entries.extend(struct.pack("<H", reloc_word))
    while len(reloc_entries) % 4 != 0:
        reloc_entries.append(0)

    reloc_block_size = 8 + len(reloc_entries)
    reloc_block = struct.pack("<II", reloc_page_rva, reloc_block_size)
    reloc_block += reloc_entries
    while len(reloc_block) % 4 != 0:
        reloc_block.append(0)

    reloc_vsize = len(reloc_block)
    reloc_vaddr = ((edata_vaddr + edata_vsize + 0xfff) & ~0xfff)

    sec_reloc = bytearray(40)
    sec_reloc[0:8] = b".reloc\x00\x00\x00"
    struct.pack_into("<I", sec_reloc, 8, reloc_vsize)
    struct.pack_into("<I", sec_reloc, 12, reloc_vaddr)
    struct.pack_into("<I", sec_reloc, 16, reloc_vsize)
    sec_reloc_raw = edata_raw_aligned + len(edata)
    while sec_reloc_raw % 0x200 != 0:
        sec_reloc_raw += 1
    struct.pack_into("<I", sec_reloc, 20, sec_reloc_raw)
    struct.pack_into("<I", sec_reloc, 36, 0x42000040)

    size_of_image = ((reloc_vaddr + reloc_vsize + 0xfff) & ~0xfff)
    struct.pack_into("<I", opt_header, 56, size_of_image)

    struct.pack_into("<I", opt_header, dd_start + 5 * 8, reloc_vaddr)
    struct.pack_into("<I", opt_header, dd_start + 5 * 8 + 4, reloc_vsize)

    file_data[opt_offset:opt_offset + 240] = opt_header

    file_data[sec_offset:sec_offset + 40] = sec_text
    file_data[sec_offset + 40:sec_offset + 80] = sec_rdata
    file_data[sec_offset + 80:sec_offset + 120] = sec_edata
    file_data[sec_offset + 120:sec_offset + 160] = sec_reloc

    file_data[text_raw_aligned:text_raw_aligned + len(text_data)] = text_data
    file_data[rdata_raw_aligned:rdata_raw_aligned + len(rdata)] = rdata
    file_data[edata_raw_aligned:edata_raw_aligned + len(edata)] = edata
    file_data[sec_reloc_raw:sec_reloc_raw + len(reloc_block)] = reloc_block

    with open(output_path, "wb") as f:
        f.write(file_data)


def find_unresolved_imports(export_dir, libs_dir):
    """Return {dll: [names]} for ELF imports not exported by any .prx stub.

    Reads missing.txt (unresolved import names) from the tools-fetch
    directory if present, otherwise scans app.exe raw data as a fallback.
    Results are grouped under a single synthetic DLL name."""
    app_exe = os.path.join(export_dir, "app.exe")
    if not os.path.isfile(app_exe):
        return {}

    # Collect all exported names from existing PRX stubs
    all_exports = set()
    for prx_file in Path(libs_dir).glob("*.prx"):
        all_exports |= prx_export_names(str(prx_file))

    # Try missing.txt first (authoritative list of unresolved imports)
    tool_dir = os.path.dirname(os.path.abspath(__file__))
    missing_txt = os.path.join(tool_dir, "missing.txt")
    missing_names = []
    if os.path.isfile(missing_txt):
        with open(missing_txt, "r", encoding="ascii", errors="replace") as f:
            missing_names = [line.strip() for line in f if line.strip()]
    # Always supplement with app.exe scan to catch imports missing.txt may have missed
    app_exe = os.path.join(export_dir, "app.exe")
    if os.path.isfile(app_exe):
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
        # Add names from app.exe scan that aren't already in missing_names
        for name in candidate_names:
            if name not in missing_names:
                missing_names.append(name)

    # Find names not exported by any stub
    missing = sorted(n for n in missing_names if n not in all_exports)

    if not missing:
        return {}

    # Group all under a single synthetic DLL name
    return {"unresolved_imports.prx": missing}


def create_missing_prx_stubs(export_dir, log_cb=print, nid_db_path=None):
    """Phase 2: Create NotImplemented stub DLLs for unresolved imports.

    If *nid_db_path* is provided, load a NID database (CSV or JSON) and
    resolve NID names to human-readable names before building stubs.
    """
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