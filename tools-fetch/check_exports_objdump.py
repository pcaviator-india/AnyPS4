import subprocess
import sys

for name in sys.argv[1:]:
    path = f'C:\\PS4\\export_Limbo.PS4-PRELUDE\\libs\\{name}'
    try:
        result = subprocess.run(
            [r'C:\PersonalProjects\AnyPs4\mingw15\mingw64\bin\objdump.exe', '-p', path],
            capture_output=True, text=True, timeout=30
        )
        # Find the export directory section
        lines = result.stdout.split('\n')
        in_exports = False
        exports = []
        for line in lines:
            if 'Export Directory' in line:
                in_exports = True
                continue
            if in_exports:
                if line.strip() == '' or line[0].isalpha():
                    in_exports = False
                    continue
                if 'nid' in line.lower():
                    exports.append(line.strip())
        print(f'{name}: {len(exports)} nid-related exports')
        for e in exports[:10]:
            print(f'  {e}')
    except Exception as exc:
        print(f'{name}: ERROR {exc}')