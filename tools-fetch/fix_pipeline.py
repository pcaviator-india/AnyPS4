path = 'c:/PersonalProjects/AnyPs4/tools-fetch/main_app.py'
with open(path, 'r') as f:
    data = f.read()
old = 'self._process_single_pkg(pkg_dir)'
new = 'self._process_single_pkg(pkg_path)'
old_block = '            try:\\n                self._process_single_pkg(pkg_dir)\\n            except NameError:\\n                # pkg_dir was a typo, use pkg_path\\n                pass\\n            try:'
if old in data:
    data = data.replace(old, new)
old2 = '            except NameError:\\n                # pkg_dir was a typo, use pkg_path\\n                pass\\n            try:'
new2 = '            try:'
if old2 in data:
    data = data.replace(old2, new2, 1)
with open(path, 'w') as f:
    f.write(data)
print('Pipeline bug fixed')
