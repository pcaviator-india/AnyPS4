import re

with open(r'C:\PersonalProjects\AnyPs4\AnyPS4\core\libs\prx\libkernel\DirectMemory\DirectMemory.cpp') as f:
    content = f.read()

for match in re.finditer(r'sceKernelMapDirectMemory\w*', content):
    start = max(0, match.start() - 150)
    end = min(len(content), match.end() + 150)
    print(f'=== Position {match.start()} ===')
    print(content[start:end])
    print()