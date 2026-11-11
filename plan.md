# AnyPS4 Porting Toolchain — Phase 2 Implementation Plan

## Goal

Enable `Limbo.PS4-PRELUDE` to execute successfully past ELF entry point transfer, load game assets, and run properly on Windows.

## Current State — GAME REACHES ELF ENTRY POINT ✅

The game now successfully:
- Transfers control to ELF entry point (`Transferring control to ELF entry point`)
- Loads all 128 PRXs from `libs/` (all valid Windows PE DLLs)
- Resolves imports by scanning PRX export tables
- Begins executing ELF code

## Root Causes Identified & Status

### 1. Fake VTable / Lazy Stubs Displacement Calculation Bug (Fixed)
**Status**: [x] Completed.

### 2. Broken Vectored Exception Handler ABI & Return Value (Fixed)
**Status**: [x] Completed.

### 3. Heap Allocator Verification Rejection (Fixed)
**Status**: [x] Completed.

### 4. Broken Libkernel PRX / Libc Symbol Compatibility (Fixed)
**Status**: [x] Completed.

### 5. All 128 PRXs Converted to Windows PE DLLs (Fixed)
**Status**: [x] Completed.
- Previously 16 stub PRXs with 0-4 exports
- Now all 128 PRXs have full export tables (137,316 total exports)
- Key fixes: `libSceSsl.prx` (0→28 exports), `libSceAudioIn.prx` (0→8 exports)

### 6. PRX Inventory & Gap Analysis GUI Tabs (Fixed)
**Status**: [x] Completed.
- PRX Inventory tab: Scan libs directory, see each PRX status
- PRX Gap Analysis tab: Compare needed vs converted PRXs

### 7. Crash After ELF Entry Point — ROOT CAUSE FOUND (Fix in progress)

**Status**: [ ] Root cause identified, fix in progress.

**Crash symptoms**:
```
Access violation write at 0x0000000000000020
Access violation write at 0x00000000ffffff88
Access violation read at 0x00000000000001e7
Access violation read at 0x00000005c4dee52d
```

**Root cause**: The ELF has only TWO PT_LOAD segments:
- Segment 1: `vaddr=0x0, memsz=0x4e6f88` (RX) - covers 0x0 to 0x4e6f88
- Segment 2: `vaddr=0x4e8000, memsz=0x87a00` (RW) - covers 0x4e8000 to 0x56fa00

**ALL crash addresses are OUTSIDE these segments:**
- 0x60f4c0, 0xaf31c7, 0xafdda6, 0xafddab, 0xafddac, 0xafddad — all ABOVE 0x56fa00
- 0xD15851E8, 0x5C4DEE52D — way outside

**Why NOPping doesn't work**: The game tries to execute code at addresses not covered by any PT_LOAD segment. These are valid code sections (like `.startup` at VA 0x586000) that were never mapped into memory because the segment mapping in the PE conversion is incomplete. NOPping individual instructions would silently break initialization without fixing the root cause.

**Fix needed**: Extend PT_LOAD segments or add missing segments in `WindowsPePatcher.cpp` to cover all code sections above 0x56fa00.

**Action items**:
1. Extend PT_LOAD segment mapping in `WindowsPePatcher.cpp` to cover all code sections
2. Run `tools-fetch/reloc_diagnostic.py` to verify segment coverage after fix
3. Re-test game execution

## Next Steps (Priority Order)

1. [ ] Fix PT_LOAD segment mapping in `WindowsPePatcher.cpp` to cover all code sections
2. [ ] Run `tools-fetch/reloc_diagnostic.py` to verify all addresses are inside segments
3. [ ] Re-test game execution — should progress past entry point crashes
4. [ ] Investigate subsequent runtime milestones (asset loading, file I/O, graphics init)

## Files

### Core C++
- `AnyPS4/core/relinker/elfpatcher/src/windows/WindowsEntryStubBuilder.cpp` — VEH handler, entry point transfer
- `AnyPS4/core/relinker/elfpatcher/src/windows/WindowsPePatcher.cpp` — Runtime PRX loading from libs/
- `AnyPS4/core/libs/prx/libc/preserve_exports.txt` — C++ mangled export preservation
- `AnyPS4/core/libs/prx/libSceSsl/Export.cpp` — SSL/TLS implementation (mbedTLS)
- `AnyPS4/core/libs/prx/libSceAudioIn/Export.cpp` — Audio input implementation

### Python Tools
- `tools-fetch/main_app.py` — GUI pipeline with PRX Inventory & Gap Analysis tabs
- `tools-fetch/prx_inventory.py` — PRX scanning and classification
- `tools-fetch/prx_gap_analysis.py` — Gap analysis between needed vs converted
- `tools-fetch/gen_stub_exports.py` — Generate APS5_EXPORT C++ code for stub PRXs
- `tools-fetch/nop_crash.py` — NOP out crash instructions in PE
- `tools-fetch/patch_sse4a.py` — Pre-patch SSE4A instructions in ELF
- `tools-fetch/phase2_stubs.py` — Phase 2 NotImplemented stub DLL builder

### Documentation
- `README.md` — Project overview and accomplishments
- `plan.md` — This file

## Build & Test Commands

```powershell
# Build relinker
cd C:\PersonalProjects\AnyPs4\AnyPs4\build-full
cmake --build . --target relinker

# Relink Limbo ELF
cd C:\PersonalProjects\AnyPs4\AnyPs4\build-full\core\relinker
.\relinker.exe --ps4 --lazy-binding --skip-sce-module --windows 'C:\PS4\export_Limbo.elf' 'C:\PS4\export_Limbo.PS4-PRELUDE\app.exe'

# Run game
cd C:\PS4\export_Limbo.PS4-PRELUDE
.\app.exe

# Run with trace
cd C:\PersonalProjects\AnyPs4\tools-fetch
python trace_app.py 'C:\PS4\export_Limbo.PS4-PRELUDE\app.exe' 'C:\PS4\export_Limbo.PS4-PRELUDE'

# Check PRX status
python main_app.py  # → PRX Inventory tab
```
