import struct

with open(r'C:\PS4\temp_Limbo.PS4-PRELUDE\uroot\eboot.elf', 'rb') as f:
    def va_to_file(va):
        if va < 0x4e8000:
            return va + 0x4000
        else:
            return va - 0x4e8000 + 0x4ec000

    symtab_va = 0x61110
    strtab_va = 0x510b58

    sym_off = va_to_file(symtab_va + 337 * 24)
    f.seek(sym_off)
    st_name, st_info, st_other, st_shndx, st_value, st_size = struct.unpack('<IBBHQQ', f.read(24))

    str_off = va_to_file(strtab_va + st_name)
    f.seek(str_off)
    chars = []
    for _ in range(100):
        c = f.read(1)
        if not c or c == b'\x00':
            break
        chars.append(c)
    name = b''.join(chars).decode('latin1', 'ignore')
    print(f"Symbol 337: name='{name}', val=0x{st_value:x}, shndx={st_shndx}")
