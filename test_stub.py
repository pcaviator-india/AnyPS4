import ctypes, tempfile, os, sys
from ctypes import wintypes
sys.path.insert(0, 'c:/PersonalProjects/AnyPs4/tools-fetch')
from phase2_stubs import build_notimplemented_stub_dll

tmp = tempfile.NamedTemporaryFile(suffix='.prx', delete=False)
tmp.close()
build_notimplemented_stub_dll('test.prx', ['bzQExy189ZI', 'TestExport'], tmp.name)
print('Size: %d' % os.path.getsize(tmp.name))

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
LoadLibraryW = kernel32.LoadLibraryW
LoadLibraryW.restype = wintypes.HMODULE
LoadLibraryW.argtypes = [wintypes.LPCWSTR]

hmod = LoadLibraryW(tmp.name)
err = kernel32.GetLastError()
print('Module handle: %s' % hmod)
print('GetLastError: %d' % err)

if hmod:
    GetProcAddress = kernel32.GetProcAddress
    GetProcAddress.restype = ctypes.c_void_p
    GetProcAddress.argtypes = [wintypes.HMODULE, ctypes.c_char_p]
    proc = GetProcAddress(hmod, b'bzQExy189ZI')
    if proc:
        print('GetProcAddress: 0x%x' % proc)
        func = ctypes.CFUNCTYPE(ctypes.c_void_p)(proc)
        result = func()
        print('bzQExy189ZI() = 0x%x' % result)
        print('SUCCESS!')
    else:
        print('GetProcAddress: NULL')

os.unlink(tmp.name)