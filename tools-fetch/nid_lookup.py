#!/usr/bin/env python3
"""
NID lookup tool for AnyPS4.

Look up PS4 NIDs and resolve them to human-readable function names using
a NID database (CSV or JSON format). Can also compute NIDs from symbol names.

Usage:
    python nid_lookup.py --db nid_db.csv --nid +AFvOEXrKJk
    python nid_lookup.py --db nid_db.csv --name sceGnmRegisterMemory
    python nid_lookup.py --db nid_db.csv --lookup "+AFvOEXrKJk,0z45PIH+SNI"
    python nid_lookup.py --compute sceGnmRegisterMemory

No automatic downloads are performed. Provide your own database file
(e.g. aerolib.csv from https://github.com/zecoxao/sce_symbols
 or https://github.com/idc/ps4libdoc).
"""

import argparse
import json
import sys
from pathlib import Path

from nid_db import NidDatabase, compute_nid, is_nid, resolve_nid, set_default_db


def cmd_lookup(args) -> int:
    """Resolve one or more NIDs to names."""
    db = NidDatabase()
    try:
        count = db.load(args.db)
        print(f"Loaded {count} entries from {args.db}")
    except Exception as exc:
        print(f"ERROR: could not load database {args.db}: {exc}", file=sys.stderr)
        return 1

    nids = [n.strip() for n in args.nid.split(",") if n.strip()]
    for nid in nids:
        if not is_nid(nid):
            print(f"  {nid}: INVALID NID format (expected 11 chars from A-Za-z0-9+-)")
            continue
        name = db.lookup(nid)
        if name:
            print(f"  {nid} -> {name}")
        else:
            print(f"  {nid}: NOT FOUND in database")
    return 0


def cmd_name(args) -> int:
    """Compute NID(s) from symbol name(s)."""
    names = [n.strip() for n in args.name.split(",") if n.strip()]
    for name in names:
        nid = compute_nid(name)
        print(f"  {name} -> {nid}")
    return 0


def cmd_resolve(args) -> int:
    """Resolve NIDs using the default database, printing both raw and resolved."""
    db = NidDatabase()
    try:
        count = db.load(args.db)
        print(f"Loaded {count} entries from {args.db}")
    except Exception as exc:
        print(f"ERROR: could not load database {args.db}: {exc}", file=sys.stderr)
        return 1

    items = [i.strip() for i in args.items.split(",") if i.strip()]
    for item in items:
        if is_nid(item):
            resolved = db.resolve_name(item)
            status = "RESOLVED" if resolved != item else "UNKNOWN"
            print(f"  {item} -> {resolved} [{status}]")
        else:
            # Try computing NID from name
            nid = compute_nid(item)
            in_db = db.lookup_name(item) is not None
            print(f"  {item} -> NID={nid} [in_db={in_db}]")
    return 0


def cmd_set_default(args) -> int:
    """Set the default NID database path for lazy loading."""
    try:
        db = set_default_db(args.db)
        print(f"Default NID database set: {len(db)} entries from {args.db}")
    except Exception as exc:
        print(f"ERROR: could not load database {args.db}: {exc}", file=sys.stderr)
        return 1
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Look up and compute PS4 NIDs (NID database lookup tool)"
    )
    parser.add_argument(
        "--db",
        default=None,
        help="Path to NID database CSV or JSON file (NID name per line)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # lookup
    p_lookup = sub.add_parser("lookup", help="Resolve NID(s) to function name(s)")
    p_lookup.add_argument("--nid", required=True, help="Comma-separated NID(s)")
    p_lookup.set_defaults(func=cmd_lookup)

    # name
    p_name = sub.add_parser("name", help="Compute NID from symbol name(s)")
    p_name.add_argument("--name", required=True, help="Comma-separated symbol name(s)")
    p_name.set_defaults(func=cmd_name)

    # resolve
    p_resolve = sub.add_parser(
        "resolve",
        help="Mixed mode: resolve NIDs or compute NIDs from names",
    )
    p_resolve.add_argument(
        "--items", required=True, help="Comma-separated NIDs or names"
    )
    p_resolve.set_defaults(func=cmd_resolve)

    # set-default
    p_default = sub.add_parser(
        "set-default", help="Set the default NID database path"
    )
    p_default.add_argument(
        "--db", required=True, help="Path to NID database CSV or JSON file"
    )
    p_default.set_defaults(func=cmd_set_default)

    # Global --db applies to lookup/resolve/set-default
    args = parser.parse_args(argv)
    if args.command in ("lookup", "resolve", "set-default") and not args.db:
        parser.error(f"--db is required for the '{args.command}' command")

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())