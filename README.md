# About

Tool for automatic executables porting to Linux and Windows.

[**Web converter**](https://boykopovar.github.io/AnyPS5/) - files stay on your device.

![anyps5_collage1](https://github.com/user-attachments/assets/ed2f0b2d-33d3-46d7-ab88-767ca872fc99)

Includes a [relinker](core/relinker) that converts executable to the target system's native format and implementations of [system prx libraries](core/libs/prx) suitable for dynamic linking. No emulation or separate runtime process.

[**Discord**](https://discord.gg/BHFztBPUe), [Usage](docs/user/USAGE.md), [Build instructions](docs/dev/BUILD.md), [Architecture](docs/dev/ARCHITECTURE.md), [Technical debt of the project](docs/dev/TechnicalDebt.md), [code style conventions](docs/dev/CONVENTIONS.md), [contributing](CONTRIBUTING.md)

## Status

[![libraries](https://boykopovar.github.io/AnyPS5/badge-libraries.svg)](https://boykopovar.github.io/AnyPS5/progress.html) [![shaders](https://boykopovar.github.io/AnyPS5/badge-shaders.svg)](https://boykopovar.github.io/AnyPS5/progress.html)

[![progress map](https://boykopovar.github.io/AnyPS5/progress.svg)](https://boykopovar.github.io/AnyPS5/progress.html)

[Progress history](https://boykopovar.github.io/AnyPS5/history.html)

<sub>* System libraries: percentage of the functions known to the project so far (declared in [core/libs/prx](core/libs/prx)), not of every PS5 system function. The total grows as more functions are declared.</sub>

Unsupported or unexpected states strictly throw `std::runtime_error`. `what()` is printed to stderr and the process terminates.

The [shader recompiler](core/shader/recompiler/Recompiler.cpp) successfully produces SPIR-V (validated via [Spirv-Tools](3rdparty/SPIRV-Tools) when built with `ANYPS5_ENABLE_SPIRV_TOOLS`).

## Compatibility

Per-game progress (stage reached, open blockers, libraries and GPU coverage) is tracked on the [blocker map](https://alxcbtw.github.io/anyps5-roadmap/), a community project built from public GitHub data ([source](https://github.com/AlxcBTW/anyps5-roadmap)). Test reports go in the [Game bring-up](https://github.com/boykopovar/AnyPS5/discussions/categories/game-bring-up) discussions, one thread per title.

## Input mapping

SDL-mapped game controllers are supported, including analog sticks and triggers. Keyboard and mouse controls can be configured with an `anyps5-input.ini` file. See [input mapping](docs/user/INPUT_MAPPING.md) for the supported devices and configuration format.

## Windows Porting — Current Debugging State

### What we intend
The [Windows ELF-to-PE relinker](core/relinker/elfpatcher/src/windows/) converts PS4 ELF64 x86-64 executables into native Windows PE32+ binaries. The entry stub (`WindowsEntryStubBuilder.cpp`) performs:

1. Early diagnostic logging via `OutputDebugStringA` (visible in DebugView when run as Administrator)
2. Path handling: `GetModuleFileNameW`, path copy, directory separator search, `SetCurrentDirectoryW`
3. PRX library loading via `LoadLibraryExW` from `libs/` directory
4. Import resolution via `GetProcAddress` for all ELF imports
5. Argument processing: `GetCommandLineW`, `WideCharToMultiByte`, `VirtualAlloc`
6. Vectored Exception Handler (VEH) installation before control transfer
7. Transfer control to the ELF entry point via `call entryRva`

### What works (verified via DebugView)
All stub logging messages appear in order, confirming correct execution through the entire entry stub:

```
ELF entry stub started
GetEnvVar called
GetModFileName called
GetModFileName ret
Path copy done
After requireNonzero
Buffer overflow
About to copy path
Path copied
Before SetCurDir
After SetCurDir
Loading PRXs
PRXs loaded
Resolving imports
Imports resolved
About to transfer to ELF entry point
```

### What we are up to
Debugging a crash that occurs **after** `About to transfer to ELF entry point`, i.e., inside ELF code itself — not in the stub.

### What is pending / the problem
The ELF entry point crashes immediately with `0xC0000005` (access violation) reading a PS4 virtual address that was never relocated to a Windows address:

```
FATAL: unhandled exception 0xc0000005 on thread XXXX ''
  rip 0x0000000140224097 app.exe+0x224097
  read of 0x00000001c0b2e737
```

### Root cause
`WindowsRelocationBuilder.cpp` only processes `.rela`/`.rela.plt` relocations with **defined symbols** (type 1/`R_X86_64_64`, type 6/`R_X86_64_GLOB_DAT`). If `0x1c0b2e737` is:
- an absolute immediate embedded in an instruction (symbol index 0), or
- in a PT_LOAD segment not covered by any relocation entry,

then it remains as a raw PS4 virtual address and causes an access violation when dereferenced.

### Fix applied (commit `d9d60248b`)
- **`WindowsRelocationBuilder.cpp`**: Defined symbol relocations now compute the Windows-relocated address instead of throwing an error.
- **`WindowsEntryStubBuilder.cpp`**: Added VEH installation before `call entryRva` to catch and log crashes via `OutputDebugStringA` ("Exception in ELF entry stub").

### Remaining work
- Determine why `0x1c0b2e737` was not covered by any relocation entry
- Check if symbol index 0 relocations (absolute immediates) need handling
- Verify `GetRelocatedAddress()` maps all PT_LOAD segments correctly
- Add entry-point address + first 16 bytes logging to DebugView before transfer

## Disclaimer

This project is intended for interoperability, research, preservation, and compatibility purposes. It does not include, distribute, or require copyrighted software, firmware, cryptographic keys, or proprietary libraries. Users are responsible for ensuring that any binaries used with this project are obtained and used in accordance with applicable laws and their respective license terms.

## License

This project is licensed under the GNU General Public License version 2 only.
