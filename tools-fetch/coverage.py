"""Compare game base-NIDs against stub APS5_EXPORT NIDs."""
import glob
import re

pat = re.compile(r'APS5_EXPORT\(\"([A-Za-z0-9+\-]{11})\"')
exports = set()
for f in glob.glob('AnyPS4/core/libs/prx/*/Export.cpp') + glob.glob('AnyPS4/core/libs/prx/*/*.cpp') + glob.glob('AnyPS4/core/libs/prx/*/*/*.cpp'):
    try:
        exports.update(pat.findall(open(f, encoding='utf-8', errors='ignore').read()))
    except OSError:
        pass
print('stub NIDs:', len(exports))

imps = [l.strip() for l in open('tools-fetch/imports.txt') if l.strip()]
base = sorted({l.split('#')[0] for l in imps} or
              {l.strip() for l in open('tools-fetch/imports_raw.txt') if l.strip()})
print('game unique base NIDs:', len(base))
miss = sorted(n for n in base if n not in exports)
print('MISSING:', len(miss))
open('tools-fetch/missing.txt', 'w').write('\n'.join(miss))
for n in miss[:80]:
    print(' ', n)
