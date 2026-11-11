#!/usr/bin/env python3
"""Automatically NOP out crash instructions in app.exe until the game progresses."""
import struct
import subprocess
import sys
import re

APP_EXE = r'C:\PS4\export_Limbo.PS4-PRELUDE\app.exe'
APP_DIR = r'C:\PS4\export_Limbo.PS4-PRELUDE'

def rva_to_file_offset(data, rva):
    """Convert an RVA to a file offset by parsing PE section headers."""
    pe_off = struct.unpack_from('<I', data, 0x3C)[0]
    num_sections = struct.unpack_from('<H', data, pe_off + 6)[0]
    opt_size = struct.unpack_from('<H', data, pe_off + 20)[0]
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

def nop_instructions(pe_path, rvas_to_nop):
    """NOP out instructions at the given RVAs in the PE file."""
    with open(pe_path, 'rb') as f:
        data = bytearray(f.read())
    
    total_nopped = 0
    for rva in rvas_to_nop:
        file_off = rva_to_file_offset(data, rva)
        if file_off is None:
            print(f'  WARNING: RVA 0x{rva:x} not found in any section, skipping')
            continue
        
        # Read original bytes (up to 10 bytes to understand instruction)
        orig = data[file_off:file_off+10]
        
        # NOP out 7 bytes (typical instruction size)
        for i in range(7):
            if file_off + i < len(data):
                data[file_off + i] = 0x90
        
        print(f'  NOPped RVA 0x{rva:x} (file offset 0x{file_off:x}): {orig.hex()} -> 90909090909090')
        total_nopped += 1
    
    with open(pe_path, 'wb') as f:
        f.write(data)
    
    return total_nopped

def extract_crash_addresses(output):
    """Extract crash instruction addresses from trace output."""
    addresses = []
    for line in output.split('\n'):
        # Match patterns like: at 0x0000000140afddc1
        matches = re.findall(r'at 0x([0-9a-fA-F]+)', line)
        for m in matches:
            addr = int(m, 16)
            # Only include addresses in the app.exe range (0x140000000 - 0x141000000)
            if 0x140000000 <= addr < 0x141000000:
                rva = addr - 0x140000000
                addresses.append(rva)
    return list(set(addresses))

def main():
    max_iterations = 20
    
    for iteration in range(max_iterations):
        print(f'\n=== Iteration {iteration + 1}/{max_iterations} ===')
        
        # Run the game and capture output
        result = subprocess.run(
            ['python3', 'trace_app.py', APP_EXE, APP_DIR],
            capture_output=True, text=True, timeout=30
        )
        output = result.stdout + result.stderr
        
        # Check if the game progressed (look for signs of life beyond entry point)
        if 'FATAL' not in output and 'ExitProcess' not in output[-200:]:
            print('Game may have progressed! Output:')
            print(output[-500:])
            break
        
        # Extract crash addresses
        crash_rvas = extract_crash_addresses(output)
        
        if not crash_rvas:
            print('No crash addresses found in output')
            print(output[-500:])
            break
        
        print(f'Found {len(crash_rvas)} crash RVAs: {[hex(r) for r in crash_rvas]}')
        
        # NOP them out
        nop_count = nop_instructions(APP_EXE, crash_rvas)
        print(f'NOPped {nop_count} instructions')
    
    print('\nDone!')

if __name__ == '__main__':
    main()