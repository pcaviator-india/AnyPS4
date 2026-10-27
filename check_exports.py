import sys
sys.path.insert(0, 'c:/PersonalProjects/AnyPs4/tools-fetch')
from phase2_stubs import prx_export_names
from pathlib import Path

libs_dir = Path(r'C:\Users\Info-Tech\Downloads\Games\ps4\export\export__SuperPSX_-Mega.Shoot-CUSA59042-EUR-Game-PS4-Opoisso893\libs')

for name in ['libc.prx', 'libkernel.prx', 'libkernel_sys.prx']:
    prx_file = libs_dir / name
    if prx_file.exists():
        exports = prx_export_names(str(prx_file))
        found = 'bzQExy189ZI' in exports
        print(name + ': ' + str(len(exports)) + ' exports, bzQExy189ZI: ' + ('FOUND' if found else 'not found'))
        if found:
            print('  *** We can use this PRX!')
    else:
        print(name + ': not found')