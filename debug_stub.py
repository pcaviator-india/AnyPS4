import struct, sys, tempfile, os
sys.path.insert(0, 'c:/PersonalProjects/AnyPs4/tools-fetch')
from phase2_stubs import build_notimplemented_stub_dll

test_names = ['bzQExy189ZI', 'testFunc1', 'testFunc2']
tmp = tempfile.NamedTemporaryFile(suffix='.prx', delete=False)
tmp.close()
build_notimplemented_stub_dll('test.prx', test_names, tmp.name)

with open(tmp.name, 'rb') as f:
    data = f.read()

pe_off = struct.unpack_from('<I', data, 0x3C)[0]
opt_off = pe_off + 24
size_opt_header = struct.unpack_from('<H', data, pe_off + 20)[0]
num_sections = struct.unpack_from('<H', data, pe_off + 6)[0]
sec_off = opt_off + size_opt_header

# Find .edata section
for i in range(num_sections):
    base = sec_off + i * 40
    name = data[base:base+8].rstrip(b'\x00').decode('ascii', 'replace')
    vsize, vaddr, rsize, raddr = struct.unpack_from('<IIII', data, base + 8)
    if name == '.edata':
        print(f'.edata section: vaddr=0x{vaddr:x}, raddr=0x{raddr:x}, vsize=0x{vsize:x}')
        edata_section_data = data[raddr:raddr+40]
        print(f'First 40 bytes at file offset 0x{raddr:x}: {edata_section_data.hex()}')
        ch = struct.unpack_from('<I', edata_section_data, 0)[0]
        print(f'  Characteristics (first 4 bytes): 0x{ch:x}')
        break

# Check the optional header data directory
dd_start = opt_off + 108
exp_rva, exp_size = struct.unpack_from('<II', data, dd_start)
print(f'\nData Directory[0]: RVA=0x{exp_rva:x}, Size=0x{exp_size:x}')

# Check NumberOfSections
num_sec = struct.unpack_from('<H', data, pe_off + 6)[0]
print(f'NumberOfSections: {num_sec}')

os.unlink(tmp.name)