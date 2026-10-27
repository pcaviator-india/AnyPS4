import ctypes, os

prx_path = r'C:\Users\Info-Tech\Downloads\Games\ps4\export\export__SuperPSX_-Mega.Shoot-CUSA59042-EUR-Game-PS4-Opoisso893\libs\unresolved_imports.prx'
print(f"Stub size: {os.path.getsize(prx_path)} bytes")

try:
    lib = ctypes.WinDLL(prx_path)
    print("Stub loaded successfully!")
    
    try:
        func = lib.bzQExy189ZI
        func.restype = ctypes.c_void_p
        result = func()
        print(f"bzQExy189ZI() = 0x{result:x}")
    except Exception as e:
        print(f"Call failed: {e}")
except Exception as e:
    print(f"Load failed: {e}")

# Check if stub_calls.log exists anywhere
for root, dirs, files in os.walk(r'C:\Users\Info-Tech\Downloads\Games\ps4\export\export__SuperPSX_-Mega.Shoot-CUSA59042-EUR-Game-PS4-Opoisso893'):
    for f in files:
        if 'stub_call' in f.lower():
            print(f"Found log: {os.path.join(root, f)}")