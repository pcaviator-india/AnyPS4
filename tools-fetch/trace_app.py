import ctypes
from ctypes import wintypes
import sys
import os

DEBUG_ONLY_THIS_PROCESS = 0x00000002
INFINITE = 0xFFFFFFFF
DBG_CONTINUE = 0x00010002
DBG_EXCEPTION_NOT_HANDLED = 0x80010001

class EXCEPTION_RECORD(ctypes.Structure):
    pass
EXCEPTION_RECORD._fields_ = [
    ('ExceptionCode', wintypes.DWORD),
    ('ExceptionFlags', wintypes.DWORD),
    ('ExceptionRecord', ctypes.POINTER(EXCEPTION_RECORD)),
    ('ExceptionAddress', ctypes.c_void_p),
    ('NumberParameters', wintypes.DWORD),
    ('ExceptionInformation', ctypes.c_size_t * 15),
]

class EXCEPTION_DEBUG_INFO(ctypes.Structure):
    _fields_ = [
        ('ExceptionRecord', EXCEPTION_RECORD),
        ('dwFirstChance', wintypes.DWORD),
    ]

class OUTPUT_DEBUG_STRING_INFO(ctypes.Structure):
    _fields_ = [
        ('lpDebugStringData', ctypes.c_void_p),
        ('fUnicode', wintypes.WORD),
        ('nDebugStringLength', wintypes.WORD),
    ]

class UNION_DEBUG_INFO(ctypes.Union):
    _fields_ = [
        ('Exception', EXCEPTION_DEBUG_INFO),
        ('DebugString', OUTPUT_DEBUG_STRING_INFO),
        ('ExitProcess', wintypes.DWORD),
        ('pad', ctypes.c_uint8 * 160),
    ]

class DEBUG_EVENT(ctypes.Structure):
    _fields_ = [
        ('dwDebugEventCode', wintypes.DWORD),
        ('dwProcessId', wintypes.DWORD),
        ('dwThreadId', wintypes.DWORD),
        ('u', UNION_DEBUG_INFO),
    ]

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
kernel32.ReadProcessMemory.argtypes = [wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
kernel32.ReadProcessMemory.restype = wintypes.BOOL
kernel32.WaitForDebugEvent.argtypes = [ctypes.c_void_p, wintypes.DWORD]
kernel32.WaitForDebugEvent.restype = wintypes.BOOL
kernel32.ContinueDebugEvent.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.DWORD]
kernel32.ContinueDebugEvent.restype = wintypes.BOOL

EXCEPTION_DEBUG_EVENT = 1
CREATE_THREAD_DEBUG_EVENT = 2
CREATE_PROCESS_DEBUG_EVENT = 3
EXIT_THREAD_DEBUG_EVENT = 4
EXIT_PROCESS_DEBUG_EVENT = 5
LOAD_DLL_DEBUG_EVENT = 6
UNLOAD_DLL_DEBUG_EVENT = 7
OUTPUT_DEBUG_STRING_EVENT = 8
RIP_EVENT = 9

class STARTUPINFO(ctypes.Structure):
    _fields_ = [
        ('cb', wintypes.DWORD),
        ('lpReserved', wintypes.LPWSTR),
        ('lpDesktop', wintypes.LPWSTR),
        ('lpTitle', wintypes.LPWSTR),
        ('dwX', wintypes.DWORD),
        ('dwY', wintypes.DWORD),
        ('dwXSize', wintypes.DWORD),
        ('dwYSize', wintypes.DWORD),
        ('dwXCountChars', wintypes.DWORD),
        ('dwYCountChars', wintypes.DWORD),
        ('dwFillAttribute', wintypes.DWORD),
        ('dwFlags', wintypes.DWORD),
        ('wShowWindow', wintypes.WORD),
        ('cbReserved2', wintypes.WORD),
        ('lpReserved2', ctypes.c_char_p),
        ('hStdInput', wintypes.HANDLE),
        ('hStdOutput', wintypes.HANDLE),
        ('hStdError', wintypes.HANDLE),
    ]

class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [
        ('hProcess', wintypes.HANDLE),
        ('hThread', wintypes.HANDLE),
        ('dwProcessId', wintypes.DWORD),
        ('dwThreadId', wintypes.DWORD),
    ]

def trace(exe_path, cwd):
    si = STARTUPINFO()
    si.cb = ctypes.sizeof(si)
    pi = PROCESS_INFORMATION()

    cmd = f'"{exe_path}"'
    ok = kernel32.CreateProcessW(
        exe_path,
        cmd,
        None, None, False,
        DEBUG_ONLY_THIS_PROCESS,
        None,
        cwd,
        ctypes.byref(si),
        ctypes.byref(pi)
    )
    if not ok:
        print(f"CreateProcess failed: {ctypes.get_last_error()}")
        return

    print(f"Process started PID={pi.dwProcessId}")
    hProcess = pi.hProcess

    event = DEBUG_EVENT()
    while True:
        if not kernel32.WaitForDebugEvent(ctypes.byref(event), INFINITE):
            break

        code = event.dwDebugEventCode
        cont_status = DBG_CONTINUE

        if code == OUTPUT_DEBUG_STRING_EVENT:
            dbg = event.u.DebugString
            length = dbg.nDebugStringLength
            addr = dbg.lpDebugStringData
            buf = ctypes.create_string_buffer(length)
            bytesRead = ctypes.c_size_t()
            kernel32.ReadProcessMemory(hProcess, addr, buf, length, ctypes.byref(bytesRead))
            try:
                msg = buf.raw[:bytesRead.value].decode('utf-8', errors='replace').rstrip('\r\n')
                print(f"[DebugString] {msg}")
            except Exception as e:
                print(f"[DebugString raw] {buf.raw[:bytesRead.value]}")

        elif code == EXCEPTION_DEBUG_EVENT:
            exc = event.u.Exception
            rec = exc.ExceptionRecord
            first = "first-chance" if exc.dwFirstChance else "SECOND-CHANCE (UNHANDLED)"
            if not hasattr(trace, 'exc_count'):
                trace.exc_count = {}
            key = (rec.ExceptionCode, rec.ExceptionAddress)
            count = trace.exc_count.get(key, 0) + 1
            trace.exc_count[key] = count
            if count <= 5:
                print(f"[Exception #{count}] code=0x{rec.ExceptionCode:08x} at 0x{rec.ExceptionAddress or 0:016x} ({first})")
                if rec.ExceptionCode == 0xC0000005 and rec.NumberParameters >= 2:
                    kind = "read" if rec.ExceptionInformation[0] == 0 else "write" if rec.ExceptionInformation[0] == 1 else "execute"
                    target_addr = rec.ExceptionInformation[1]
                    print(f"            Access violation {kind} at 0x{target_addr:016x}")
            elif count == 6:
                print(f"[Exception] ... suppressing further occurrences of code=0x{rec.ExceptionCode:08x} at 0x{rec.ExceptionAddress or 0:016x} ...")
            cont_status = DBG_CONTINUE if rec.ExceptionCode == 0x80000003 else DBG_EXCEPTION_NOT_HANDLED

        elif code == EXIT_PROCESS_DEBUG_EVENT:
            exit_code = event.u.ExitProcess
            print(f"[ExitProcess] exit_code=0x{exit_code:08x} ({exit_code})")
            kernel32.ContinueDebugEvent(event.dwProcessId, event.dwThreadId, DBG_CONTINUE)
            break

        kernel32.ContinueDebugEvent(event.dwProcessId, event.dwThreadId, cont_status)

if __name__ == '__main__':
    exe = sys.argv[1] if len(sys.argv) > 1 else r"C:\PS4\export_Limbo.PS4-PRELUDE\app.exe"
    cwd = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(exe)
    trace(exe, cwd)
