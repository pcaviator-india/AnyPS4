import struct

with open(r'C:\PS4\export_Limbo.PS4-PRELUDE\app.exe', 'rb') as f:
    data = f.read()

# Let's search for RVA 0x520bb0 in app.exe (in LazyStubs or imports)
target_rva = 0x520bb0
pattern = struct.pack('<I', target_rva)

idx = 0
found = []
while True:
    pos = data.find(pattern, idx)
    if pos == -1: break
    found.append(pos)
    idx = pos + 1

print(f"Found 0x{target_rva:x} at offsets: {[hex(p) for p in found]}")

# Let's inspect around each offset
for p in found:
    print(f"\n--- At offset 0x{p:x} ---")
    chunk = data[max(0, p - 32):p + 64]
    # Check if there are strings nearby
    for offset in range(max(0, p - 100), min(len(data), p + 100)):
        # print string if ASCII
        if data[offset:offset+1].isalpha():
            end = data.find(b'\x00', offset)
            if end != -1 and 3 < end - offset < 50:
                s = data[offset:end]
                if all(32 <= b < 127 for b in s):
                    print(f"  String at 0x{offset:x}: {s.decode('latin1')}")
