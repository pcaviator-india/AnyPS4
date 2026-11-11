import struct

path = r'C:\PS4\export_Limbo.PS4-PRELUDE\app.exe'
with open(path, 'rb') as f:
    data = bytearray(f.read())

pe_off = struct.unpack_from('<I', data, 0x3C)[0]
num_sections = struct.unpack_from('<H', data, pe_off + 6)[0]
opt_size = struct.unpack_from('<H', data, pe_off + 20)[0]
sec_off = pe_off + 24 + opt_size

# Find .entry section
for i in range(num_sections):
    sec_base = sec_off + i * 40
    name = data[sec_base:sec_base+8].rstrip(b'\x00').decode('ascii', errors='replace')
    if name == '.entry':
        old_vsize = struct.unpack_from('<I', data, sec_base + 8)[0]
        virt_addr = struct.unpack_from('<I', data, sec_base + 12)[0]
        print(f'.entry: old virt_size = 0x{old_vsize:x}')
        print(f'.entry: virt_addr = 0x{virt_addr:x}')
        # Increase virt_size to cover more code
        new_vsize = 0x33000  # Cover up to 0xafde00
        struct.pack_into('<I', data, sec_base + 8, new_vsize)
        new_end = virt_addr + new_vsize
        print(f'.entry: new virt_size = 0x{new_vsize:x}')
        print(f'.entry: will cover VA 0x{virt_addr:x} - 0x{new_end:x}')
        break

with open(path, 'wb') as f:
    f.write(data)
print('Done!')