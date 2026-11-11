import os, re
BASE = r'C:\PersonalProjects\AnyPs4\AnyPS4\core\libs\prx'
prx_name = 'libSceRandom'
export_cpp = os.path.join(BASE, prx_name, 'Export.cpp')
print('File exists:', os.path.isfile(export_cpp))
with open(export_cpp, 'r') as f:
    content = f.read()
print('Has APS5_DUMMY_FUN:', 'APS5_DUMMY_FUN' in content)
for line in content.split('\n'):
    stripped = line.strip()
    match = re.match(r'^(int|void|bool|int32_t|std::size_t)\s+APS5_VABI\s+(\w+)\s*\(', stripped)
    if match:
        print('Match:', stripped[:100])