# AnyPS4 Porting Toolchain — Phase 2 Implementation Plan

## Goal

Implement Phase 2 of the AnyPS4 porting toolchain: generate minimal NotImplemented
stub PE DLLs for unresolved ELF imports so the game no longer crashes with
"FAIL: unresolved ELF import" after all PRX stubs are deployed.

## Root Cause Analysis

The NID patcher (`nid_patcher.exe`) cannot patch `app.exe` because:
- `app.exe`'s PE import table contains **only `KERNEL32.dll`** — no PS4 library imports
- PS4 imports are stored in a custom ELF-derived format (`.elf0` section), not the PE import table
- The NID patcher expects PE import table entries for PS4 libraries, which don't exist

## Recommended Approach (Option 2 — matching AnyPS5)

AnyPS5 uses: **"OS loader binds imports by NID"** — the native OS dynamic linker resolves
imports by matching NID-named symbols in loaded PRXs. No per-game NID patching needed.

For AnyPS4, this means:
1. **PS4 runtime loads ALL PRXs from `libs/` at startup** (not just those in the import table)
2. **Runtime resolves imports by scanning loaded PRXs' export tables** (by NID name)
3. **Phase 2 stubs** (`unresolved_imports.prx`) export missing NIDs as `ret 0` thunks
4. No NID patcher needed — the OS loader handles binding

## Implementation Steps

### Step 1: Phase 2 Stub Builder ✅ COMPLETE
- File: `tools-fetch/phase2_stubs.py`
- Functions: `pe_imports()`, `prx_export_names()`, `build_notimplemented_stub_dll()`, `find_unresolved_imports()`, `create_missing_prx_stubs()`
- Reads `missing.txt` for unresolved import names
- Builds valid PE DLLs with non-overlapping sections, correct export directory

### Step 2: Wire Phase 2 into Pipeline ✅ COMPLETE
- File: `tools-fetch/main_app.py`
- Import: `from phase2_stubs import create_missing_prx_stubs`
- `--no-gui` mode: calls `run_nid_and_phase2()` after copying PRX stubs
- `run_nid_and_phase2()`: Phase 2 runs BEFORE NID patching (so new stubs exist before patching)

### Step 3: Remove NID Patcher Step (CANNOT WORK)
- The NID patcher (`nid_patcher.exe`) cannot patch `app.exe` because app.exe's PE import table
  only contains `KERNEL32.dll`, not PS4 library imports
- **Remove NID patching from pipeline** — it never worked for this app.exe
- Phase 2 stubs alone are sufficient IF the runtime loads all PRXs from `libs/`

### Step 4: Runtime Change — Load All PRXs from `libs/` (C++ — NOT in tools-fetch) ✅ COMPLETE
- **File**: `AnyPS4/core/relinker/elfpatcher/src/windows/WindowsPePatcher.cpp`
- **Change**: After `libraries` is built from the ELF dynamic section (line 89), scan `runPath/libs/`
  for all `.prx` files not already in `libraries` and add them
- **WindowsEntryStubBuilder.cpp** automatically loads all libraries in `libraries` via `LoadLibraryExW`
  (lines 482-562) and resolves imports by scanning their export tables via `GetProcAddress` (lines 579-646)
- This makes Phase 2 stubs (and any future stubs) automatically available for import resolution
- **No changes to WindowsEntryStubBuilder.cpp needed** — the `libraries` vector already drives loading

### Step 5: Verification (PENDING — requires C++ rebuild)
- Re-build `WindowsPePatcher` with the libs/ scanning change
- Re-run packaging pipeline with CUSA59042 (Mega.Shoot) export
- Verify `unresolved_imports.prx` is created in `libs/` (714 exports)
- Run game — should progress past "FAIL: unresolved ELF import bzQExy189ZI"
- Any remaining unresolved imports will error out, guiding further stub coverage

## Files
- **tools-fetch/phase2_stubs.py** — Phase 2 stub builder (COMPLETE)
- **tools-fetch/main_app.py** — Pipeline integration (COMPLETE, NID patcher step removed)
- **AnyPS4/core/relinker/elfpatcher/src/windows/WindowsPePatcher.cpp** — Runtime change (COMPLETE — libs/ scanning added)
- **AnyPS4/core/relinker/elfpatcher/include/elfpatcher/windows/WindowsEntryStubBuilder.hpp** — No change needed
- **AnyPS4/core/relinker/elfpatcher/src/windows/WindowsEntryStubBuilder.cpp** — No change needed

## Key Insight
AnyPS5 uses "OS loader binds imports by NID" — the native OS dynamic linker resolves imports
by matching NID-named symbols in loaded PRXs. AnyPS4 should do the same on Windows: load ALL
PRXs from `libs/` at startup, then let the OS loader bind imports by NID name matching.
No NID patcher needed.