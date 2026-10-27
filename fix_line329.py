with open('c:/PersonalProjects/AnyPs4/tools-fetch/phase2_stubs.py', 'r') as f:
    content = f.read()

# Fix line 329 - split merged line
old = "log_stub_fixups.append((fixup_writefile2, 'writefile_iat'))  text_data.extend(b\"\\xff\\x15\")"
new = "log_stub_fixups.append((fixup_writefile2, 'writefile_iat'))\n    text_data.extend(b\"\\xff\\x15\")"

if old in content:
    content = content.replace(old, new, 1)
    with open('c:/PersonalProjects/AnyPs4/tools-fetch/phase2_stubs.py', 'w') as f:
        f.write(content)
    print('Fixed line 329')
else:
    print('Pattern not found')
    idx = content.find("fixup_writefile2")
    if idx >= 0:
        print(repr(content[idx:idx+200]))