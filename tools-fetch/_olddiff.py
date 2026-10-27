import struct

b = r'C:\PersonalProjects\AnyPs4\tools-fetch'
old = open(b + '/pkgout/uroot/eboot.elf', 'rb').read()
new = open(b + '/pkgout/uroot/_verify/final_test.elf', 'rb').read()
print('old', len(old), 'new', len(new))


def h(p):
    d = open(p, 'rb').read()
    t = struct.unpack_from('<H', d, 16)[0]
    phoff = struct.unpack_from('<I', d, 0x28)[0]
    phentsize = struct.unpack_from('<H', d, 0x2C)[0]
    phnum = struct.unpack_from('<H', d, 0x30)[0]
    print(p.split('/')[-1], 'type=0x%04x phoff=0x%x phentsize=0x%x phnum=%d ehdr_end=0x%x' % (
        t, phoff, phentsize, phnum, phoff + phentsize * phnum))


h(b + '/pkgout/uroot/eboot.elf')
h(b + '/pkgout/uroot/_verify/final_test.elf')

# Is old == new with 2566 extra bytes inserted somewhere?
delta = len(old) - len(new)
print('delta', delta, hex(delta))
# Candidate: old has 13 phdrs, new has 12 (PT_NOTE dropped?)
# Check tails: old[-512:] vs new[-512:]
print('tail match:', old[-512:] == new[-512:])
# Find divergence walking from start
i = 0
while i < min(len(old), len(new)) and old[i] == new[i]:
    i += 1
print('first diff at', hex(i))
print('old @', hex(i), ':', old[i:i + 48].hex())
print('new @', hex(i), ':', new[i:i + 48].hex())

