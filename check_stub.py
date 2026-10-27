import struct

prx_path = r'C:\Users\Info-Tech\Downloads\Games\ps4\export\export__SuperPSX_-Mega.Shoot-CUSA59042-EUR-Game-PS4-Opoisso893\libs\unresolved_imports.prx'

with open(prx_path, 'rb') as f:
    data = f.read()

pe_off = struct.unpack_from('<I', data, 0x3C)[0]
opt_off = pe_off + 24
size_opt_header = struct.unpack_from('<H', data, pe_off + 20)[0]
num_sections = struct.unpack_from('<H', data, pe_off + 6)[0]
sec_off = opt_off + size_opt_header

print("Section headers:")
for i in range(num_sections):
    base = sec_off + i * 40
    name = data[base:base+8].rstrip(b'\x00').decode('ascii', 'replace')
    vsize, vaddr, rsize, raddr = struct.unpack_from('<IIII', data, base + 8)
    print(f"  {name}: vaddr=0x{vaddr:04x} vsize=0x{vsize:04x} raddr=0x{raddr:04x} rsize=0x{rsize:04x}")

def rva_to_offset(rva):
    for i in range(num_sections):
        base = sec_off + i * 40
        vsize, vaddr, rsize, raddr = struct.unpack_from('<IIII', data, base + 8)
        if vaddr <= rva < vaddr + max(vsize, rsize):
            return raddr + (rva - vaddr)
    return None

# Data Directory[0] = Export (offset 108 in PE32+ opt header)
dd_start = opt_off + 108
exp_rva, exp_size = struct.unpack_from('<II', data, dd_start)
print(f"\nExport directory: RVA=0x{exp_rva:08x} Size=0x{exp_size:08x}")

exp_off = rva_to_offset(exp_rva)
if exp_off:
    fields = struct.unpack_from('<IIHHIIIIIII', data, exp_off)
    print(f"  Characteristics: 0x{fields[0]:08x}")
    print(f"  Name RVA: 0x{fields[4]:08x}")
    print(f"  Base: {fields[5]}")
    print(f"  NumberOfFunctions: {fields[6]}")
    print(f"  NumberOfNames: {fields[7]}")
    print(f"  AddressOfFunctions: 0x{fields[8]:08x}")
    print(f"  AddressOfNames: 0x{fields[9]:08x}")
    print(f"  AddressOfNameOrdinals: 0x{fields[10]:08x}")
    
    # Check the DLL name
    name_off = rva_to_offset(fields[4])
    if name_off:
        end = data.find(b'\x00', name_off)
        print(f"  DLL Name: {data[name_off:end].decode('ascii')}")
    
    # Check AddressOfNames
    aon_off = rva_to_offset(fields[9])
    if aon_off:
        print(f"\nFirst 10 export names:")
        for i in range(min(10, fields[7])):
            nrva = struct.unpack_from('<I', data, aon_off + i*4)[0]
            noff = rva_to_offset(nrva)
            if noff:
                end = data.find(b'\x00', noff)
                name = data[noff:end].decode('ascii', errors='replace')
                print(f"  [{i}] {name}")
            else:
                print(f"  [{i}] RVA 0x{nrva:08x} not in section")
    
    # Check AddressOfFunctions
    aof_off = rva_to_offset(fields[8])
    if aof_off:
        print(f"\nFirst 10 function RVAs:")
        for i in range(min(10, fields[6])):
            frva = struct.unpack_from('<I', data, aof_off + i*4)[0]
            print(f"  [{i}] RVA=0x{frva:08x}")
    
    # Specifically check for bzQExy189ZI
    print(f"\nLooking for bzQExy189ZI...")
    if aon_off:
        for i in range(fields[7]):
            nrva = struct.unpack_from('<I', data, aon_off + i*4)[0]
            noff = rva_to_offset(nrva)
            if noff:
                end = data.find(b'\x00', noff)
                name = data[noff:end].decode('ascii', errors='replace')
                if name == 'bzQExy189ZI':
                    ord_off = rva_to_offset(fields[10])
                    ordinal = struct.unpack_from('<H', data, ord_off + i*2)[0] if ord_off else 0
                    func_rva = struct.unpack_from('<I', data, aof_off + i*4)[0] if aof_off else 0
                    print(f"  FOUND at index {i}, ordinal {ordinal}, func RVA 0x{func_rva:08x}")
                    break
        else:
            print("  NOT FOUND in AddressOfNames")