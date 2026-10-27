"""Dump PS4 ELF imports correctly (SCE dynlibdata-relative tables)."""
import struct
import sys
import re

p = sys.argv[1]
data = open(p, "rb").read()
off = 0xCDE1E8
tags = {}
for i in range(60):
    t, v = struct.unpack_from("<qQ", data, off + i * 16)
    tags[t] = v
    if t == 0:
        break

ST_STRTAB = 0x61000035
ST_SYMTAB = 0x61000039
ST_STRSZ = 0x61000037
ST_SYMSZ = 0x6100003F
strtab_v = tags[ST_STRTAB]
symtab_v = tags[ST_SYMTAB]
strsz = tags[ST_STRSZ]
symsz = tags[ST_SYMSZ]
dynlibdata = 0xC56240
soff = dynlibdata + strtab_v
yoff = dynlibdata + symtab_v
print("strtab file", hex(soff), "symtab file", hex(yoff),
      "count", symsz // 24, "strsz", hex(strsz))
count = symsz // 24
names = []
for i in range(count):
    o = yoff + i * 24
    st_name, st_info, st_other, st_shndx, st_value, st_size = struct.unpack_from(
        "<IBBHQQ", data, o)
    if st_name == 0 or st_shndx != 0:
        continue
    if st_name >= strsz:
        continue
    end = data.index(b"\0", soff + st_name)
    name = data[soff + st_name:end].decode("utf-8", "replace")
    if name:
        names.append(name)
print("undefined named imports:", len(names))
seen = set()
uniq = [n for n in names if not (n in seen or seen.add(n))]
print("unique:", len(uniq))
open("tools-fetch/imports_raw.txt", "w").write("\n".join(uniq))
base = sorted({n.split("#")[0] for n in uniq})
open("tools-fetch/imports.txt", "w").write("\n".join(base))
print("wrote tools-fetch/imports.txt with", len(base), "base nids")
for n in uniq[:10]:
    print("  raw:", n)
