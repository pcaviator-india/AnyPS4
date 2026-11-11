#!/usr/bin/env python3
"""Add __declspec(dllexport) to function declarations in Export.cpp files."""

import os
import re
import sys

BASE = r"C:\PersonalProjects\AnyPs4\AnyPS4\core\libs\prx"

TARGET_PRXS = ["libSceSsl", "libSceAudioIn"]


def add_dllexport(filepath):
    """Add __declspec(dllexport) to APS5_VABI function declarations."""
    with open(filepath, 'r') as f:
        content = f.read()

    # Pattern: return_type APS5_VABI function_name(
    # We want to insert __declspec(dllexport) after the return type
    pattern = r'^(int|void|bool|int32_t|std::size_t)\s+(APS5_VABI\s+\w+\s*\()'
    
    new_lines = []
    count = 0
    for line in content.split('\n'):
        stripped = line.strip()
        match = re.match(r'^(int|void|bool|int32_t|std::size_t)\s+APS5_VABI\s+(\w+)\s*\(', stripped)
        if match:
            ret_type = match.group(1)
            rest = match.group(2)
            # Replace the first occurrence of ret_type with "__declspec(dllexport) ret_type"
            indent = line[:len(line) - len(line.lstrip())]
            new_line = f"{indent}__declspec(dllexport) {ret_type} {rest}"
            new_lines.append(new_line)
            count += 1
        else:
            new_lines.append(line)

    new_content = '\n'.join(new_lines)
    with open(filepath, 'w') as f:
        f.write(new_content)
    print(f"  Added __declspec(dllexport) to {count} functions in {os.path.basename(os.path.dirname(filepath))}")
    return count


def main():
    total = 0
    for prx_name in TARGET_PRXS:
        export_cpp = os.path.join(BASE, prx_name, "Export.cpp")
        if not os.path.isfile(export_cpp):
            print(f"SKIP {prx_name}: no Export.cpp")
            continue
        print(f"\nProcessing {prx_name}...")
        count = add_dllexport(export_cpp)
        total += count
    print(f"\nTotal: {total} functions got __declspec(dllexport)")


if __name__ == "__main__":
    main()