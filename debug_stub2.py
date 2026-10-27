import struct

with open(r'C:\Users\Info-Tech\Downloads\Games\ps4\export\export__SuperPSX_-Mega.Shoot-CUSA59042-EUR-Game-PS4-Opoisso893\libs\unresolved_imports.prx', 'rb') as f:
    data = f.read()

pe_off = struct.unpack_from('<I', data, 0x3C)[0]
print('PE offset:', pe_off)
print('PE sig:', data[pe_off:pe_off+4])

opt_off = pe_off + 24
size_opt_header = struct.unpack_from('<H', data, pe_off + 20)[0]
magic = struct.unpack_from('<H', data, opt_off)[0]
num_sections = struct.unpack_from('<H', data, pe_off + 6)[0]
print('Magic: 0x%04x' % magic)
print('SizeOfOptionalHeader:', size_opt_header)
print('NumberOfSections (COFF):', num_sections)

coff_characteristics = struct.unpack_from('<H', data, pe_off + 18)[0]
print('COFF Characteristics: 0x%04x' % coff_characteristics)

num_sections_opt = struct.unpack_from('<H', data, opt_off + 68)[0]
print('NumberOfSections (Opt):', num_sections_opt)
size_of_image = struct.unpack_from('<I', data, opt_off + 56)[0]
size_of_headers = struct.unpack_from('<I', data, opt_off + 60)[0]
subsystem = struct.unpack_from('<H', data, opt_off + 64)[0]
dll_characteristics = struct.unpack_from('<H', data, opt_off + 66)[0]
print('SizeOfImage: 0x%08x' % size_of_image)
print('SizeOfHeaders: 0x%08x' % size_of_headers)
print('Subsystem:', subsystem)
print('DllCharacteristics: 0x%04x' % dll_characteristics)

sec_off = opt_off + size_opt_header
print()
print('Section headers:')
for i in range(num_sections):
    base = sec_off + i * 40
    name = data[base:base+8].rstrip(b'\x00').decode('ascii', 'replace')
    vsize, vaddr, rsize, raddr = struct.unpack_from('<IIII', data, base + 8)
    flags = struct.unpack_from('<I', data, base + 36)[0]
    print('  %-12s vaddr=0x%08x vsize=0x%08x raddr=0x%08x rsize=0x%08x flags=0x%08x' % (name, vaddr, vsize, raddr, rsize, flags))

dd_start = opt_off + 108
exp_rva, exp_size = struct.unpack_from('<II', data, dd_start)
print()
print('Export dir: RVA=0x%08x, Size=0x%08x' % (exp_rva, exp_size))

reloc_rva, reloc_size = struct.unpack_from('<II', data, dd_start + 5*8)
print('Reloc dir: RVA=0x%08x, Size=0x%08x' % (reloc_rva, reloc_size))

def rva_to_offset(rva):
    for i in range(num_sections):
        base = sec_off + i * 40
        vsize, vaddr, rsize, raddr = struct.unpack_from('<IIII', data, base + 8)
        if vaddr <= rva < vaddr + max(vsize, rsize):
            return raddr + (rva - vaddr)
    return None

exp_off = rva_to_offset(exp_rva)
if exp_off:
    fields = struct.unpack_from('<IIHHIIIIIII', data, exp_off)
    print('Export dir at offset 0x%08x:' % exp_off)
    print('  Characteristics: 0x%08x' % fields[0])
    print('  TimeDateStamp: 0x%08x' % fields[1])
    print('  MajorVersion:', fields[2])
    print('  MinorVersion:', fields[3])
    print('  Name RVA: 0x%08x' % fields[4])
    print('  Base:', fields[5])
    print('  NumberOfFunctions:', fields[6])
    print('  NumberOfNames:', fields[7])
    print('  AddressOfFunctions: 0x%08x' % fields[8])
    print('  AddressOfNames: 0x%08x' % fields[9])
    print('  AddressOfNameOrdinals: 0x%08x' % fields[10])
else:
    print('Export RVA not in any section!')

print()
print('File size: %d bytes' % len(data))
print('SizeOfImage: 0x%08x bytes' % size_of_image)