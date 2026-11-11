#!/usr/bin/env python3
"""PRX Gap Analysis Tool

Compares the PRX/SPRX libraries a game actually needs (from imports.txt,
missing.txt, or an ELF dynamic section) against what is available as
converted Windows PE DLLs in libs/. Outputs a list of missing or stub-only
PRXs that need conversion or Phase 2 stub generation.
"""
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prx_inventory import scan_libs, summary, write_json  # noqa: E402


def read_lines(path: str) -> List[str]:
    if not path or not os.path.isfile(path):
        return []
    with open(path, "r", encoding="ascii", errors="replace") as f:
        return [line.strip() for line in f if line.strip()]


def extract_candidate_names_from_exe(exe_path: str) -> Set[str]:
    if not exe_path or not os.path.isfile(exe_path):
        return set()
    with open(exe_path, "rb") as f:
        data = f.read()
    candidate_names = set()
    for match in re.finditer(rb"[\x21-\x7e]{6,32}\x00", data):
        raw = match.group(0)[:-1]
        try:
            name = raw.decode("ascii")
        except UnicodeDecodeError:
            continue
        if " " in name or "%" in name or name.startswith("##") or name.startswith("#"):
            continue
        has_digit = any(c.isdigit() for c in name)
        has_letter = any(c.isalpha() for c in name)
        if not (has_digit and has_letter):
            continue
        has_symbol = any(c in "+-_.=/" for c in name)
        is_mixed_case = any(c.isupper() for c in name) and any(c.islower() for c in name)
        if not (has_symbol or is_mixed_case):
            continue
        candidate_names.add(name)
    return candidate_names


def needed_prx_names(export_dir: str, imports_path: str, missing_path: str) -> Set[str]:
    needed: Set[str] = set()
    for line in read_lines(imports_path):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        dll_name = line.split("!")[0].split(":")[0].strip()
        if dll_name and _looks_like_prx(dll_name):
            needed.add(dll_name)
    for line in read_lines(missing_path):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if _looks_like_prx(line):
            needed.add(line)
    app_exe = os.path.join(export_dir, "app.exe")
    if os.path.isfile(app_exe):
        for name in extract_candidate_names_from_exe(app_exe):
            if _looks_like_prx(name):
                needed.add(name)
    return needed


def _looks_like_prx(name: str) -> bool:
    """Heuristic: does this string look like a PS4 PRX library name?"""
    if not name:
        return False
    lower = name.lower()
    # Known PS4 library prefixes
    if lower.startswith(("lib", "sce", "ulobjmgr")):
        return True
    # Contains .prx or .sprx extension
    if lower.endswith((".prx", ".sprx", ".dll")):
        return True
    # Common system DLLs
    if lower in ("kernel32.dll", "user32.dll", "shell32.dll", "advapi32.dll",
                 "ws2_32.dll", "iphlpapi.dll", "ntdll.dll"):
        return True
    return False


def analyze_gaps(
    libs_dir: str,
    needed: Set[str],
    inventory: Dict[str, dict],
) -> dict:
    available: Set[str] = set(inventory.keys())
    gaps = {
        "missing_prxs": [],
        "not_pe_prxs": [],
        "stub_only_prxs": [],
        "converted_prxs": [],
        "unneeded_prxs": [],
        "needed_count": len(needed),
        "available_count": len(available),
    }
    for name in sorted(needed):
        candidates = {name}
        if not name.endswith((".prx", ".sprx", ".dll", ".exe")):
            candidates.add(name + ".prx")
            candidates.add(name + ".sprx")
            candidates.add(name + ".dll")
        found = None
        for cand in candidates:
            if cand in inventory:
                found = cand
                break
            if found:
                break
        if not found:
            for inv_name, entry in inventory.items():
                if entry["stem"] == name or entry["stem"] == name.replace(".prx", ""):
                    found = inv_name
                    break
        if found is None:
            gaps["missing_prxs"].append(name)
        else:
            entry = inventory[found]
            if not entry["is_pe"]:
                gaps["not_pe_prxs"].append(found)
            elif entry["is_stub"]:
                gaps["stub_only_prxs"].append(found)
            else:
                gaps["converted_prxs"].append(found)
    needed_normalized: Set[str] = set()
    for n in needed:
        needed_normalized.add(n)
        if not n.endswith((".prx", ".sprx", ".dll", ".exe")):
            needed_normalized.add(n + ".prx")
            needed_normalized.add(n + ".sprx")
    for name in sorted(available):
        if name not in needed_normalized:
            stem_match = False
            for n in needed:
                for inv_name, entry in inventory.items():
                    if entry["stem"] == n or entry["stem"] == n.replace(".prx", ""):
                        stem_match = True
                        break
            if not stem_match:
                gaps["unneeded_prxs"].append(name)
    return gaps


def print_gaps(gaps: dict):
    print("=== PRX Gap Analysis ===")
    print(f"Needed PRXs:       {gaps['needed_count']}")
    print(f"Available PRXs:    {gaps['available_count']}")
    print()
    if gaps["missing_prxs"]:
        print(f"MISSING ({len(gaps['missing_prxs'])}):")
        for name in gaps["missing_prxs"]:
            print(f"  {name}")
        print()
    if gaps["not_pe_prxs"]:
        print(f"NOT_PE ({len(gaps['not_pe_prxs'])}):")
        for name in gaps["not_pe_prxs"]:
            print(f"  {name}")
        print()
    if gaps["stub_only_prxs"]:
        print(f"STUB_ONLY ({len(gaps['stub_only_prxs'])}):")
        for name in gaps["stub_only_prxs"]:
            print(f"  {name}")
        print()
    if gaps["converted_prxs"]:
        print(f"CONVERTED ({len(gaps['converted_prxs'])}):")
        for name in gaps["converted_prxs"]:
            print(f"  {name}")
        print()
    if gaps["unneeded_prxs"]:
        print(f"UNNEEDED ({len(gaps['unneeded_prxs'])}):")
        for name in gaps["unneeded_prxs"]:
            print(f"  {name}")
        print()
    total_gaps = (
        len(gaps["missing_prxs"])
        + len(gaps["not_pe_prxs"])
        + len(gaps["stub_only_prxs"])
    )
    if total_gaps == 0:
        print("All needed PRXs are fully converted. No gaps.")
    else:
        print(f"Total gaps needing attention: {total_gaps}")


def main(argv: List[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    libs_dir = argv[0]
    imports_path = None
    missing_path = None
    manifest_path = None
    output_path = None
    export_dir = None
    i = 1
    while i < len(argv):
        arg = argv[i]
        if arg == "--imports" and i + 1 < len(argv):
            imports_path = argv[i + 1]
            i += 2
        elif arg == "--missing" and i + 1 < len(argv):
            missing_path = argv[i + 1]
            i += 2
        elif arg == "--manifest" and i + 1 < len(argv):
            manifest_path = argv[i + 1]
            i += 2
        elif arg == "--output" and i + 1 < len(argv):
            output_path = argv[i + 1]
            i += 2
        elif arg == "--export-dir" and i + 1 < len(argv):
            export_dir = argv[i + 1]
            i += 2
        else:
            i += 1
    inventory = scan_libs(libs_dir)
    summ = summary(inventory)
    needed = set()
    if export_dir:
        needed = needed_prx_names(export_dir, imports_path, missing_path)
    elif imports_path or missing_path:
        for line in read_lines(imports_path):
            if line and not line.startswith("#"):
                needed.add(line.split("!")[0].strip())
        for line in read_lines(missing_path):
            if line and not line.startswith("#"):
                needed.add(line)
    gaps = analyze_gaps(libs_dir, needed, inventory)
    print_gaps(gaps)
    if output_path:
        report = {
            "summary": summ,
            "gaps": gaps,
            "inventory": inventory,
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"\nGap report written to: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))