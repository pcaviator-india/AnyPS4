import mmap

# Absolute path to the PKG file
pkg_path = r'c:\PersonalProjects\AnyPs4\PKG\[SuperPSX]-Mega.Shoot-CUSA59042-EUR-Game-PS4-Opoisso893.pkg'
f = open(pkg_path, 'rb')
m = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
print('size:', len(m))
print('first64:', m[:64].hex())
print('end64:', m[-64:].hex())

# Find any occurrence of the PKG magic string
pat = b'PKG'
idxs = []
start = 0
while True:
    i = m.find(pat, start)
    if i == -1:
        break
    idxs.append(i)
    start = i + 1
print('PKG magic offsets:', [hex(i) for i in idxs[:20]])

# Look for 'eboot.bin' and 'sce_module'
for s in [b'eboot.bin', b'sce_module', b'param.sfo', b'ps4_linker']:
    i = m.find(s)
    print(s, 'at', hex(i) if i >= 0 else 'not found')

# Check for the string at offset 0x2a80 which was referenced earlier
print('offset 0x2a80 bytes:', m[0x2a80:0x2a80+32].hex())

