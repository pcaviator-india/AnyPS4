# AnyPS4 — PS4 to Windows Porting Toolchain

## Project Overview

AnyPS4 converts PS4 ELF/SELF executables and PRX libraries to Windows PE binaries, enabling PS4 games to run natively on Windows (and eventually Linux). The project consists of:

- **`AnyPS4/`** — C++ relinker/core libraries (ELF→PE conversion, runtime entry stub, PRX implementations)
- **`tools-fetch/`** — Python toolchain (PRX stub generation, inventory, gap analysis, patching)

## Current Build Target

`Limbo.PS4-PRELUDE` → `C:\PS4\export_Limbo.PS4-PRELUDE\app.exe`

## Major Accomplishments

### 1. ELF Entry Point Transfer - reached, first blockers cleared

The game transfers control to the ELF entry point (`Transferring control to ELF entry point`). It then ran into a NULL-pointer crash, whose root cause was unresolved NID imports (see Remaining Issues). That is fixed; the game now crashes later, in `libSceAgcDriver.prx`.

### 2. All 128 PRXs Converted to Windows PE DLLs ✅

| Metric | Count |
|--------|-------|
| Total PRX files in `libs/` | 128 |
| Valid Windows PE DLLs | 128 |
| Fully converted (with exports) | 128 |
| Missing / not PE | 0 |

All PRX/SPRX files in `C:\PS4\export_Limbo.PS4-PRELUDE\libs\` are valid Windows PE binaries. Previously 16 were stubs with 0-4 exports; now all have full export tables.

### 3. Key PRX Conversions

| PRX | Before | After | Notes |
|-----|--------|-------|-------|
| `libSceSsl.prx` | 0 exports | 28 exports | mbedTLS integration |
| `libSceAudioIn.prx` | 0 exports | 8 exports | Audio input |
| `libSceAgcVsh.prx` | 1 export | 4 exports | |
| `libSceAjm.prx` | 1 export | 4 exports | |
| `libSceAjmi.prx` | 1 export | 4 exports | |
| `libSceAudio.prx` | 1 export | 4 exports | |
| `libSceShare.native.prx` | 1 export | 4 exports | |
| `libSceUsbStorage.prx` | 1 export | 4 exports | |
| `libSceUsbStorageDialog.prx` | 1 export | 4 exports | |
| `libSceXml.prx` | 1 export | 4 exports | |
| `libkernel_web.prx` | 1 export | 4 exports | |
| `ulobjmgr.prx` | 2 exports | 4 exports | |
| `libSceCommonDialog.prx` | 2 exports | 4 exports | |
| `libSceDbgThreadSanitizer.prx` | 2 exports | 4 exports | |
| `libScePlayerSelectionDialog.prx` | 1 export | 2 exports | |
| `libSceRandom.prx` | 1 export | 2 exports | |

### 4. VEH Handler (diagnostic mode)

**File**: `AnyPS4/core/relinker/elfpatcher/src/windows/WindowsEntryStubBuilder.cpp`

- Win64 ABI fixed (`sub rsp, 0x20` shadow space); returns `EXCEPTION_CONTINUE_SEARCH`.
- **Removed** the "map 4 GB at page 0" `VirtualAlloc` (null address + 2^60 size, it never worked and its result was unchecked).
- **Disabled** the RIP-skip hacks (+1 MB on access violation, +64 bytes on illegal instruction). They produced cascades of fake faults. The handler now passes every exception on, so the first real fault terminates the process.
- The old ACCESS_VIOLATION / ILLEGAL_INSTRUCTION / kernel-space code is still emitted but unreachable (jump at handler start). Delete it once no longer needed as reference.
- SSE4A emulation is handled by `libc.prx` (`CrashReport.cpp`, `APS5_NO_SSE4A_EMULATION` / `APS5_TRACE_SSE4A`), not by the stub.

### 5. PRX Inventory & Gap Analysis Tools ✅

**Files**:
- `tools-fetch/prx_inventory.py` — Scan any libs directory, classify each PRX as CONVERTED / STUB / NOT_PE, export JSON/CSV
- `tools-fetch/prx_gap_analysis.py` — Compare needed vs converted PRXs, find gaps

**GUI Tabs added to `main_app.py`**:
- **PRX Inventory** tab — Scan libs directory, see each PRX status with icons, export JSON/CSV
- **PRX Gap Analysis** tab — Compare what the game needs vs what's converted

### 6. libc.prx Export Preservation ✅

Added C++ mangled path helper exports to `preserve_exports.txt` so `nid_patcher` doesn't hash them into NIDs:
- `_Z24ResolvePath_nid_no_patchB5cxx11PKc`
- `_Z31RelinkedModulePath_nid_no_patchRKNSt10filesystem7__cxx114pathE`
- `_Z40ResolvePathOrRelinkedModule_nid_no_patchB5cxx11PKc`

## Remaining Issues

### Current blocker: exception in `libSceAgcDriver.prx` (graphics driver)

After the entry point the game now runs further, then dies. Observed on `app.exe` after the fixes below:

- `FATAL: C++ exception St13runtime_error ... cannot be delivered` from `libSceAgcDriver.prx` (`AgcDriver::DisplayBufferSize`, which throws `std::runtime_error` after formatting a message with `snprintf`). The unwinder finds no `.pdata` entry for that frame, so the exception cannot be delivered.
- Followed by write faults in game code (`app.exe+0x1402f768c`, `+0x1402f76a2`) at addresses like `0x2_4e00000`, i.e. stack/heap probing that fails.
- `0xC0000139` / error 127 (`ERROR_PROC_NOT_FOUND`) appears when `libstdc++-6.dll`, `libgcc_s_seh-1.dll` or `libwinpthread-1.dll` are not next to `app.exe`.

### Findings (what was wrong, what is fixed)

| # | Finding | Status |
|---|---------|--------|
| 1 | The earlier "missing PT_LOAD segments" theory was **wrong**. A PS4 ELF with two PT_LOAD segments (RX `0x0-0x4e6f88`, RW `0x4e8000-0x56fa00`) is normal; the ELF has no section headers, so `reloc_diagnostic.py` never analysed relocations, and it compared PE runtime addresses with ELF vaddrs. | Corrected |
| 2 | The VEH skipped RIP by 1 MB / 64 bytes and continued, creating fake "crash addresses" (`0xafdd62`, `0xafddab`...). | Fixed: handler now passes exceptions on |
| 3 | `VirtualAlloc(0, 2^60, ...)` "page-0 mapping" never worked. | Removed |
| 4 | **Root cause of the `[rdi+0x20]` write:** `<export>/libs/` held the *unpatched* PRXs (`build-full/core/libs/libs/unpatched`, C++ export names). The ELF imports by NID, so 1150 imports were unresolved. `sceKernelMapDirectMemory` (`L-Q3LEjIbgA`) was a lazy stub, left `addr == NULL`, and Limbo's heap init wrote to `[0+0x20]`. | Fixed: deployed the patched set from `build-full/core/libs/libs/` (target `libs`). Unresolved imports 1150 -> 146 |
| 5 | `tools-fetch/nid_db.xml` has 0 entries, so `nid_lookup.py` names nothing. NIDs can be named by hashing export names (SHA-1 of name + salt `518D64A635DED8C1E6B039B1C3E55230`, first 8 bytes reversed, base64 with `/` -> `-`); this identified `rTXw65xmLIA` = `sceKernelAllocateDirectMemory`, `L-Q3LEjIbgA` = `sceKernelMapDirectMemory`, `fJnpuVVBbKk` = `_Znwm`, `uMei1W9uyNo` = `exit`, `8G2LB+A3rzg` = `atexit`, `bzQExy189ZI` = `_init_env`. | Open (populate the DB) |
| 6 | Local, uncommitted changes in the `AnyPS4` submodule add a `VirtualAlloc` fallback to `sceKernelMapDirectMemory` / `sceKernelMapDirectMemory2` and relax the `ApplicationHeap` API check. The fallback hides failures; it should be removed once the real mapping path is confirmed. | Review |

### Address mapping used for debugging

- PE image base `0x140000000`; ELF vaddr 0 is at RVA `0x10000`, so `ELF vaddr = RVA - 0x10000` and `objdump -b binary` file offset = vaddr + `0x4000`.
- Entry point: ELF `0x17bbd0`. Import stubs (`ff 25 ...; push idx; jmp`) are indexed into `DT_SCE_JMPREL` (Orbis tags: strtab `0x18`, symtab `0x2868`, jmprel `0x5be0`, relative to the SCE dynlib segment at file offset `0x515be0`).

### Next steps (priority order)

1. **Make the VEH useful.** Log exception code, RIP (module + offset), fault type/address, key registers and 16 bytes at RIP, behind an env var such as `APS4_VEH_TRACE`. Delete the unreachable skip code.
2. **Fix the AgcDriver failure.** Find why `DisplayBufferSize` rejects the buffer (inspect the `DisplayBuffer` argument Limbo passes via `sceVideoOut*` / `sceGnm*`), and check `.pdata`/`.xdata` coverage in `libSceAgcDriver.prx` (the PRX has 4976 entries and none cover RVA `0x471e`; check how the PRXs are linked and whether the NID patch step or section layout drops unwind data).
3. **Resolve the remaining 146 imports.** Relink without `--lazy-binding` and run `app_trace.exe` with `APS5_TRACE_CALLS=all`; implement or map the missing functions in the proper PRX. List them with the hashing approach above.
4. **Fix the deploy tooling.** `tools-fetch/main_app.py` (`_patch_nids` / PRX copy) must copy the *patched* PRXs, plus the three MinGW runtime DLLs, into `<export>/libs` and next to `app.exe`.
5. **Remove diagnostic workarounds** (the `VirtualAlloc` fallbacks in `libkernel`, lazy-binding fake vtable) once the real paths work.
6. **Fix `tools-fetch/reloc_diagnostic.py`** to use program headers and `DT_RELA`/`DT_JMPREL` when the ELF has no section headers.
7. Then asset loading, file I/O and graphics initialisation.

## How to Build & Test

### Build relinker
```powershell
cd C:\PersonalProjects\AnyPs4\AnyPs4\build-full
cmake --build . --target relinker
```

### Relink Limbo ELF
```powershell
cd C:\PersonalProjects\AnyPs4\AnyPs4\build-full\core\relinker
.\relinker.exe --ps4 --lazy-binding --skip-sce-module --windows 'C:\PS4\export_Limbo.elf' 'C:\PS4\export_Limbo.PS4-PRELUDE\app.exe'
```

### Rebuild and deploy PRXs (required: NID-patched set)
```powershell
cd C:\PersonalProjects\AnyPs4\AnyPS4\build-full
$env:PATH='C:\PersonalProjects\AnyPs4\mingw15\mingw64\bin;'+$env:PATH
cmake --build . --target libs -j 8      # about 4 minutes, writes core\libs\libs\*.prx (NID-patched)
robocopy core\libs\libs C:\PS4\export_Limbo.PS4-PRELUDE\libs *.prx
# libstdc++-6.dll, libgcc_s_seh-1.dll, libwinpthread-1.dll must sit next to app.exe
```
Do not deploy `core\libs\libs\unpatched\*.prx`: their exports are not NIDs.

### Run game
```powershell
cd C:\PS4\export_Limbo.PS4-PRELUDE
.\app.exe
```

### Trace imports
```powershell
cd C:\PersonalProjects\AnyPs4\AnyPS4\build-full\core\relinker
.\relinker.exe --ps4 --skip-sce-module --windows --trace-imports 'C:\PS4\export_Limbo.elf' 'C:\PS4\export_Limbo.PS4-PRELUDE\app_trace.exe'
$env:APS5_TRACE_CALLS='all'; .\app_trace.exe   # without --lazy-binding, lists every unresolved NID
```

### Run with trace
```powershell
cd C:\PersonalProjects\AnyPs4\tools-fetch
python trace_app.py 'C:\PS4\export_Limbo.PS4-PRELUDE\app.exe' 'C:\PS4\export_Limbo.PS4-PRELUDE'
```

### Check PRX status
```powershell
cd C:\PersonalProjects\AnyPs4\tools-fetch
python main_app.py  # → PRX Inventory tab
```
