import sys, os

for prx_dir in sys.argv[1:]:
    export_cpp = os.path.join(prx_dir, 'Export.cpp')
    if not os.path.isfile(export_cpp):
        print(f"=== {prx_dir} === NO Export.cpp")
        continue
    with open(export_cpp, 'r') as f:
        content = f.read()
    print(f"=== {prx_dir} ===")
    # Find extern C block
    in_extern = False
    brace_depth = 0
    for line in content.split('\n'):
        stripped = line.strip()
        if 'extern \"C\"' in line:
            in_extern = True
            brace_depth = 0
            continue
        if in_extern:
            brace_depth += line.count('{') - line.count('}')
            if 'APS5_VABI' in line and '(' in line and ')' in line:
                # Extract function signature
                print(f"  {stripped[:120]}")
            if brace_depth <= 0 and '}' in line:
                in_extern = False
    print()