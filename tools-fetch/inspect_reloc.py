import struct

# Let's inspect eboot.elf relocations to find the exact symbol for GOT entry 0x510bb0
with open(r'C:\PS4\temp_Limbo.PS4-PRELUDE\uroot\eboot.elf', 'rb') as f:
    elf = f.read()

# In eboot.elf, where is 0x510bb0 referenced in the relocation table?
# Earlier we found it at file offset 0x51b880 in eboot.elf.
# At 0x51b880: r_offset=0x510bb0, type=7 (JUMP_SLOT), sym_idx=337
# What is symbol 337 in eboot.elf?
# In PS4 ELFs, symbol names are NIDs.
# Let's read the relocation table DT_SCE_PLTRELA (or DT_RELA)
# Let's inspect all strings in eboot.elf or find how AnyPS4 parses NIDs!
print(f"File size: {len(elf)}")
