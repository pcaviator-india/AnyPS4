with open(r'C:\PersonalProjects\AnyPs4\AnyPS4\core\libs\prx\libSceSsl\Export.cpp') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    stripped = line.strip()
    if 'namespace {' in stripped:
        print(f'{i+1}: namespace {{')
    if stripped == '}':
        print(f'{i+1}: }}')
    if 'extern' in line and 'C' in line:
        print(f'{i+1}: {stripped[:80]}')