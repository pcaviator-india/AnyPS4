"""Check that --ps4 accepts PS4 ELF types (ET_SCE_EXEC/ET_SCE_EXEC_ASLR/ET_SCE_DYNAMIC)
with FreeBSD or SYSV OSABI, and rejects them without --ps4; PS5 types still work."""

from pathlib import Path
import struct
import subprocess
import sys
import tempfile

ET_EXEC = 2
ET_DYN = 3
ET_SCE_EXEC = 0xFE00
ET_SCE_EXEC_ASLR = 0xFE10
ET_SCE_DYNAMIC = 0xFE18
ELFOSABI_SYSV = 0
ELFOSABI_FREEBSD = 0x09
PT_LOAD = 1
PT_DYNAMIC = 2
PT_SCE_VERSION = 0x6FFFFF01


def fixture(e_type, os_abi, size=0x3000):
    """A minimal ELF64 x86-64 image with one PT_LOAD and one PT_DYNAMIC."""
    image = bytearray(size)
    image[:16] = b"\x7fELF\x02\x01\x01" + bytes(9)
    headers = [
        (PT_LOAD, 5, 0x1000, 0x1000, 0x2000, 0x2000, 0x1000),
        (PT_DYNAMIC, 6, 0x2400, 0x2400, 128, 128, 8),
        (PT_SCE_VERSION, 0, 0, 0, 0, 0, 1),
    ]
    struct.pack_into("<HHIQQQIHHHHHH", image, 16,
                     3, 62, 1, 0x1000, 64, 0, 0, 64, 56, len(headers), 64, 0, 0)
    for index, (kind, flags, offset, vaddr, filesz, memsz, align) in enumerate(headers):
        struct.pack_into("<IIQQQQQQ", image, 64 + index * 56,
                         kind, flags, offset, vaddr, vaddr, filesz, memsz, align)
    struct.pack_into("<H", image, 0x10, e_type)
    struct.pack_into("<B", image, 0x07, os_abi)
    image[0x1000:0x1001] = b"\xcc"
    for index, tag in enumerate([(5, 0x2600), (10, 1), (6, 0x2620), (11, 24),
                                  (7, 0x2700), (8, 0), (9, 24), (0, 0)]):
        struct.pack_into("<qQ", image, 0x2400 + index * 16, *tag)
    return image


def relink(relinker, work, name, image, options):
    source = work / f"{name}.elf"
    output = work / f"{name}.out"
    source.write_bytes(image)
    result = subprocess.run([str(relinker), "--skip-sce-module", *options, str(source), str(output)],
                            capture_output=True, text=True, timeout=20)
    return result, output


def main():
    relinker = Path(sys.argv[1]).resolve()
    with tempfile.TemporaryDirectory(prefix="anyps5-ps4-header-") as directory:
        work = Path(directory)

        # PS4 types with FreeBSD OSABI: accepted with --ps4, rejected without.
        for e_type, name in ((ET_SCE_EXEC, "sce_exec"),
                             (ET_SCE_EXEC_ASLR, "sce_exec_aslr"),
                             (ET_SCE_DYNAMIC, "sce_dynamic")):
            image = fixture(e_type, ELFOSABI_FREEBSD)
            result, output = relink(relinker, work, f"accept-{name}", image, ["--ps4"])
            assert result.returncode == 0, (name, "with --ps4", result.stdout, result.stderr)

            result, _ = relink(relinker, work, f"reject-{name}", image, [])
            assert result.returncode == 2, (name, "without --ps4 should fail", result.returncode, result.stderr)
            assert "Unsupported ELF type for PS4" in result.stderr or \
                   "Unsupported ELF OSABI for PS4" in result.stderr, \
                (name, "without --ps4 wrong error", result.stderr)

        # PS4 types with SYSV OSABI: also accepted with --ps4.
        for e_type, name in ((ET_SCE_EXEC, "sce_exec_sysv"),
                             (ET_SCE_EXEC_ASLR, "sce_exec_aslr_sysv"),
                             (ET_SCE_DYNAMIC, "sce_dynamic_sysv")):
            image = fixture(e_type, ELFOSABI_SYSV)
            result, output = relink(relinker, work, name, image, ["--ps4"])
            assert result.returncode == 0, (name, "with --ps4 SYSV", result.stdout, result.stderr)

        # PS5 types with SYSV OSABI: accepted with and without --ps4.
        for e_type, name in ((ET_EXEC, "exec"), (ET_DYN, "dyn")):
            image = fixture(e_type, ELFOSABI_SYSV)
            result, output = relink(relinker, work, f"ps5-{name}", image, ["--ps4"])
            assert result.returncode == 0, (name, "PS5 with --ps4", result.stdout, result.stderr)
            result, output = relink(relinker, work, f"ps5-{name}-plain", image, [])
            assert result.returncode == 0, (name, "PS5 without --ps4", result.stdout, result.stderr)

        # PS5 types with FreeBSD OSABI: rejected without --ps4, accepted with --ps4.
        image = fixture(ET_EXEC, ELFOSABI_FREEBSD)
        result, output = relink(relinker, work, "ps5-freebsd-ps4", image, ["--ps4"])
        assert result.returncode == 0, ("PS5 FreeBSD with --ps4", result.stdout, result.stderr)
        result, _ = relink(relinker, work, "ps5-freebsd-plain", image, [])
        assert result.returncode == 2, ("PS5 FreeBSD without --ps4 should fail",
                                        result.returncode, result.stderr)

    print("PS4 header acceptance tests passed")


if __name__ == "__main__":
    main()