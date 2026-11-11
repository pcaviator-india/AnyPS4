import struct

with open(r'C:\PS4\temp_Limbo.PS4-PRELUDE\uroot\eboot.elf', 'rb') as f:
    raw = f.read()

ehdr = raw[:64]
phoff = struct.unpack('<Q', ehdr[32:40])[0]
phentsize = struct.unpack('<H', ehdr[54:56])[0]
phnum = struct.unpack('<H', ehdr[56:58])[0]

dyn_off = None
sceTableBase = 0
for i in range(phnum):
    ph = raw[phoff + i * phentsize : phoff + (i+1) * phentsize]
    p_type, p_flags, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_align = struct.unpack('<IIQQQQQQ', ph[:56])
    if p_type == 2:
        dyn_off = p_offset
    elif p_type == 0x61000000: # PT_SCE_DYNLIBDATA
        sceTableBase = p_offset
        print(f"PT_SCE_DYNLIBDATA at file offset 0x{sceTableBase:x}")

pos = dyn_off
tags = {}
while True:
    tag, val = struct.unpack('<Qq', raw[pos:pos+16])
    pos += 16
    if tag == 0: break
    tags[tag] = val

DT_OS_STRTAB = 0x61000035
DT_OS_STRSZ = 0x61000037
DT_OS_SYMTAB = 0x61000039
DT_OS_SYMENT = 0x6100003B
DT_OS_SYMTABSZ = 0x6100003F
DT_OS_JMPREL = 0x61000029
DT_OS_PLTRELSZ = 0x6100002D
DT_OS_RELA = 0x6100002F
DT_OS_RELASZ = 0x61000031
DT_OS_RELAENT = 0x61000033

str_off = sceTableBase + tags[DT_OS_STRTAB]
str_sz = tags[DT_OS_STRSZ]
sym_off = sceTableBase + tags[DT_OS_SYMTAB]
sym_ent = tags[DT_OS_SYMENT]
jmprel_off = sceTableBase + tags[DT_OS_JMPREL]
jmprel_sz = tags[DT_OS_PLTRELSZ]
rela_off = sceTableBase + tags[DT_OS_RELA]
rela_sz = tags[DT_OS_RELASZ]
rela_ent = tags[DT_OS_RELAENT]

print(f"str_off: 0x{str_off:x}, sym_off: 0x{sym_off:x}, jmprel_off: 0x{jmprel_off:x}")

def read_str(off):
    p = str_off + off
    end = raw.find(b'\x00', p)
    return raw[p:end].decode('latin1', 'ignore')

for off in range(0, jmprel_sz, 24):
    r_pos = jmprel_off + off
    r_offset, r_info, r_addend = struct.unpack('<QQq', raw[r_pos:r_pos+24])
    sym_idx = r_info >> 32
    s_pos = sym_off + sym_idx * sym_ent
    name_off = struct.unpack('<I', raw[s_pos:s_pos+4])[0]
    name = read_str(name_off)
    if r_offset == 0x510bb0:
        print(f"*** FOUND TARGET IN JMPREL: r_offset=0x{r_offset:x}, sym_idx={sym_idx}, name='{name}'")

for off in range(0, rela_sz, 24):
    r_pos = rela_off + off
    r_offset, r_info, r_addend = struct.unpack('<QQq', raw[r_pos:r_pos+24])
    sym_idx = r_info >> 32
    s_pos = sym_off + sym_idx * sym_ent
    name_off = struct.unpack('<I', raw[s_pos:s_pos+4])[0]
    name = read_str(name_off)
    if r_offset == 0x510bb0:
        print(f"*** FOUND TARGET IN RELA: r_offset=0x{r_offset:x}, sym_idx={sym_idx}, name='{name}'")
