import json

with open('export_libs_final_manifest.json') as f:
    data = json.load(f)

for name, entry in sorted(data['prx_files'].items()):
    if entry['is_stub']:
        print(f'=== {name} ({entry["export_count"]} exports) ===')
        for exp in entry['exports'][:10]:
            print(f'  {exp}')
        if entry['export_count'] > 10:
            print(f'  ... and {entry["export_count"] - 10} more')
        print()