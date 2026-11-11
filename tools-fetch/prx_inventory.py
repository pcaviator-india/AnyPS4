#!/usr/bin/env python3
"""PRX Inventory Tool

Scans a directory of PS4 PRX / SPRX files and reports which ones have been
converted to valid Windows PE DLLs, their export counts (NID names), and
whether they are stubs or full implementations.
"""
import csv
import json
import os
import struct
import sys
from pathlib import Path
from typing import Dict, List, Optional


def is_pe(path: str) -> bool:
    try:
        with open(path, "rb") as f:
            data = f.read(256)
        if len(data) < 0x40 or data[:2] != b"MZ":
            return False
        pe_off = struct.unpack_from("<I", data, 0x3C)[0]
        if pe_off + 4 > len(data):
            return False
        return data[pe_off : pe_off + 4] == b"PE\x00\x00"
    except Exception:
        return False


def _rva_to_offset(data, sections, rva):
    for vaddr, span, raddr in sections:
        if vaddr <= rva < vaddr + span:
            return raddr + (rva - vaddr)
    return None


def pe_export_names(path: str) -> List[str]:
    with open(path, "rb") as f:
        data = f.read()
    if data[:2] != b"MZ":
        raise ValueError("not a PE file: " + path)
    pe_off = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe_off : pe_off + 4] != b"PE\x00\x00":
        raise ValueError("bad PE signature: " + path)
    num_sections = struct.unpack_from("<H", data, pe_off + 6)[0]
    opt_size = struct.unpack_from("<H", data, pe_off + 20)[0]
    opt = pe_off + 24
    magic = struct.unpack_from("<H", data, opt)[0]
    dd_off = opt + (112 if magic == 0x20B else 96)
    exp_rva, exp_size = struct.unpack_from("<II", data, dd_off)
    sections = []
    sec_off = opt + opt_size
    for index in range(num_sections):
        base = sec_off + index * 40
        vsize, vaddr, rsize, raddr = struct.unpack_from("<IIII", data, base + 8)
        sections.append((vaddr, max(vsize, rsize), raddr))
    if not exp_rva:
        return []
    exp_off = _rva_to_offset(data, sections, exp_rva)
    if exp_off is None:
        return []
    fields = struct.unpack_from("<IIHHIIIIII", data, exp_off)
    num_names = fields[7]
    names_rva = fields[9]
    names_off = _rva_to_offset(data, sections, names_rva)
    if names_off is None:
        return []
    names = []
    for index in range(num_names):
        rva = struct.unpack_from("<I", data, names_off + index * 4)[0]
        off = _rva_to_offset(data, sections, rva)
        if off is None:
            continue
        end = data.find(b"\x00", off)
        if end > off:
            names.append(data[off:end].decode("ascii", "replace"))
    return names


def scan_libs(libs_dir: str) -> Dict[str, dict]:
    inventory: Dict[str, dict] = {}
    libs_path = Path(libs_dir)
    if not libs_path.exists() or not libs_path.is_dir():
        return inventory
    for f in sorted(libs_path.glob("*.prx")) + sorted(libs_path.glob("*.sprx")):
        path = str(f)
        entry = {
            "name": f.name,
            "stem": f.stem,
            "size": f.stat().st_size,
            "is_pe": is_pe(path),
            "converted": False,
            "is_stub": False,
            "exports": [],
            "export_count": 0,
            "error": None,
        }
        if entry["is_pe"]:
            try:
                exports = pe_export_names(path)
                entry["exports"] = exports
                entry["export_count"] = len(exports)
                entry["converted"] = True
                if entry["export_count"] < 5:
                    entry["is_stub"] = True
            except Exception as exc:
                entry["error"] = str(exc)
        inventory[f.name] = entry
    return inventory


def summary(inventory: Dict[str, dict]) -> dict:
    total = len(inventory)
    pe_count = sum(1 for v in inventory.values() if v["is_pe"])
    converted = sum(1 for v in inventory.values() if v["converted"])
    stubs = sum(1 for v in inventory.values() if v["is_stub"])
    missing = total - pe_count
    total_exports = sum(v["export_count"] for v in inventory.values())
    return {
        "total": total,
        "pe_files": pe_count,
        "converted": converted,
        "stubs": stubs,
        "missing_or_not_pe": missing,
        "total_exports": total_exports,
    }


def write_json(inventory: Dict[str, dict], output_path: str):
    data = {"summary": summary(inventory), "prx_files": inventory}
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def write_csv(inventory: Dict[str, dict], output_path: str):
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "prx_name",
                "stem",
                "size",
                "is_pe",
                "converted",
                "is_stub",
                "export_count",
                "error",
            ]
        )
        for name, entry in inventory.items():
            writer.writerow(
                [
                    entry["name"],
                    entry["stem"],
                    entry["size"],
                    entry["is_pe"],
                    entry["converted"],
                    entry["is_stub"],
                    entry["export_count"],
                    entry.get("error", ""),
                ]
            )


def main(argv: List[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    libs_dir = argv[0]
    output_json = None
    output_csv = None
    i = 1
    while i < len(argv):
        if argv[i] == "--output" and i + 1 < len(argv):
            output_json = argv[i + 1]
            i += 2
        elif argv[i] == "--csv" and i + 1 < len(argv):
            output_csv = argv[i + 1]
            i += 2
        else:
            i += 1
    inventory = scan_libs(libs_dir)
    summ = summary(inventory)
    print(f"PRX Inventory for: {libs_dir}")
    print(f"  Total PRX/SPRX files: {summ['total']}")
    print(f"  Valid PE DLLs:       {summ['pe_files']}")
    print(f"  Converted (PE+exports): {summ['converted']}")
    print(f"  Stubs (<5 exports):  {summ['stubs']}")
    print(f"  Missing / not PE:    {summ['missing_or_not_pe']}")
    print(f"  Total exports:       {summ['total_exports']}")
    print()
    for name, entry in inventory.items():
        status = []
        if not entry["is_pe"]:
            status.append("NOT_PE")
        elif entry["is_stub"]:
            status.append("STUB")
        elif entry["converted"]:
            status.append("CONVERTED")
        if entry.get("error"):
            status.append(f"ERROR:{entry['error']}")
        status_str = ",".join(status) if status else "UNKNOWN"
        print(
            f"  {name:45s} size={entry['size']:>10,}  "
            f"exports={entry['export_count']:>5}  {status_str}"
        )
    if output_json:
        write_json(inventory, output_json)
        print(f"\nJSON manifest written to: {output_json}")
    if output_csv:
        write_csv(inventory, output_csv)
        print(f"CSV inventory written to: {output_csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))