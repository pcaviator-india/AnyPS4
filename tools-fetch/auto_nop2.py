#!/usr/bin/env python3
"""Automatically NOP out crash instructions in app.exe."""
import struct
import subprocess
import sys
import re
import shutil
import os
import time

APP_EXE = r'C:\PS4\export_Limbo.PS4-PRELUDE\app.exe'
APP_EXE_BACKUP = r'C:\PS4\export_Limbo.PS4-PRELUDE\app.exe.backup'
APP_DIR = r'C:\PS4\export_Limbo.PS4-PRELUDE'
RELINKER = r'C:\PersonalProjects\AnyPs4\AnyPs4\build-full\core\relinker\relinker.exe'
ELF_FILE = r'C:\PS4\export_Limbo.elf'

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

def nop_instructions(pe_path, rvas_to_nop, num_bytes=7):
    """NOP out instructions at the given RVAs in the PE file."""
    with open(pe_path, 'rb') as f:
        data = bytearray(f.read())
    
    total_nopped = 0
    for rva in rvas_to_nop:
        file_off = rva_to_file_offset(data, rva)
        if file_off is None:
            print(f'  WARNING: RVA 0x{rva:x} not found, skipping')
            continue
        
        orig = data[file_off:file_off+num_bytes]
        for i in range(num_bytes):
            if file_off + i < len(data):
                data[file_off + i] = 0x90
        
        print(f'  NOPped RVA 0x{rva:x}: {orig.hex()} -> 90'*num_bytes)
        total_nopped += 1
    
    with open(pe_path, 'wb') as f:
        f.write(data)
    
    return total_nopped

def extract_crash_addresses(output):
    """Extract crash instruction addresses from trace output."""
    addresses = []
    for line in output.split('\n'):
        matches = re.findall(r'at 0x([0-9a-fA-F]+)', line)
        for m in matches:
            addr = int(m, 16)
            if 0x140000000 <= addr < 0x141000000:
                rva = addr - 0x140000000
                addresses.append(rva)
    return list(set(addresses))

def run_and_capture():
    """Run the game and capture output."""
    result = subprocess.run(
        ['python3', 'trace_app.py', APP_EXE, APP_DIR],
        capture_output=True, text=True, timeout=30
    )
    return result.stdout + result.stderr, result.returncode

def main():
    max_iterations = 10
    
    for iteration in range(max_iterations):
        print(f'\n=== Iteration {iteration + 1}/{max_iterations} ===')
        
        # Run the game
        output, rc = run_and_capture()
        
        # Check for progress - look for signs the game got past entry point
        if 'FATAL' not in output:
            print('Game may be running!')
            print(output[-500:])
            break
        
        # Extract crash addresses
        crash_rvas = extract_crash_addresses(output)
        
        if not crash_rvas:
            # Try to find any address pattern in output
            matches = re.findall(r'0x140([0-9a-fA-F]{5,6})', output)
            if matches:
                crash_rvas = [int(m, 16) for m in matches[:5]]
                print(f'Found crash RVAs (from output): {[hex(r) for r in crash_rvas]}')
            else:
                print('No crash addresses found')
                print(output[-300:])
                break
        
        print(f'Crash RVAs: {[hex(r) for r in crash_rvas]}')
        
        # Relink fresh to get a clean app.exe
        print('Relinking...')
        subprocess.run(
            [RELINKER, '--ps4', '--lazy-binding', '--skip-sce-module',
             '--windows', ELF_FILE, APP_EXE],
            capture_output=True, timeout=60
        )
        
        # NOP the crash addresses
        nop_count = nop_instructions(APP_EXE, crash_rvas)
        print(f'NOPped {nop_count} instructions')
    
    print('\nDone!')

if __name__ == '__main__':
    main()