# AnyPS4 Porting Toolchain - Phase 2 Plan

## Goal

Run `Limbo.PS4-PRELUDE` past ELF entry, load assets, initialise graphics and run on Windows.

## Current State (2026-11-11)

- Control reaches the ELF entry point and the game runs for a while (heap init, allocator, C++ static init).
- All 128 PRXs are valid PE DLLs and load when the three MinGW runtime DLLs sit next to `app.exe`.
- With the NID-patched PRXs deployed, unresolved ELF imports dropped from 1150 to 146.
- The process still crashes: `AgcDriver::DisplayBufferSize` (`libSceAgcDriver.prx`) throws `std::runtime_error` and the unwinder finds no unwind data for that frame; later, write faults occur in game code.

## Root Causes and Status

| # | Item | Status |
|---|------|--------|
| 1 | Fake vtable / lazy stub displacement bug | [x] Fixed |
| 2 | VEH ABI and return value (shadow space, `CONTINUE_SEARCH`) | [x] Fixed |
| 3 | Heap allocator verification rejecting the default API | [x] Fixed |
| 4 | libc/libkernel symbol compatibility (`preserve_exports.txt`) | [x] Fixed |
| 5 | All 128 PRXs converted with exports | [x] Fixed |
| 6 | PRX inventory / gap analysis GUI tabs | [x] Done |
| 7 | **"Missing PT_LOAD segments" theory** | [x] **Disproved**: two PT_LOAD segments are normal; the ELF has no section headers, and the earlier crash addresses were produced by the VEH skipping RIP |
| 8 | VEH RIP-skip hacks and bogus `VirtualAlloc(0, 2^60)` page-0 map | [x] Removed (VEH now passes exceptions on) |
| 9 | **Unpatched PRXs deployed** (exports not NIDs) -> 1150 unresolved imports -> `sceKernelMapDirectMemory` returned NULL -> write to `[0+0x20]` | [x] Fixed by deploying `build-full/core/libs/libs/*.prx` |
| 10 | `AgcDriver::DisplayBufferSize` throws, no unwind data for the frame | [ ] Open (current blocker) |
| 11 | 146 remaining unresolved imports | [ ] Open |
| 12 | Local `VirtualAlloc` fallback in `sceKernelMapDirectMemory(2)` hides mapping failures | [ ] Review / remove |
| 13 | `nid_db.xml` empty (0 entries) | [ ] Open |

## Next Steps (priority order)

1. [ ] **VEH diagnostics**: add an env-var-gated trace (code, RIP module+offset, fault type/address, registers, bytes at RIP) in `WindowsEntryStubBuilder.cpp`; delete the unreachable skip code.
2. [ ] **AgcDriver failure**:
   - find which `DisplayBuffer` field `DisplayBufferSize` rejects (arguments come from the game's `sceVideoOut*` / `sceGnm*` calls);
   - check `.pdata`/`.xdata` coverage in `libSceAgcDriver.prx` (4976 entries, none cover RVA `0x471e`): see how the PRX is linked and whether the NID patch or section layout drops unwind data, and whether `configure_windows_unwind` applies to this target.
3. [ ] **Remaining 146 imports**: relink without `--lazy-binding`, run `app_trace.exe` with `APS5_TRACE_CALLS=all`, name NIDs by hashing, implement or map them in the right PRX.
4. [ ] **Deploy tooling**: make `tools-fetch/main_app.py` copy the patched PRXs and the MinGW runtime DLLs; stop using the `unpatched` set.
5. [ ] **Remove workarounds**: libkernel `VirtualAlloc` fallbacks, lazy-binding fake vtable once real paths work.
6. [ ] **Fix `tools-fetch/reloc_diagnostic.py`** to parse program headers and `DT_RELA`/`DT_JMPREL` when section headers are absent.
7. [ ] **Populate `nid_db.xml`** (or load names via `AnyPS4/tools/nid_names.py`) so `nid_lookup.py` returns names.
8. [ ] Then: asset loading, file I/O, graphics init.

## Debugging Cheat Sheet

- PE image base `0x140000000`; ELF vaddr 0 is RVA `0x10000`: `ELF vaddr = RVA - 0x10000`; for `objdump -b binary`, file offset = vaddr + `0x4000`.
- Import stubs are `ff 25 <rel32>; 68 <idx>; e9 ...`; `<idx>` indexes `DT_SCE_JMPREL` (Orbis dynamic tags: strtab `0x18`, symtab `0x2868`, jmprel `0x5be0`, relative to the SCE dynlib segment at file offset `0x515be0`).
- NID = base64url-ish(SHA-1(name + `518D64A635DED8C1E6B039B1C3E55230`)[:8] reversed), `/` replaced by `-`.
- `trace_app.py` attaches a debugger and prints first/second-chance exceptions, debug strings and exit code; `APS5_TRACE_CALLS=all` with a `--trace-imports` build lists unresolved imports.
- `LoadLibrary` error 127 on a PRX usually means a missing dependency DLL or a missing export in a dependency (`libc.prx` is the root of the chain).

## Files

### Core C++
- `AnyPS4/core/relinker/elfpatcher/src/windows/WindowsEntryStubBuilder.cpp` - entry stub, VEH, import resolution
- `AnyPS4/core/relinker/elfpatcher/src/windows/WindowsPePatcher.cpp` - PE writer
- `AnyPS4/core/libs/CMakeLists.txt` - `libs` target (build then NID-patch every PRX)
- `AnyPS4/core/libs/prx/libc/preserve_exports.txt` - exports kept un-hashed
- `AnyPS4/core/libs/prx/libkernel/DirectMemory/Export.cpp` - direct memory (contains the local fallback)
- `AnyPS4/core/libs/prx/libc/src/specifics/windows/CrashReport.cpp` - crash reports, SSE4A emulation

### Python tools (`tools-fetch/`)
- `main_app.py` GUI pipeline; `prx_inventory.py`, `prx_gap_analysis.py`; `trace_app.py`; `reloc_diagnostic.py` (needs the fix above); `nid_lookup.py`, `nid_db.py`.

## Build and Test

```powershell
# relinker
cd C:\PersonalProjects\AnyPs4\AnyPS4\build-full
$env:PATH='C:\PersonalProjects\AnyPs4\mingw15\mingw64\bin;'+$env:PATH
cmake --build . --target relinker

# PRXs (NID-patched), ~4 minutes, then deploy
cmake --build . --target libs -j 8
robocopy core\libs\libs C:\PS4\export_Limbo.PS4-PRELUDE\libs *.prx

# relink and run
cd core\relinker
.\relinker.exe --ps4 --lazy-binding --skip-sce-module --windows 'C:\PS4\export_Limbo.elf' 'C:\PS4\export_Limbo.PS4-PRELUDE\app.exe'
cd C:\PS4\export_Limbo.PS4-PRELUDE; .\app.exe

# trace
cd C:\PersonalProjects\AnyPs4\tools-fetch
python trace_app.py 'C:\PS4\export_Limbo.PS4-PRELUDE\app.exe' 'C:\PS4\export_Limbo.PS4-PRELUDE'
```

If `app.exe` is still running, relinking fails with "Cannot open output file"; stop the process first.
