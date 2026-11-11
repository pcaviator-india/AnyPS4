import subprocess
import sys

OBJDUMP = r'C:\PersonalProjects\AnyPs4\mingw15\mingw64\bin\objdump.exe'

def check_symbols(dll_path, symbol_patterns):
    try:
        result = subprocess.run(
            [OBJDUMP, '-t', dll_path],
            capture_output=True, text=True, timeout=30
        )
        found = []
        for line in result.stdout.split('\n'):
            for pat in symbol_patterns:
                if pat in line:
                    found.append(line.strip())
                    break
        return found
    except Exception as exc:
        return [f'ERROR: {exc}']

if __name__ == '__main__':
    dll_path = sys.argv[1]
    patterns = sys.argv[2:]
    found = check_symbols(dll_path, patterns)
    print(f'Symbols in {dll_path}:')
    for f in found:
        print(f'  {f}')