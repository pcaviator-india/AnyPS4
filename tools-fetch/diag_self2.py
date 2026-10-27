import math
import struct
from collections import Counter

path = r'c:\PersonalProjects\AnyPs4\tools-fetch\pkgout\uroot\eboot.bin'
data = open(path, 'rb').read()


def entropy(b):
    if not b:
        return 0.0
    c = Counter(b)
    n = len(b)
    return -sum((v / n) * math.log2(v / n) for v in c.values())


print('raw header 0x00..0x40:')
for o in range(0, 0x40, 16):
    print('  %#06x: %s' % (o, data[o:o + 16].hex(' ')))

print('\nraw records 0x40..0x160:')
for o in range(0x40, 0x160, 16):
    print('  %#06x: %s' % (o, data[o:o + 16].hex(' ')))

print('\nentropy probes:')
for off in [0x400, 0x6380, 0xb4e690, 0xb4ead0, 0xbae68c, 0xbd2d10, 0xbd3110, 0xcda4a0]:
    e = entropy(data[off:off + 0x4000])
    print('  %#09x: %.3f bits/byte  first16=%s' % (off, e, data[off:off + 16].hex(' ')))

print('\nsize checks:')
print('  rec[0] 0x6380 + 0xb4830c = %#x' % (0x6380 + 0xb4830c))
print('  rec[0] region to rec[1]: 0xb4e690 - 0x6380 = %#x' % (0xb4e690 - 0x6380))
print('  rec[2] 0xb4ead0 + 0x84240 = %#x' % (0xb4ead0 + 0x84240))
