#!/usr/bin/env python3
"""NOP out instructions at a specific RVA in a PE file."""
import struct
import sys

def rva_to_file_offset(data, rva):
    """Convert an RVA to a file offset by parsing PE section headers."""
    pe_off = struct.unpack_from('<I', data, 0x3C)[0]
    num_sections = struct.unpack_from('<H', data, pe_off + 6)[0]
    opt_size = struct.unpack_from('<H', data, pe_off + 20)[0]
    
    # Section headers start after COFF header + Optional header
    sec_off = pe_off + 24 + opt_size
    
    for i in range(num_sections):
        sec_base = sec_off + i * 40
        virt_addr = struct.unpack_from('<I', data, sec_base + 12)[0]
        virt_size = struct.unpack_from('<I', data, sec_base + 8)[0]
        raw_addr = struct.unpack_from('<I', data, sec_base + 20)[0]
        raw_size = struct.unpack_from('<I', data, sec_base + 16)[0]
        
        if virt_addr <= rva < virt_addr + virt_size:
            file_off = raw_addr + (rva - virt_addr)
            return file_off
    
    return None

def nop_instructions(pe_path, rva, num_bytes):
    """NOP out num_bytes at the given RVA in the PE file."""
    with open(pe_path, 'rb') as f:
        data = bytearray(f.read())
    
    file_off = rva_to_file_offset(data, rva)
    if file_off is None:
        print(f'Error: RVA 0x{rva:x} not found in any section')
        return False
    
    print(f'RVA 0x{rva:x} -> file offset 0x{file_off:x}')
    print(f'Original bytes: {data[file_off:file_off+num_bytes].hex()}')
    
    # NOP out the bytes
    for i in range(num_bytes):
        data[file_off + i] = 0x90
    
    print(f'Patched bytes: {data[file_off:file_off+num_bytes].hex()}')
    
    with open(pe_path, 'wb') as f:
        f.write(data)
    
    print(f'Patched {num_bytes} bytes at RVA 0x{rva:x} in {pe_path}')
    return True

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python nop_crash.py <pe_file> <rva_hex> [num_bytes]')
        sys.exit(1)
    
    pe_path = sys.argv[1]
    rva = int(sys.argv[2], 16)
    num_bytes = int(sys.argv[3]) if len(sys.argv) > 3 else 7
    
    nop_instructions(pe_path, rva, num_bytes)