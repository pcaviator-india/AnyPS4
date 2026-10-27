"""Debug: dump raw dynamic symbols from a PS4 eboot.elf."""
import struct
import sys

p = sys.argv[1]
data = open(p, "rb").read()
# PT_LOAD0: file off 0x4000 maps vaddr 0 (from header inspection)
BASE_OFF, BASE_VADDR = 0x4000, 0x0


def v2f(v):
    return BASE_OFF + (v - BASE_VADDR)


strtab_v, symtab_v = 0x18, 0x37d8
symsz = 0x49C8
strsz = 0x37C0
soff, yoff = v2f(strtab_v), v2f(symtab_v)
print("strtab file off", hex(soff), "symtab file off", hex(yoff), "count", symsz // 24)

count = symsz // 24
undef = 0
samples = []
for i in range(count):
    off = yoff + i * 24
    st_name, st_info, st_other, st_shndx, st_value, st_size = struct.unpack_from(
        "<IBBHQQ", data, off)
    if st_name == 0 or st_shndx != 0:
        continue
    undef += 1
    if len(samples) < 25:
        name_off = soff + st_name
        name = "<out-of-range>"
        if st_name < strsz and name_off < len(data):
            end = data.index(b"\0", name_off)
            name = data[name_off:end].decode("utf-8", "replace")
        samples.append((i, hex(st_name), st_info, st_shndx, name))
print("undefined symbols:", undef)
for s in samples:
    print(s)
# also print the first 10 symbols regardless of binding, with raw bytes
print("\nfirst 10 raw symbols:")
for i in range(10):
    off = yoff + i * 24
    st_name, st_info, st_other, st_shndx, st_value, st_size = struct.unpack_from(
        "<IBBHQQ", data, off)
    print(i, hex(st_name), st_info, st_shndx, hex(st_value))

