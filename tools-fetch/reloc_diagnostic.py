#!/usr/bin/env python3
"""
ELF Relocation Diagnostic Tool

Analyzes PS4 ELF relocations and segment mappings to determine if relocation
targets fall inside valid PT_LOAD segments.

Usage:
    python reloc_diagnostic.py <elf_file>
"""

import struct
import sys
import argparse

ELF_MAGIC = b'\x7fELF'


class ELFSegment:
    def __init__(self, p_type, p_offset, p_vaddr, p_paddr,
                 p_filesz, p_memsz, p_flags, p_align):
        self.p_type = p_type
        self.p_offset = p_offset
        self.p_vaddr = p_vaddr
        self.p_paddr = p_paddr
        self.p_filesz = p_filesz
        self.p_memsz = p_memsz
        self.p_flags = p_flags
        self.p_align = p_align
        self.is_executable = bool(p_flags & 1)
        self.is_writable = bool(p_flags & 2)
        self.is_readable = bool(p_flags & 4)

    def contains_vaddr(self, vaddr):
        return self.p_vaddr <= vaddr < self.p_vaddr + self.p_memsz

def parse_elf_segments(elf_path):
    with open(elf_path, 'rb') as f:
        data = bytearray(f.read())

    if data[:4] != ELF_MAGIC:
        print(f"Error: {elf_path} is not an ELF file")
        return None, None

    if data[4] != 2:
        print(f"Error: Only ELF64 supported, class={data[4]}")
        return None, None

    e_phoff = struct.unpack_from('<Q', data, 0x20)[0]
    e_phentsize = struct.unpack_from('<H', data, 0x36)[0]
    e_phnum = struct.unpack_from('<H', data, 0x38)[0]
    e_entry = struct.unpack_from('<Q', data, 0x18)[0]

    print(f"ELF Entry Point: 0x{e_entry:x}")
    print(f"Program headers: offset=0x{e_phoff:x}, count={e_phnum}, size={e_phentsize}")
    print()

    segments = []
    for i in range(e_phnum):
        phoff = e_phoff + i * e_phentsize
        p_type = struct.unpack_from('<I', data, phoff)[0]
        p_flags = struct.unpack_from('<I', data, phoff + 4)[0]
        p_offset = struct.unpack_from('<Q', data, phoff + 8)[0]
        p_vaddr = struct.unpack_from('<Q', data, phoff + 16)[0]
        p_paddr = struct.unpack_from('<Q', data, phoff + 24)[0]
        p_filesz = struct.unpack_from('<Q', data, phoff + 32)[0]
        p_memsz = struct.unpack_from('<Q', data, phoff + 40)[0]
        p_align = struct.unpack_from('<Q', data, phoff + 48)[0]

        seg = ELFSegment(p_type, p_offset, p_vaddr, p_paddr,
                         p_filesz, p_memsz, p_flags, p_align)
        segments.append(seg)

        if p_type == 1:
            print(f"PT_LOAD: vaddr=0x{p_vaddr:x}, memsz=0x{p_memsz:x}, "
                  f"offset=0x{p_offset:x}, filesz=0x{p_filesz:x}, "
                  f"flags={'R' if seg.is_readable else ''}"
                  f"{'W' if seg.is_writable else ''}"
                  f"{'X' if seg.is_executable else ''}")
        elif p_type == 2:
            print(f"PT_DYNAMIC: vaddr=0x{p_vaddr:x}, memsz=0x{p_memsz:x}")

    return segments, data

def find_segment_containing(segments, vaddr):
    for seg in segments:
        if seg.p_type == 1 and seg.contains_vaddr(vaddr):
            return seg
    return None

def parse_relocations(data, segments):
    print("\n" + "=" * 70)
    print("RELOCATION DIAGNOSTIC")
    print("=" * 70)

    e_shoff = struct.unpack_from('<Q', data, 0x28)[0]
    e_shentsize = struct.unpack_from('<H', data, 0x3A)[0]
    e_shnum = struct.unpack_from('<H', data, 0x3C)[0]
    e_shstrndx = struct.unpack_from('<H', data, 0x3E)[0]

    print(f"Section headers: offset=0x{e_shoff:x}, count={e_shnum}, size={e_shentsize}")
    print(f"Section name string table index: {e_shstrndx}")

    shstrndx_off = e_shoff + e_shstrndx * e_shentsize
    shstr_offset = struct.unpack_from('<Q', data, shstrndx_off + 16)[0]

    def get_section_name(sh_name_off):
        if sh_name_off == 0:
            return ""
        end = data.find(b'\x00', shstr_offset + sh_name_off)
        if end == -1:
            return ""
        return data[shstr_offset + sh_name_off:end].decode('ascii', errors='replace')

    reloc_sections = []
    for i in range(e_shnum):
        shoff = e_shoff + i * e_shentsize
        sh_type = struct.unpack_from('<I', data, shoff)[0]
        sh_name = struct.unpack_from('<I', data, shoff)[0]
        sh_offset = struct.unpack_from('<Q', data, shoff + 16)[0]
        sh_size = struct.unpack_from('<Q', data, shoff + 40)[0]
        sh_name_str = get_section_name(sh_name)

        if sh_type in (4, 9):
            reloc_sections.append({
                'index': i,
                'name': sh_name_str,
                'type': sh_type,
                'offset': sh_offset,
                'size': sh_size,
            })
            print(f"\nSection[{i}]: {sh_name_str} (type=0x{sh_type:x}, "
                  f"offset=0x{sh_offset:x}, size=0x{sh_size:x})")

    for sec in reloc_sections:
        print(f"\n--- Relocations in {sec['name']} ---")
        count = sec['size'] // 24
        print(f"Total relocations: {count}")

        inside_count = 0
        outside_count = 0

        for j in range(min(count, 200)):
            roffset = sec['offset'] + j * 24
            r_offset = struct.unpack_from('<Q', data, roffset)[0]
            r_info = struct.unpack_from('<Q', data, roffset + 8)[0]
            r_addend = struct.unpack_from('<q', data, roffset + 16)[0]

            r_symbol = r_info >> 32
            r_type = r_info & 0xFFFFFFFF

            seg = find_segment_containing(segments, r_offset)
            inside = seg is not None

            if inside:
                inside_count += 1
                status = "INSIDE"
            else:
                outside_count += 1
                status = "OUTSIDE"

            if j < 20 or not inside:
                print(f"  [{j:4d}] offset=0x{r_offset:016x} symbol={r_symbol:4d} "
                      f"type=0x{r_type:08x} addend=0x{r_addend:016x} -> {status}"
                      + (f" (seg={seg.p_vaddr:x}+0x{seg.p_memsz:x})" if seg else ""))

        print(f"  Summary: {inside_count} inside segments, {outside_count} outside segments")

def check_addresses(segments):
    print("\n" + "=" * 70)
    print("ADDRESS DIAGNOSTIC - Specific Addresses of Interest")
    print("=" * 70)

    test_addresses = [
        0xD15851E8,
        0x5C4DEE52D,
        0x60F4C0,
        0xAF31C7,
        0xAFDDAB,
        0xAFDDAC,
        0xAFDDAD,
    ]

    for addr in test_addresses:
        seg = find_segment_containing(segments, addr)
        if seg:
            offset_in_seg = addr - seg.p_vaddr
            file_offset = seg.p_offset + offset_in_seg
            print(f"  0x{addr:016x}: INSIDE segment (vaddr=0x{seg.p_vaddr:x}, "
                  f"memsz=0x{seg.p_memsz:x}), offset_in_seg=0x{offset_in_seg:x}, "
                  f"file_offset=0x{file_offset:x}")
        else:
            print(f"  0x{addr:016x}: OUTSIDE all PT_LOAD segments")

    print("\n" + "=" * 70)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 70)

def main():
    parser = argparse.ArgumentParser(description='ELF Relocation Diagnostic Tool')
    parser.add_argument('elf_file', help='Path to PS4 ELF file')
    args = parser.parse_args()

    segments, data = parse_elf_segments(args.elf_file)
    if segments is None:
        sys.exit(1)

    print("\n" + "=" * 70)
    print("CRASH ADDRESS ANALYSIS")
    print("=" * 70)

    crash_addrs = [
        0xD15851E8,
        0x5C4DEE52D,
        0x60F4C0,
        0xAF31C7,
        0xAFDDAB,
        0xAFDDAC,
        0xAFDDAD,
    ]

    for addr in crash_addrs:
        seg = find_segment_containing(segments, addr)
        if seg:
            offset_in_seg = addr - seg.p_vaddr
            print(f"  0x{addr:016x}: INSIDE segment at offset 0x{offset_in_seg:x}"
                  f" (seg vaddr=0x{seg.p_vaddr:x})")
        else:
            print(f"  0x{addr:016x}: OUTSIDE all PT_LOAD segments")

    parse_relocations(data, segments)
    check_addresses(segments)


if __name__ == '__main__':
    main()