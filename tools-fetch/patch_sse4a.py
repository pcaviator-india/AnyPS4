#!/usr/bin/env python3
"""
Scan an ELF binary for SSE4A instructions (EXTRQ/INSERTQ) and replace them with NOPs.
SSE4A is not supported on Intel CPUs, causing ILLEGAL_INSTRUCTION exceptions.

SSE4A encodings (AMD64 Architecture Programmer's Manual):
  EXTRQ   xmm1, imm8, imm8        66 [REX] 0F 78 /0 ib ib
  INSERTQ xmm1, xmm2, imm8, imm8  F2 [REX] 0F 78 /r ib ib
  Register forms:                 66/F2 [REX] 0F 79 /r
"""

import struct
import sys

def find_sse4a_instructions(data, start_offset=0):
    """Find all SSE4A instruction offsets in binary data."""
    offsets = []
    i = start_offset
    while i < len(data) - 7:
        # Check for 66 0F 78 or F2 0F 78 (EXTRQ/INSERTQ immediate form)
        if data[i] == 0x66 and data[i+1] == 0x0F and data[i+2] == 0x78:
            offsets.append(i)
            i += 1
            continue
        if data[i] == 0xF2 and data[i+1] == 0x0F and data[i+2] == 0x78:
            offsets.append(i)
            i += 1
            continue
        i += 1
    return offsets

def patch_elf(elf_path, output_path=None):
    """Patch SSE4A instructions in an ELF file."""
    if output_path is None:
        output_path = elf_path
    
    with open(elf_path, 'rb') as f:
        data = bytearray(f.read())
    
    # ELF header
    if data[:4] != b'\x7fELF':
        print(f'Error: {elf_path} is not an ELF file')
        return False
    
    e_phoff = struct.unpack_from('<Q', data, 0x20)[0]
    e_phentsize = struct.unpack_from('<H', data, 0x36)[0]
    e_phnum = struct.unpack_from('<H', data, 0x38)[0]
    
    total_patched = 0
    
    for i in range(e_phnum):
        phoff = e_phoff + i * e_phentsize
        p_type = struct.unpack_from('<I', data, phoff)[0]
        p_flags = struct.unpack_from('<I', data, phoff + 4)[0]
        p_offset = struct.unpack_from('<Q', data, phoff + 8)[0]
        p_vaddr = struct.unpack_from('<Q', data, phoff + 16)[0]
        p_filesz = struct.unpack_from('<Q', data, phoff + 32)[0]
        p_memsz = struct.unpack_from('<Q', data, phoff + 40)[0]
        
        # Only process executable segments (PT_LOAD with execute flag)
        if p_type != 1:  # PT_LOAD
            continue
        if not (p_flags & 1):  # PF_X
            continue
        
        print(f'Scanning segment {i}: vaddr=0x{p_vaddr:x}, offset=0x{p_offset:x}, size=0x{p_filesz:x}')
        
        segment_data = data[p_offset:p_offset + p_filesz]
        offsets = find_sse4a_instructions(segment_data)
        
        for offset in offsets:
            abs_offset = p_offset + offset
            # Replace with NOPs (0x90)
            # SSE4A instructions are 4-7 bytes, replace with NOPs
            instr_len = 7  # Maximum size, pad with NOPs
            for j in range(instr_len):
                if abs_offset + j < len(data):
                    data[abs_offset + j] = 0x90
            total_patched += 1
            print(f'  Patched SSE4A at vaddr=0x{p_vaddr + offset:x}, file_offset=0x{abs_offset:x}')
    
    if total_patched > 0:
        with open(output_path, 'wb') as f:
            f.write(data)
        print(f'\nPatched {total_patched} SSE4A instructions -> {output_path}')
        return True
    else:
        print('\nNo SSE4A instructions found')
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python patch_sse4a.py <input.elf> [output.elf]')
        sys.exit(1)
    
    elf_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    patch_elf(elf_path, output_path)