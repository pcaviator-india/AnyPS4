import os

root = r'c:\PersonalProjects\AnyPs4\AnyPS4\core\relinker\relinker\tests'
files = ['test_ps4_minimal.py', 'test_ps4_header.py', 'test_ps4_syscall_stub.py']

for fname in files:
    path = os.path.join(root, fname)
    with open(path, 'r') as f:
        content = f.read()
    
    new_content = content
    # Fix double-escaped hex escapes: \\\\xNN -> \\xNN
    # File contains literal \\x7f (backslash backslash x 7 f)
    # Need single \x7f (backslash x 7 f which Python reads as byte 0x7f)
    for hexval in ['7f', '02', '01', '00', '09', '0a', '0d', '1b', '5c', '2e', '2f', '5f', '3a', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '41', '42', '43', '44', '45', '46', '61', '62', '63', '64', '65', '66', 'cc', 'ca']:
        new_content = new_content.replace('\\\\x' + hexval, '\\x' + hexval)
    
    # Fix PT_DYNAMIC segment size: 96 -> 128 (8 tags x 16 bytes = 128 bytes needed)
    new_content = new_content.replace('(PT_DYNAMIC, 6, 0x2400, 0x2400, 96, 96, 8)', '(PT_DYNAMIC, 6, 0x2400, 0x2400, 128, 128, 8)')
    
    # Fix PT_LOAD segment size: 0x1000 -> 0x2000 so it covers dynamic data addresses (0x2400-0x2700+)
    new_content = new_content.replace('(PT_LOAD, 5, 0x1000, 0x1000, 0x1000, 0x1000, 0x1000)', '(PT_LOAD, 5, 0x1000, 0x1000, 0x2000, 0x2000, 0x1000)')
    
    if new_content != content:
        with open(path, 'w') as f:
            f.write(new_content)
        print(f'FIXED: {fname}')
    else:
        print(f'NO CHANGES: {fname}')
