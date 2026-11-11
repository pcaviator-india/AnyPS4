import json

with open('export_libs_final_manifest.json') as f:
    data = json.load(f)

stubs = []
converted = 0
for name, entry in sorted(data['prx_files'].items()):
    if entry['is_stub']:
        stubs.append((name, entry['export_count']))
    elif entry['converted'] and not entry['is_stub']:
        converted += 1

print(f'Converted (full): {converted}')
print(f'Stubs: {len(stubs)}')
print()
for name, count in stubs:
    print(f'  {name}: {count} exports  STUB')