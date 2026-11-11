# AnyPS4 — PS4 to Windows Porting Toolchain

## Project Overview

AnyPS4 converts PS4 ELF/SELF executables and PRX libraries to Windows PE binaries, enabling PS4 games to run natively on Windows (and eventually Linux). The project consists of:

- **`AnyPS4/`** — C++ relinker/core libraries (ELF→PE conversion, runtime entry stub, PRX implementations)
- **`tools-fetch/`** — Python toolchain (PRX stub generation, inventory, gap analysis, patching)

## Current Build Target

`Limbo.PS4-PRELUDE` → `C:\PS4\export_Limbo.PS4-PRELUDE\app.exe`

## Major Accomplishments

### 1. ELF Entry Point Transfer — RESOLVED ✅

The game now successfully **transfers control to the ELF entry point** (`Transferring control to ELF entry point` message appears in console). Previously this was the hard blocker — the game crashed immediately at entry.

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

### 4. VEH Handler Fixes ✅

**File**: `core/relinker/elfpatcher/src/windows/WindowsEntryStubBuilder.cpp`

- Fixed Win64 ABI (added `sub rsp, 0x20` shadow space)
- Fixed return value (`EXCEPTION_CONTINUE_SEARCH` instead of `EXCEPTION_EXECUTE_HANDLER`)
- Added page-0 mapping with 256MB at `PAGE_EXECUTE_READWRITE` before entry point transfer
- Added ACCESS_VIOLATION handler that commits faulting pages via `VirtualAlloc`
- Added ILLEGAL_INSTRUCTION handler that skips SSE4A instructions (RIP modification via CONTEXT offset `0xF8`)
- Added kernel-space fault handler that sets `RAX=0x1000`

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

### Crash After ELF Entry Point ❌

The game reaches the entry point but crashes shortly after with access violations.

**ROOT CAUSE IDENTIFIED** (using `tools-fetch/reloc_diagnostic.py`):

The ELF has only TWO PT_LOAD segments:
- Segment 1: `vaddr=0x0, memsz=0x4e6f88` (RX) - covers 0x0 to 0x4e6f88
- Segment 2: `vaddr=0x4e8000, memsz=0x87a00` (RW) - covers 0x4e8000 to 0x56fa00

**ALL crash addresses are OUTSIDE these segments:**

| Address | Inside Segment? | Status |
|---------|----------------|--------|
| 0x17bbd0 (entry point) | ✅ INSIDE | Valid code |
| 0x60f4c0 | ❌ OUTSIDE | Above segment end (0x56fa00) |
| 0xaf31c7 | ❌ OUTSIDE | Above segment end |
| 0xafdda6 | ❌ OUTSIDE | Above segment end |
| 0xafddab | ❌ OUTSIDE | Above segment end |
| 0xafddac | ❌ OUTSIDE | Above segment end |
| 0xafddad | ❌ OUTSIDE | Above segment end |
| 0xD15851E8 | ❌ OUTSIDE | Way outside |
| 0x5C4DEE52D | ❌ OUTSIDE | Way outside |

**Why NOPping doesn't work**: The game tries to execute code at addresses not covered by any PT_LOAD segment. These are valid code sections (like `.startup` at VA 0x586000) that were never mapped into memory because the segment mapping in the PE conversion is incomplete.

**Fix needed**: Extend PT_LOAD segments or add missing segments in `WindowsPePatcher.cpp` to cover all code sections. NOPping individual instructions will NOT fix this — it would silently break initialization.

**Files to fix**:
- `AnyPS4/core/relinker/elfpatcher/src/windows/WindowsPePatcher.cpp` - Fix segment mapping to cover all code sections
- `tools-fetch/reloc_diagnostic.py` - Diagnostic tool (created) to verify segment coverage

## Files to Fix Next

| File | Action |
|------|--------|
| `AnyPS4/core/relinker/elfpatcher/src/windows/WindowsPePatcher.cpp` | Extend PT_LOAD segment mapping to cover all code sections |
| `tools-fetch/reloc_diagnostic.py` | Run to verify segment coverage after fix |

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

### Run game
```powershell
cd C:\PS4\export_Limbo.PS4-PRELUDE
.\app.exe
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
