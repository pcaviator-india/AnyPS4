#!/usr/bin/env python3
"""Add __declspec(dllexport) to function declarations in Export.cpp files.

Only adds to function declarations at top level (not inside function bodies).
Tracks brace depth to avoid breaking code inside function bodies.
"""

import os
import re
import sys

BASE = r"C:\PersonalProjects\AnyPs4\AnyPS4\core\libs\prx"

# PRXs that need __declspec(dllexport) - functions outside extern "C"
TARGET_PRXS = ["libSceSsl", "libSceAudioIn"]


def add_dllexport(filepath):
    """Add __declspec(dllexport) to top-level function declarations."""
    with open(filepath, 'r') as f:
        lines = f.readlines()

    new_lines = []
    brace_depth = 0
    in_extern_c = False
    count = 0

    for line in lines:
        stripped = line.strip()

        # Track brace depth
        open_braces = line.count('{')
        close_braces = line.count('}')

        # Check if this line is a function declaration at top level
        # (brace_depth <= 1 means we're at file scope or inside extern "C")
        # but NOT inside a function body (depth >= 2)
        is_func_decl = False
        if brace_depth <= 1:
            match = re.match(
                r'^(\s*)(int|void|bool|int32_t|std::size_t)\s+(APS5_VABI\s+\w+\s*\()',
                line
            )
            if match:
                indent = match.group(1)
                # Insert __declspec(dllexport) before the return type,
                # keeping the rest of the line intact (parameters, etc.)
                rest = line[match.end():]
                new_lines.append(
                    f'{indent}__declspec(dllexport) {match.group(0)}{rest}'
                )
                count += 1
                is_func_decl = True

        if not is_func_decl:
            new_lines.append(line)

        # Update brace depth AFTER processing the line
        brace_depth += open_braces - close_braces
        if brace_depth < 0:
            brace_depth = 0

    new_content = ''.join(new_lines)
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