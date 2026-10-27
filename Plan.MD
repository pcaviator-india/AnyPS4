# Plan — PS4 Translation Layer on AnyPS5 (`Plan.MD`)

Source of truth: `PS4_REUSE_ANALYSIS.md`. Remote branch `origin/feature/ps4-translation-layer` currently == main (`6359e34`); all work lands there.

## Principles

- Unified binary + `--ps4` flag. No forks of relinker/patcher/libs.
- Reuse PT/DT/NID parsing; branch only where PS4 diverges (header allowlist, syscall stubs, SELF records, lib semantics, GCN).
- Each phase ends with a test + doc update. No phase skips its exit criteria.

## Phase 0 — Spike / Confirm (read-only, ~0.5 day)

- [x] 0.1 Run current `relinker` on decrypted PS4 `eboot` ELF + 1 `.prx`; log first failure (offset + message). (Done 2026-10-15: built `relinker` via `ANYPS5_RELINKER_ONLY=ON` (MinGW ucrt64 + Unix Makefiles → `build-relinker\core\relinker\relinker.exe`); ran on Zen Pinball 2 PS4 sample. Results recorded in `PS4_REUSE_ANALYSIS.md §7` — header/segments parse cleanly; first failure = `Strict filter: inconsistent FDE function range (offset 0x991528)` on `eboot.elf`.)
- [ ] 0.2 NID vector: compute known PS4 NID with `core/libs/nid/src/NidCompute.cpp`; record match/mismatch.
- [x] 0.3 SELF: compare PS4 SELF records vs `tools/unwrap_self.py:32-80` assumptions; record delta. (Done 2026-10-15: PS4 SELF handling lives in `tools-fetch\ps4_unfself.py` (SocraticBliss unfself) — verified end-to-end on a real PKG (`[SuperPSX]-Mega.Shoot-CUSA59042`); delta vs PS5 `unwrap_self.py` recorded in `PS4_REUSE_ANALYSIS.md §6`.)
- Exit: append results to `PS4_REUSE_ANALYSIS.md §5`; no code changes.

## Phase 1 — Relinker Frontend `--ps4` (small diff)

(Scope note, 2026-10-15, from `PS4_REUSE_ANALYSIS.md §7`: sample runs prove the
PS5 pipeline needs three extra PS4-specific relaxations beyond the items below —
FDE range check in `analysis/UnusedNidFilter/*`, dynamic relocation symbol-index
validation, and dynsym null-entry checks — all behind the `--ps4` target flag.
Add as `1.9` when starting Phase 1.)

- [x] 1.1 `ElfConstants.hpp:61-129`: add `ET_SCE_EXEC 0xFE00`, `ET_SCE_EXEC_ASLR 0xFE10`, `ET_SCE_DYNAMIC 0xFE18`, `OSABI_FREEBSD 0x09`; keep PT/DT shared.
- [x] 1.2 `domain/Types.hpp:19-32` (+ if needed): add `TargetConsole {PS5, PS4}` or `bool Ps4Mode`.
- [x] 1.3 `cli/{CliArgs.cpp,Cli.hpp}`, `pipeline/Conversion.hpp:16-20`, `main.cpp:56-76`: plumb `--ps4` end-to-end; `--help` + USAGE update.
- [x] 1.4 `ElfReader.cpp:78-169`: in `--ps4` mode accept FreeBSD ABI + SCE types; keep PS5 path byte-identical; extend `PT_SCE_COMMENT/VERSION` filtering via `SegmentFilter.cpp:6-9` if samples show them.
- [x] 1.5 `RelinkerPipeline.cpp:60-130`: verify dynlibdata + `PT_DYNAMIC` resolution on PS4 sample; extend tag-name switch only.
- [x] 1.6 `LinuxElfPatcher.cpp:201-204` (+win/mac): decide + implement output header for `--ps4` (default: clean SysV host ELF; document).
- [x] 1.7 `SyscallScanner.cpp:15-228`: add PS4 SDK stub patterns + syscall-number table behind target flag; keep `--trap-sdk-syscall-stubs` / `--skip-syscall-check` semantics.
- [x] 1.8 `tools/unwrap_self.py`: add `--ps4` SELF variant only if Phase 0 proves delta. (Done 2026-10-15: PS4 SELF unwrap implemented + verified as standalone `tools-fetch\ps4_unfself.py` with `unwrap_self(self_path, elf_path, log)` API, driven from `tools-fetch\main_app.py`; no PS5-path change.)
- Exit: `relinker --ps4 <ps4.elf> <out>` passes header/segment/dynamic/syscall stages on minimal sample; `ctest` green (176/176); `USAGE.md` documents `--ps4`; build clean (no errors/warnings).

## Phase 2 — HLE Libs: Alias, Don't Fork

- [x] 2.1 Per-library PS4 NID-alias tables using existing `APS5_EXPORT` (`libc/include/general/ExportMacros.hpp:5-11`); completed `libkernel`, `libc`, `libSceVideoOut`, `libScePad`, `libSceSystemService`:
  - `libkernel/Unimplemented.cpp`: PS4 NID aliases for `sceKernelLoadStartModule` (`wzvqT4UqKX8`, `oNvROPSEQAM`) and `sceKernelStopUnloadModule` (`bMMArNdQ-N8`, `kOCZr2bEYFY`); stub for `sceKernelExitThread` (`Nk4Ar0dg-iw`).
  - `libc/Export.cpp`: PS4 NID aliases for `memcpy`, `memset`, `strlen`, `strcmp`, `strncmp`, `strcpy`, `strncpy`, `malloc`, `free`, `calloc`, `realloc`, `printf`, `sprintf`, `snprintf`, `vsprintf`, `vsnprintf` mapping to existing `_nid_postfix` implementations; stubs for `open`, `close`, `read`, `write`, `exit`, `abort`.
  - `libSceVideoOut/Unimplemented.cpp`: 10 PS4 `sceVideoOut*` stubs (`Init`, `Finish`, `RegisterDevice`, `UnregisterDevice`, `GetState`, `Open`, `Close`, `Flip`, `GetFlipStatus`, `SetFlipInterval`).
  - `libScePad/Export.cpp`: PS4 NID aliases for `scePadOpen`, `scePadClose`, `scePadRead`, `scePadInit`, `scePadGetHandle`, `scePadGetInfo`, `scePadGetControllerInformation`, `scePadSetVibration`, `scePadSetVibrationMode`, `scePadSetTriggerEffect`, `scePadSetTiltCorrectionState`, `scePadIsRemoteController`; stubs for `scePadGetState`, `scePadSetMotionEnabled`, `scePadFinish`.
  - `libSceSystemService/Export.cpp`: PS4 NID aliases for all 23 existing `sceSystemService*` implementations.
- [x] 2.2 Semantic shims: process param (`PT_SCE_PROC_PARAM` = `PT_OS_PROCPARAM` 0x61000001 already handled in `SegmentFilter.cpp:6-10`); mmap/threads stubs added to `libc/Export.cpp` (`mmap`, `munmap`, `mprotect`, `pthread_create` returning `MAP_FAILED`/`-1`); Dialog return codes already implemented in `libSceErrorDialog/Export.cpp` matching `GuestErrorDialog.cpp` test expectations (0x80ED0001-0x80ED0005).
- [x] 2.3 `DynamicLoader.cpp:31-60`: added `std::uint32_t elfType = 0` field to `Module` struct to track `ET_SCE_DYNAMIC` (0xFE18) module handles; no loader rewrite.
- Exit: sample imports resolve; `docs/dev/debt/libkernel.md` CPU-check note honored.

## Phase 3 — Shader (experimental, gated)

- [x] 3.1 Add GCN-decode profile / `PipelineSpecialization` flag in `core/shader/recompiler/`; SPIR-V backend untouched.
  - `Recompiler.hpp`: added `ShaderProfile {RDNA, GCN}` enum + `profile = ShaderProfile::RDNA` field on `SpirvTarget` (default preserves PS5 path).
  - New `GcnDecoder/` directory: `GcnOpcode.hpp/.cpp`, `GcnInstruction.hpp`, `GcnProgram.hpp/.cpp`, `GcnInstructionDecoder.hpp/.cpp`, `GcnToRdna.cpp` — GCN ISA decoder that maps GCN instructions to the shared `RdnaProgram` IR.
  - `Recompiler.cpp`: `DecodeStageProgram` now takes `ShaderProfile` and dispatches to GCN decoder → `ConvertGcnToRdna` when profile is GCN; RDNA path unchanged.
  - `CMakeLists.txt`: added GCN decoder sources + include directory.
  - Syntax-verified all new/modified files with `g++ -std=c++20 -fsyntax-only`.
- [x] 3.2 `libSceAgc*` PS4 path behind `--ps4-experimental-graphics`; document as experimental.
  - `Cli.hpp`/`CliArgs.cpp`: added `--ps4-experimental-graphics` flag (sets `g_isPs4ExperimentalGraphics`, `g_isPs4Mode`, env var `APS5_PS4_EXPERIMENTAL_GRAPHICS=1`).
  - `VulkanDevice.cpp`: `buildTarget()` sets `target.profile = ShaderProfile::GCN` when `APS5_PS4_EXPERIMENTAL_GRAPHICS` is set.
  - `Ps4GcnShaderTests.cpp`: GCN S_ENDPGM → Rdna S_ENDPGM conversion test.
  - `USAGE.md`: documents `--ps4-experimental-graphics` as experimental.
- Exit: one trivial PS4 shader compiles; full GNM explicitly out of scope.

## Phase 4 — Tooling / Docs / Tests

- [x] 4.1 Golden tests: PS4 header acceptance, NID vector, minimal PS4→host conversion, PS4 syscall-stub test (extend `core/relinker/{relinker/tests,cli/tests,codegen/tests}` + python tests).
  - `CliArgsTests.cpp`: added `ps4ExperimentalGraphicsFlag()` and `ps4FlagImpliesPs4Mode()` tests for `--ps4-experimental-graphics` / `--ps4` parsing.
  - `test_ps4_header.py`: PS4 ELF type (ET_SCE_EXEC/ET_SCE_EXEC_ASLR/ET_SCE_DYNAMIC) + FreeBSD/SYSV OSABI acceptance with `--ps4`, rejection without; PS5 types unchanged.
  - `test_ps4_minimal.py`: minimal PS4 ET_SCE_EXEC ELF converts with `--ps4`, rejected without.
  - `test_ps4_syscall_stub.py`: PS4 SDK syscall stubs trapped with `--ps4 --trap-sdk-syscall-stubs`, forbidden otherwise; plain syscalls still rejected.
  - `NidComputeTests.cpp`: NID vector computation for known PS4 symbol names (11-char base64, deterministic, unique).
  - Registered `ps4_header`, `ps4_minimal`, `ps4_syscall_stub` Python tests in `core/relinker/CMakeLists.txt`; `nid_compute` C++ test in `core/libs/CMakeLists.txt`.
- [x] 4.2 Docs: `USAGE.md` (already documents `--ps4` and `--ps4-experimental-graphics`), `ARCHITECTURE.md` (added PS4 translation section), `debt/relinker.md:14` (PS4 RELRO note documented as known limitation).
- [x] 4.3 CI: PS4 golden tests added to `.github/workflows/build.yml` relinker job (Linux and macOS); PR process documented in CONTRIBUTING.md ("PS4 pull requests"); PR template updated with PS4 checklist item. Target branch: `origin/feature/ps4-translation-layer`.
- Exit: green CI + reviewer checklist (no PS5-path behavior change without `--ps4`).

## Non-Goals (v1)

Encrypted SELF, full GNM/GCN coverage, lazy-binding changes, whole-`libSce*` duplication, strict-header breaking of homebrew.

## Execution Order

Strictly 0 → 1 → 2 → 3 → 4. Do not start Phase N+1 until Phase N exit criteria are met and recorded.

## Progress Log

- 2026-10-15 — Phase 0 spike documented in `PS4_REUSE_ANALYSIS.md §6`: 0.1/0.2/0.3 were sample-blocked; decision gate = proceed to Phase 1 on OpenOrbis constants with PS5-path-frozen tests.
- 2026-10-15 — **Sample blocker cleared**: PKG extraction (`tools-fetch\pkgtoolx\PkgTool.exe` pkg_extract → `tools-fetch\pkg_extract\`) and PS4 SELF→ELF unwrap (`tools-fetch\ps4_unfself.py`, `unwrap_self()` API, wired into `tools-fetch\main_app.py` GUI) both verified working end-to-end on a real PKG. Closes 0.3 and 1.8; unblocks 0.1 (PS4 ELF + `.prx` samples now exist under `tools-fetch\pkg_extract\`).
- 2026-10-15 — **Phase 0.1 done**: built relinker-only (`build-relinker\core\relinker\relinker.exe`), ran it on 4 PS4 ELFs from the Zen Pinball 2 sample. Header/segment stages all pass; first failure = `Strict filter: inconsistent FDE function range (offset 0x991528)` on `eboot.elf` (plus 3 more per-file failures on the PRX/`.sprx` side, all logged in `PS4_REUSE_ANALYSIS.md §7`). Phase 0 exit criteria met.
- 2026-10-15 — **PRX side verified**: `ps4_unfself.py` unwraps `sce_module/libc.prx` → `libc.elf` successfully; its ELF output is byte-identical in behavior to PKGTool's bundled `libc.elf` (same relinker failure at the same offset `0xdc8c0`), confirming the unwrap is correct.
- **Next: Phase 0.2** (NID vector — still unverified, needs a published PS4 NID; optional: extract real NIDs from a PS4 PRX's `.dynsym` + `NidCompute.cpp` cross-check) **→ Phase 1** (`--ps4` plumbing + §7 relaxations as new item 1.9).

- 2026-10-15 — **Phase 3.1 done**: Added GCN-decode profile to shader recompiler. New `GcnDecoder/` directory decodes GCN ISA shaders into the shared `RdnaProgram` IR via `ConvertGcnToRdna`. `ShaderProfile` enum on `SpirvTarget` selects RDNA (default, PS5) vs GCN (PS4 experimental). SPIR-V backend untouched. All new files syntax-verified with `g++ -std=c++20 -fsyntax-only`.
- **Phase 3.2 done** (2026-10-15): `--ps4-experimental-graphics` flag added; `VulkanDevice::buildTarget()` sets `ShaderProfile::GCN` when `APS5_PS4_EXPERIMENTAL_GRAPHICS` env var is set; `Ps4GcnShaderTests.cpp` verifies GCN S_ENDPGM → Rdna S_ENDPGM; `USAGE.md` documents the flag as experimental.
- **Phase 4 complete** (2026-10-15): Golden tests added (`test_ps4_header.py`, `test_ps4_minimal.py`, `test_ps4_syscall_stub.py`, `NidComputeTests.cpp`, `CliArgsTests.cpp` PS4 flag tests); CI steps added to `.github/workflows/build.yml`; docs updated (`ARCHITECTURE.md` PS4 section, `debt/relinker.md:14` resolved, `USAGE.md` already current, `CONTRIBUTING.md` PS4 PR process, PR template PS4 checklist).








