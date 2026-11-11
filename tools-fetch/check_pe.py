import struct

path = r'C:\PS4\export_Limbo.PS4-PRELUDE\app.exe'
with open(path,'rb') as f: data=f.read()
pe_off=struct.unpack_from('<I',data,0x3C)[0]
print('PE signature: 0x{:x}'.format(struct.unpack_from('<I',data,pe_off)[0]))
machine=struct.unpack_from('<H',data,pe_off+4)[0]
print('Machine: 0x{:x} (0x8664=x64)'.format(machine))
num_sec=struct.unpack_from('<H',data,pe_off+6)[0]
opt_size=struct.unpack_from('<H',data,pe_off+20)[0]
print('Num sections: {}'.format(num_sec))
print('Optional header size: 0x{:x}'.format(opt_size))
magic=struct.unpack_from('<H',data,pe_off+24)[0]
print('Optional header magic: 0x{:x} (0x20b=PE32+)'.format(magic))
print('File size: 0x{:x}'.format(len(data)))