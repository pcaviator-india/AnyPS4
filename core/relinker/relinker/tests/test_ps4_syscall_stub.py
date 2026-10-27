"""Check that --ps4 recognizes PS4 SDK syscall stubs and traps them with --trap-sdk-syscall-stubs."""

from pathlib import Path
import struct
import subprocess
import sys
import tempfile

# PS4 SDK syscall stub: mov rax, rdi / mov rdi, rsi / mov rsi, rdx / mov rdx, rcx / syscall / ret
PS4_STUB_SHORT = bytes.fromhex("4889f84889f74889d64889ca0f05c3")
# PS4 SDK syscall stub with full register save: ... / mov r10, [rsp+8] / syscall / ret
PS4_STUB_FULL = bytes.fromhex("4889f84889f74889d64889ca4d89c24d89c84c8b4c24080f05c3")

# A plain syscall (no stub prefix) should still be forbidden.
PLAIN_SYSCALL = bytes.fromhex("48c7c0090000004889ca0f05c3")

PT_LOAD = 1
PT_DYNAMIC = 2


def fixture(code, size=0x8000):
    image = bytearray(size)
    image[:16] = b"\x7fELF\x02\x01\x01" + bytes(9)
    struct.pack_into("<HHIQQQIHHHHHH", image, 16, 3, 62, 1, 0, 64, 0, 0, 64, 56, 5, 64, 0, 0)
    struct.pack_into("<IIQQQQQQ", image, 64, 1, 5, 0x4000, 0, 0, 0x1000, 0x1000, 0x4000)
    tags = [(5, 0x600), (10, 1), (6, 0x620), (11, 24), (7, 0x700), (8, 0), (9, 24), (0, 0)]
    struct.pack_into("<IIQQQQQQ", image, 120, 2, 6, 0x4600, 0x600, 0x600, len(tags) * 16, len(tags) * 16, 8)
    image[0x4000:0x4000 + len(code)] = code
    for index, tag in enumerate(tags):
        struct.pack_into("<qQ", image, 0x4600 + index * 16, *tag)
    return bytes(image)


def relink(relinker, work, name, image, options):
    source = work / f"{name}.elf"
    output = work / f"{name}.out"
    source.write_bytes(image)
    result = subprocess.run([str(relinker), "--skip-sce-module", *options, str(source), str(output)],
                            capture_output=True, text=True, timeout=20)
    return result, output


def main():
    relinker = Path(sys.argv[1]).resolve()
    with tempfile.TemporaryDirectory(prefix="anyps5-ps4-syscall-") as directory:
        work = Path(directory)

        # PS4 short stub: accepted with --ps4 --trap-sdk-syscall-stubs (trapped).
        result, output = relink(relinker, work, "short-trapped",
                                fixture(PS4_STUB_SHORT), ["--ps4", "--trap-sdk-syscall-stubs"])
        assert result.returncode == 0, ("PS4 short stub trapped", result.returncode, result.stdout, result.stderr)
        assert "Trapping SDK syscall instruction" in result.stderr, result.stderr

        # PS4 short stub: forbidden without --trap-sdk-syscall-stubs under --ps4.
        result, _ = relink(relinker, work, "short-forbidden",
                           fixture(PS4_STUB_SHORT), ["--ps4"])
        assert result.returncode == 2, ("PS4 short stub not trapped", result.returncode, result.stderr)
        assert "Forbidden syscall instruction at code offset" in result.stderr, result.stderr

        # PS4 short stub: not recognized without --ps4 (rejected as forbidden syscall).
        result, _ = relink(relinker, work, "short-no-ps4",
                           fixture(PS4_STUB_SHORT), ["--trap-sdk-syscall-stubs"])
        assert result.returncode == 2, ("PS4 short stub without --ps4", result.returncode, result.stderr)
        assert "Forbidden syscall instruction at code offset" in result.stderr, result.stderr

        # PS4 full stub: accepted with --ps4 --trap-sdk-syscall-stubs.
        result, output = relink(relinker, work, "full-trapped",
                                fixture(PS4_STUB_FULL), ["--ps4", "--trap-sdk-syscall-stubs"])
        assert result.returncode == 0, ("PS4 full stub trapped", result.returncode, result.stdout, result.stderr)
        assert "Trapping SDK syscall instruction" in result.stderr, result.stderr

        # Plain syscall (no stub): forbidden even with --trap-sdk-syscall-stubs under --ps4.
        result, _ = relink(relinker, work, "plain-forbidden",
                           fixture(PLAIN_SYSCALL), ["--ps4", "--trap-sdk-syscall-stubs"])
        assert result.returncode == 2, ("plain syscall should fail", result.returncode, result.stderr)
        assert "Forbidden syscall instruction at code offset" in result.stderr, result.stderr

    print("PS4 syscall stub tests passed")


if __name__ == "__main__":
    main()