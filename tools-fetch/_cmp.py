import re

src = open('C:/PersonalProjects/AnyPs4/fix_restore.py', encoding='utf-8').read()
m = re.search(r"missing = '''(.*?)'''", src, re.S)
emb = m.group(1)
cur = open('C:/PersonalProjects/AnyPs4/tools-fetch/main_app.py', encoding='utf-8').read()
anchor = '    @staticmethod\n    def _try_mkdir(path):'
i = cur.index(anchor)
tail = cur[i:]
print('embedded len', len(emb), 'tail len', len(tail))
print('IDENTICAL' if emb.strip() == tail.strip() else 'DIFFERENT')

if emb.strip() != tail.strip():
    import difflib
    for line in difflib.unified_diff(emb.strip().splitlines(), tail.strip().splitlines(), 'embedded', 'current', lineterm='', n=1):
        print(line)
