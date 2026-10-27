# AnyPS5 → PS4 Translation Layer — Complete Understanding

Date: 2026-10-15. Repo: `c:\PersonalProjects\AnyPs4\AnyPS5`
(HEAD `6359e34`; main == origin/main == origin/feature/ps4-translation-layer.)

## 1. What AnyPS5 Is (verified in-tree)

- Relinker (`core/relinker/`): converts PS5 ELFs to host ELF/PE/Mach-O.
  Entry `core/relinker/main.cpp`; pipeline
  `core/relinker/relinker/src/pipeline/RelinkerPipeline.cpp`.
- HLE libs (`core/libs/prx/`, ~110 dirs): guest NID imports to native
  impls via `APS5_EXPORT` (`core/libs/prx/libc/include/general/ExportMacros.hpp:5-11`)
  + `DynamicLoader.cpp` (`core/libs/prx/libkernel/Module/src/DynamicLoader.cpp:1-60`).
- NID (`core/libs/nid/src/NidCompute.cpp`): SHA1(symbol + 16-byte suffix
  `51 8D 64 A6 35 DE D8 C1 E6 B0 39 B1 C3 E5 52 30`), reverse 8 bytes,
  base64 charset `A-Za-z0-9+-`, 11-char NID. Believed same as PS4 (verify by vector).
- Shader (`core/shader/recompiler/`): RDNA decoder to SPIR-V. PS4 = GCN:
  biggest ISA gap, deferred to Phase 3 behind a flag.
- Tools: `tools/unwrap_self.py:1-80` unwraps decrypted SELF/fSELF to ELF.
  Relinker skips SELF with warning (`docs/user/USAGE.md:11`).
- Docs: `README.md`, `docs/dev/ARCHITECTURE.md`, `docs/user/USAGE.md:1-80`,
  `docs/dev/debt/relinker.md:14` (PS4 RELRO note).

## 2. PS4 vs PS5 Format (spec vs in-tree constants)

Same numerics, reuse as-is:
- `PT_SCE_DYNLIBDATA 0x61000000`, `PT_SCE_PROC_PARAM 0x61000001`,
  `PT_SCE_RELRO 0x61000010` (`ElfConstants.hpp:76-78`).
- `DT_SCE_* 0x61000007..0x6100003F` == current `DT_OS_*`
  (`ElfConstants.hpp:94-129`).
- Uncovered-RELRO to RW-LOAD fallback exists (`ElfReader.cpp:147-166`).

Deltas, branch behind `--ps4` only:
- Header: PS4 `EI_OSABI=0x09` FreeBSD; `e_type ET_SCE_EXEC 0xFE00`,
  `ET_SCE_EXEC_ASLR 0xFE10` (default), `ET_SCE_DYNAMIC 0xFE18`.
  Current `ElfReader::ReadHeader` (`ElfReader.cpp:78-116`) checks
  magic/class/endian/version/machine/ehsize but never gates on
  Type/OsAbi — add constants + explicit allowlist.
- Syscalls: `0F 05` trapped; PS5-SDK stub bytes + mmap/mprotect inlines
  (`SyscallScanner.cpp:15-71`) need PS4-SDK variants + number table.
  Flags `--trap-sdk-syscall-stubs`, `--skip-syscall-check`
  (`CliArgs.cpp:58-60`, `USAGE.md:75-76`) keep semantics.
- SELF: `unwrap_self.py` PS5 record assumptions
  (`RECORD_OFFSET 0x40`, FIRST_REGION 0x400) need PS4 variant check.
- CPU: PS4 Jaguar needs fewer AMD-only rewrites than PS5 Zen2
  (`USAGE.md:44`); rewriter reuse.
- Graphics: PS4 GNM/GCN vs `libSceAgc*` + RDNA — experimental only.

## 3. Exact Touchpoints

- `core/relinker/elfpatcher/include/elfpatcher/general/ElfConstants.hpp:61-129`
- `core/relinker/relinker/src/parsing/ElfReader.cpp:78-169`
- `core/relinker/relinker/src/pipeline/RelinkerPipeline.cpp:60-130`
- `core/relinker/relinker/src/analysis/SyscallScanner.cpp:15-228`
- `core/relinker/elfpatcher/src/linux/LinuxElfPatcher.cpp:201-204` (+win/mac)
- `core/relinker/cli/{src/CliArgs.cpp,include/Cli.hpp}`,
  `relinker/include/relinker/pipeline/Conversion.hpp:16-20`, `main.cpp:56-76`
- `tools/unwrap_self.py:32-80`, `core/libs/nid/src/NidCompute.cpp:8-52`
- `core/libs/prx/*` aliases, `core/shader/recompiler/` GCN flag.

## 4. Rules

No pipeline/lib forks; no RDNA rewrite in v1; no encrypted SELF;
no lazy-binding changes; prefer `--ps4` allowlist over silent accept.

## 6. Phase 0 Results (2026-10-15, read-only spike)

- 0.1 PS4 sample run: BLOCKED. No *.elf/*.prx/*.self/*.bin samples
  found under `c:\PersonalProjects\AnyPs4` (recursive search empty).
  No code changes made. Needs a user-supplied decrypted PS4 ELF+PRX.
- 0.2 NID vector: UNVERIFIED (no published vector retrievable; wiki
  fetches returned chrome, no code). Local re-implementation of
  `NidCompute.cpp` in Python executes and yields stable 11-char NIDs
  (e.g. sceKernelWrite->4wSze92BhLI, malloc->gQX+4GDQjpM,
  sceVideoOutOpen->Up36PTk687E) but these are NOT confirmed against
  real PS4 values. Treat as unconfirmed.
- 0.3 SELF delta: UNVERIFIED (psdevwiki 403; no PS4 SELF sample).
  `unwrap_self.py` PS5 assumptions (`RECORD_OFFSET 0x40`,
  `FIRST_REGION 0x400`, size-matched record placement, entropy refusal)
  documented from code read (`tools/unwrap_self.py:32-187`).
- Incidental positive: `test_elf_header.py:17-19` already feeds a
  FreeBSD-OSABI (`byte 7 = 9`) fixture through the relinker expecting
  success, so the OSABI half of the header gap is already covered by
  tests; remaining header work is the `e_type` allowlist.
- Decision gate: proceed to Phase 1 on OpenOrbis constants
  (ET_SCE_EXEC 0xFE00 / ASLR 0xFE10 / DYNAMIC 0xFE18, OSABI 0x09)
  with PS5-path-frozen tests; live-sample + NID-vector validation
  deferred until samples/vectors supplied.

## 7. Phase 0.1 Results (2026-10-15, live PS4 sample spike)

- Build: `cmake -S . -B build-relinker -G "Unix Makefiles" -DANYPS5_RELINKER_ONLY=ON -DBUILD_TESTING=ON`
  with `C:/msys64/ucrt64/bin/{gcc,g++}` (no Ninja/GnuWin32-make quirks). Binary:
  `build-relinker/core/relinker/relinker.exe`. No code changes.
- Sample: `PS4_Zen_Pinball_2_CUSA00186` PKG → `tools-fetch/pkg_extract/<name>/uroot/`
  (Zen Pinball 2, CUSA00186). PKG extraction + SELF decryption already done by
  PkgTool (`.elf` files present alongside raw `.bin` SELFs).
- Header facts (confirmed on live sample): `eboot.elf` `e_type=0xFE00` (ET_SCE_EXEC),
  `libc.elf` `e_type=0xFE18` (ET_SCE_DYNAMIC), both `EI_OSABI=0x09` (FreeBSD),
  x86-64. Header allowlist constants in §2 match reality.
- Relinker passes header + program/section header stages on all PS4 samples (no
  rejection at `ElfReader`); first failure per input, all via `--windows --skip-sce-module`:
  - `uroot/eboot.elf` (EXEC): `FAIL: Strict filter: inconsistent FDE function range
    (offset 0x991528)` — same failure with `unused-filter=0/1/2`.
    → Blocker: `analysis/UnusedNidFilter` (EhFrameReader + StrictNidFilter).
  - `uroot/sce_module/libc.elf` (DYNAMIC): `FAIL: RELATIVE relocation has a
    nonzero symbol index (offset 0xdc8c0)`. → Blocker: relocation validation
    in dynlibdata/relocation path (R_X86_64_RELATIVE with non-zero st_info,
    possibly PS4 linkers emitting extra symbol indices).
  - `uroot/sce_module/libSceFios2.elf` (DYNAMIC): `FAIL: Unnamed import symbol
    is not a null symbol entry (offset 0x5a4f0)`. → Blocker: dynsym name check
    (PS4 allows unnamed/duplicate dynsym entries; relax under `--ps4`).
  - `uroot/sce_sys/about/right.elf` (small firmware module): `FAIL: Unterminated
    dynamic segment (offset 0x82f8)`. → Blocker: `ElfReader::ReadDynamicTags`
    requires `DT_NULL`; PS4 modules may end dynamic arrays differently or have
    a mis-sized segment — inspect `0x82f8` bytes before deciding.
- PRX side: `sce_module/libc.prx` / `libSceFios2.prx` are still SELF (magic
  `4f 15 3d 1d`); relinker rejects SELF at `ElfReader.cpp:84-86` ("The input is
  a SELF container, not an ELF") — expected; unwrap via `ps4_unfself.py` first
  (already verified). `.sprx`/`sce_discmap.plt` skipped (firmware-only).
- Implication for Phase 1 scope: in addition to the §1 items (constants,
  `--ps4` plumbing), PS4 needs targeted relaxations in
  `analysis/UnusedNidFilter/*` (FDE range), dynamic relocation validation, and
  dynsym null-entry checks. All behind the target flag; PS5 path stays frozen
  and ctest-gated.




