import struct
import sys

path = r'c:\PersonalProjects\AnyPs4\tools-fetch\pkgout\uroot\eboot.bin'
data = open(path, 'rb').read()

print('file size:', hex(len(data)))
print('SELF magic:', hex(struct.unpack_from('<I', data, 0)[0]))

# SELF records at 0x40, 0x20 bytes each, up to 0x400
print('\nSELF records (offset 0x40, 0x20 bytes each):')
off = 0x40
i = 0
while off + 0x20 <= 0x400:
    flags, segment, size, size_again = struct.unpack_from('<QQQQ', data, off)
    if size == 0 or size != size_again:
        print('  stop at record %d: flags=%#x segment=%#x size=%#x size_again=%#x' % (i, flags, segment, size, size_again))
        break
    print('  [%d] flags=%#x segment_offset=%#x size=%#x' % (i, flags, segment, size))
    off += 0x20
    i += 1

# Inner ELF
inner = data.find(b'\x7fELF')
print('\ninner ELF at:', hex(inner))
ehdr = data[inner:inner + 0x40]
program_offset = struct.unpack_from('<Q', ehdr, 0x20)[0]
entry_size = struct.unpack_from('<H', ehdr, 0x36)[0]
count = struct.unpack_from('<H', ehdr, 0x38)[0]
print('program header table at inner+%#x, %d entries of %d bytes' % (program_offset, count, entry_size))

PT = {1: 'PT_LOAD', 2: 'PT_DYNAMIC', 3: 'PT_INTERP', 4: 'PT_NOTE', 6: 'PT_PHDR', 7: 'PT_TLS',
      0x6474E550: 'PT_GNU_EH_FRAME', 0x6474E551: 'PT_GNU_STACK', 0x6474E552: 'PT_GNU_RELRO',
      0x61000000: 'PT_SCE_DYNLIBDATA', 0x61000001: 'PT_OS_PROCPARAM', 0x61000002: 'PT_OS_0x61000002',
      0x61000010: 'PT_SCE_MODULEPARAM?', 0x61100000: 'PT_SCE_0x61100000', 0x6FFFFFFF: 'PT_LOSUNW'}

for index in range(count):
    o = inner + program_offset + index * 56
    kind, flags, file_offset, vaddr, paddr, file_size, memory_size, alignment = struct.unpack_from('<IIQQQQQQ', data, o)
    name = PT.get(kind, 'PT_%#x' % kind)
    print('  [%2d] %-20s flags=%#x offset=%#010x vaddr=%#012x filesz=%#010x memsz=%#010x align=%#x'
          % (index, name, flags, file_offset, vaddr, file_size, memory_size, alignment))

# Show what load_for(0xc00000) would find
print('\nchecking coverage of vaddr 0xc00000:')
covered = False
for index in range(count):
    o = inner + program_offset + index * 56
    kind, flags, file_offset, vaddr, paddr, file_size, memory_size, alignment = struct.unpack_from('<IIQQQQQQ', data, o)
    if kind == 1 and memory_size and vaddr <= 0xc00000 < vaddr + memory_size:
        print('  covered by PT_LOAD [%d]: vaddr=%#x memsz=%#x' % (index, vaddr, memory_size))
        covered = True
if not covered:
    print('  NOT covered by any PT_LOAD')
