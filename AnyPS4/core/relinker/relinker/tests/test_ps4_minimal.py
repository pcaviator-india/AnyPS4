"""Minimal PS4-to-host conversion: a PS4 ET_SCE_EXEC ELF with FreeBSD ABI is relinked with --ps4."""

from pathlib import Path
import struct
import subprocess
import sys
import tempfile

ET_SCE_EXEC = 0xFE00
ELFOSABI_FREEBSD = 0x09
PT_LOAD = 1
PT_DYNAMIC = 2
PT_SCE_VERSION = 0x6FFFFF01


def fixture(size=0x3000):
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
    struct.pack_into("<H", image, 0x10, ET_SCE_EXEC)
    struct.pack_into("<B", image, 0x07, ELFOSABI_FREEBSD)
    # Entry point: a single int3 ret instruction at 0x1000.
    struct.pack_into("<Q", image, 0x18, 0x1000)
    image[0x1000] = 0xCC
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
    with tempfile.TemporaryDirectory(prefix="anyps5-ps4-minimal-") as directory:
        work = Path(directory)

        image = fixture()

        # With --ps4: should succeed.
        result, output = relink(relinker, work, "ps4", image, ["--ps4"])
        assert result.returncode == 0, ("PS4 minimal conversion with --ps4",
                                        result.returncode, result.stdout, result.stderr)
        assert output.exists(), "PS4 minimal conversion produced no output"
        data = output.read_bytes()
        assert data[:4] == b"\x7fELF", "output is not an ELF"

        # Without --ps4: should fail on the PS4 header.
        result, _ = relink(relinker, work, "ps4-no-flag", image, [])
        assert result.returncode == 2, ("PS4 minimal without --ps4 should fail",
                                        result.returncode, result.stderr)
        assert "Unsupported" in result.stderr, result.stderr

    print("PS4 minimal conversion tests passed")


if __name__ == "__main__":
    main()