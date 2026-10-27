"""Diagnostic: dump eboot.elf NID imports and compare against PRX stub exports.

Usage:
    python check_nids.py                # check stub exports against sample NIDs
    python elf_imports.py <eboot.elf>   # full import comparison for a game ELF
"""
import hashlib
import base64
import glob
import struct
import subprocess
import re
import os
import sys

SUFFIX = bytes([
    0x51, 0x8D, 0x64, 0xA6, 0x35, 0xDE, 0xD8, 0xC1,
    0xE6, 0xB0, 0x39, 0xB1, 0xC3, 0xE5, 0x52, 0x30,
])
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-"
STD_B64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
STUB_DIR = r"c:\PersonalProjects\AnyPs4\AnyPS4\build-full\core\libs\libs"
OBJDUMP = r"c:\PersonalProjects\AnyPs4\mingw15\mingw64\bin\objdump.exe"


def nid(name: str) -> str:
    digest = hashlib.sha1(name.encode() + SUFFIX).digest()
    reversed_ = digest[7::-1]
    full = base64.b64encode(reversed_).decode()
    return "".join(ALPHABET[STD_B64.index(c)] for c in full[:11])


def collect_exports_by_lib(stub_dir: str) -> dict:
    result = {}
    for prx in glob.glob(os.path.join(stub_dir, "*.prx")):
        out = subprocess.run(
            [OBJDUMP, "-p", prx],
            capture_output=True, text=True, errors="replace",
        ).stdout
        names = set()
        # Format: "[  55] +base[  56]  0000 1nTKA7pN1jw"
        for m in re.finditer(r"\[\s*\d+\]\s*\+base\[\s*\d+\]\s+\d+\s+(\S+)", out):
            names.add(m.group(1))
        result[os.path.basename(prx)] = names
    return result


def collect_exports(stub_dir: str) -> set:
    all_exports = set()
    for names in collect_exports_by_lib(stub_dir).values():
        all_exports |= names
    return all_exports



def elf_dynamic_imports(elf_path: str) -> list:
    """Return import symbol names (undefined syms) from a PS4 ELF64 eboot."""
    with open(elf_path, "rb") as f:
        data = f.read()
    if data[:4] != b"\x7fELF":
        raise ValueError("not an ELF file")
    # Elf64_Ehdr
    e_phoff = struct.unpack_from("<Q", data, 0x20)[0]
    e_shoff = struct.unpack_from("<Q", data, 0x28)[0]
    e_phentsize = struct.unpack_from("<H", data, 0x36)[0]
    e_phnum = struct.unpack_from("<H", data, 0x38)[0]
    e_shentsize = struct.unpack_from("<H", data, 0x3A)[0]
    e_shnum = struct.unpack_from("<H", data, 0x3C)[0]
    e_shstrndx = struct.unpack_from("<H", data, 0x3E)[0]

    def vaddr_to_off(vaddr):
        for i in range(e_phnum):
            off = e_phoff + i * e_phentsize
            p_type = struct.unpack_from("<I", data, off)[0]
            if p_type != 1:  # PT_LOAD
                continue
            p_offset, p_vaddr = struct.unpack_from("<QQ", data, off + 8)
            p_filesz = struct.unpack_from("<Q", data, off + 32)[0]
            if p_vaddr <= vaddr < p_vaddr + p_filesz:
                return p_offset + (vaddr - p_vaddr)
        return None

    # parse sections to locate .dynsym / .dynstr (PS4 uses section-less binaries
    # too, so fall back to DT_SYMTAB/DT_STRTAB from PT_DYNAMIC)
    dynsym_off = dynstr_off = None
    dynsym_size = None

    if e_shoff and e_shnum:
        shstr_off = struct.unpack_from("<Q", data, e_shoff + e_shstrndx * e_shentsize + 24)[0]
        for i in range(e_shnum):
            off = e_shoff + i * e_shentsize
            sh_name = struct.unpack_from("<I", data, off)[0]
            sh_offset = struct.unpack_from("<Q", data, off + 24)[0]
            sh_size = struct.unpack_from("<Q", data, off + 32)[0]
            end = data.index(b"\0", shstr_off + sh_name)
            name = data[shstr_off + sh_name:end].decode()
            if name == ".dynsym":
                dynsym_off = sh_offset
                dynsym_size = sh_size
            elif name == ".dynstr":
                dynstr_off = sh_offset

    if dynsym_off is None or dynstr_off is None:
        # PT_DYNAMIC fallback (PS4 uses DT_OS_* custom tags)
        DT_SYMTAB, DT_STRTAB = 6, 5
        DT_OS_SYMTAB, DT_OS_STRTAB = 0x61000039, 0x61000035
        DT_OS_SYMTABSZ = 0x6100003F
        for i in range(e_phnum):
            off = e_phoff + i * e_phentsize
            p_type = struct.unpack_from("<I", data, off)[0]
            if p_type != 2:  # PT_DYNAMIC
                continue
            p_offset = struct.unpack_from("<Q", data, off + 8)[0]
            p_filesz = struct.unpack_from("<Q", data, off + 32)[0]
            symtab = strtab = symsz = None
            for j in range(0, p_filesz, 16):
                tag, val = struct.unpack_from("<QQ", data, p_offset + j)
                if tag in (DT_SYMTAB, DT_OS_SYMTAB):
                    symtab = val
                elif tag in (DT_STRTAB, DT_OS_STRTAB):
                    strtab = val
                elif tag == DT_OS_SYMTABSZ:
                    symsz = val
            if symtab and strtab:
                dynsym_off = vaddr_to_off(symtab)
                dynstr_off = vaddr_to_off(strtab)
                if dynsym_off is None or dynstr_off is None:
                    raise RuntimeError("cannot translate dynamic table vaddrs")
                dynsym_size = symsz
                break

    if dynsym_off is None or dynstr_off is None:
        raise RuntimeError("cannot locate dynamic symbol/string tables")

    imports = []
    # string table size for bounds checks
    strsz = None
    if e_shoff and e_shnum:
        # .dynstr size is known from the section header
        for i in range(e_shnum):
            off = e_shoff + i * e_shentsize
            sh_name = struct.unpack_from("<I", data, off)[0]
            sh_size = struct.unpack_from("<Q", data, off + 32)[0]
            if shstr_off is not None:
                end = data.index(b"\0", shstr_off + sh_name)
                if data[shstr_off + sh_name:end] == b".dynstr":
                    strsz = sh_size
                    break
    count = (dynsym_size // 24) if dynsym_size else 16384
    for i in range(count):
        off = dynsym_off + i * 24
        if off + 24 > len(data):
            break
        st_name = struct.unpack_from("<I", data, off)[0]
        st_shndx = struct.unpack_from("<H", data, off + 6)[0]
        if st_name == 0 or st_shndx != 0:
            continue
        name_off = dynstr_off + st_name
        if strsz is not None and st_name >= strsz:
            continue
        if name_off >= len(data):
            break
        try:
            end = data.index(b"\0", name_off)
        except ValueError:
            break
        name = data[name_off:end].decode("utf-8", "replace")
        if name:
            imports.append(name)
    return imports


def compare_with_elf(elf_path: str, stub_dir: str = STUB_DIR):
    by_lib = collect_exports_by_lib(stub_dir)
    all_exports = set()
    for names in by_lib.values():
        all_exports |= names
    print(f"stub exports: {len(all_exports)} across {len(by_lib)} libraries")

    imports = elf_dynamic_imports(elf_path)
    seen = set()
    unique = [n for n in imports if not (n in seen or seen.add(n))]
    nid_re = re.compile(r"^[A-Za-z0-9+\-]{11}$")
    nids = [n for n in unique if nid_re.match(n)]
    other = [n for n in unique if not nid_re.match(n)]
    missing = [n for n in nids if n not in all_exports]
    print(f"unique imports: {len(unique)} (NID-shaped: {len(nids)}, other: {len(other)})")
    print(f"NIDs found in stubs: {len(nids) - len(missing)}")
    print(f"NIDs MISSING from stubs: {len(missing)}")
    if missing:
        print("\nfirst 60 missing NIDs:")
        for n in missing[:60]:
            print("  " + n)
    if other:
        print(f"\nnon-NID imports ({len(other)}), first 60:")
        for n in other[:60]:
            print("  " + n)
    # which libraries provide the found ones
    found = [n for n in nids if n in all_exports]
    if found:
        cover = {}
        for n in found[:500]:
            for lib, names in by_lib.items():
                if n in names:
                    cover[lib] = cover.get(lib, 0) + 1
                    break
        print("\ncoverage by library (top):")
        for lib, c in sorted(cover.items(), key=lambda kv: -kv[1])[:15]:
            print(f"  {lib}: {c}")


def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "--elf":
        compare_with_elf(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else STUB_DIR)
        return
    stub_dir = sys.argv[1] if len(sys.argv) > 1 else STUB_DIR
    exports = collect_exports(stub_dir)
    print(f"Total stub exports: {len(exports)}")

    failing = [
        "St4apgcBNfo", "0z45PIH+SNI", "rFZLbF+Z4o0", "9F4Z+J51gKU",
        "s6KzX7ZQZ8M", "g6Zo9bE4n6I", "Y2bM3lKgq5I", "zr094EQ39Ww",
    ]
    for f in failing:
        status = "IN STUBS" if f in exports else "MISSING"
        print(f"{f}: {status}")

    print()
    common = [
        "scePadRead", "sceVideoOutOpen", "sceKernelWrite", "malloc", "free",
        "memcpy", "memset", "sceKernelGettimeofday", "sceKernelUsleep",
        "snprintf", "sceSystemServiceParamGet", "sceUserServiceGetInitialUser",
        "sceSysmoduleLoadModule", "abort", "exit",
        "sceKernelCreateThread", "sceKernelStartThread",
    ]
    for name in common:
        value = nid(name)
        status = "IN STUBS" if value in exports else "MISSING"
        print(f"{name} -> {value}: {status}")


if __name__ == "__main__":
    main()
