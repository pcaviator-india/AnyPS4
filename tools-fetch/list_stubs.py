import json
with open('export_libs_manifest.json') as f:
    data = json.load(f)
for name, entry in sorted(data['prx_files'].items()):
    if entry['is_stub']:
        print(f"{name}: {entry['export_count']} exports")