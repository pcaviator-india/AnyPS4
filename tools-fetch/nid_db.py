#!/usr/bin/env python3
"""
NID database module for AnyPS4 Phase 2 stub generation.

Loads NID -> human-readable name mappings from CSV/JSON files and provides
bidirectional lookup. Based on the aerolib.csv format used by AnyPS4's
nid_names.py (https://github.com/pcaviator-india/AnyPS4) and the sce_symbols
project by zecoxao.

CSV format (aerolib.csv style):
    NID name          # optional comment
    +AFvOEXrKJk sceGnmRegisterMemory
    ...
    # comment lines are ignored
    # trailing # comment after the name is ignored

JSON format:
    {
        "+AFvOEXrKJk": "sceGnmRegisterMemory",
        ...
    }

NID format: 11 characters from [A-Za-z0-9+-] (base64url-ish without padding)

No automatic downloads are performed. The user must provide the database file.
"""

import re
from pathlib import Path
from typing import Dict, Optional

# NID pattern: exactly 11 chars from the custom base64 alphabet
NID_RE = re.compile(r"^[A-Za-z0-9+\-]{11}$")

# NID suffix used in the PS4 NID hashing algorithm (SHA1 + suffix + base64url)
NID_SUFFIX = bytes([
    0x51, 0x8D, 0x64, 0xA6, 0x35, 0xDE, 0xD8, 0xC1,
    0xE6, 0xB0, 0x39, 0xB1, 0xC3, 0xE5, 0x52, 0x30,
])

CHARSET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-"
STD_B64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"


def is_nid(name: str) -> bool:
    """Return True if *name* looks like a PS4 NID (11 chars, base64url-ish)."""
    return bool(NID_RE.match(name))

def compute_nid(symbol: str) -> str:
    """Compute the PS4 NID for a symbol name.

    Algorithm (matches AnyPS4/tools/nid_names.py and check_nids.py):
        1. SHA1(symbol_name + SUFFIX)
        2. Reverse bytes 7..0
        3. Custom base64 encoding (first 11 chars)
    """
    import hashlib
    import base64

    digest = hashlib.sha1(symbol.encode("ascii") + NID_SUFFIX).digest()
    reversed_ = digest[7::-1]
    full = base64.b64encode(reversed_).decode()
    return "".join(CHARSET[STD_B64.index(c)] for c in full[:11])


class NidDatabase:
    """Load and query a NID -> name database.

    Supports CSV (aerolib.csv style: "NID name" per line) and JSON
    ({"NID": "name", ...}) formats.
    """

    def __init__(self) -> None:
        self.nid_to_name: Dict[str, str] = {}
        self.name_to_nid: Dict[str, str] = {}
        self.source_path: Optional[Path] = None
        self.loaded = False

    def load_csv(self, path: Path) -> int:
        """Load a CSV-format NID database (NID name per line).

        Returns the number of entries loaded.
        """
        path = Path(path)
        count = 0
        with open(path, "r", encoding="utf-8-sig", errors="replace") as handle:
            for line in handle:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # Strip inline comment
                if "#" in line:
                    line = line[: line.index("#")].strip()
                parts = line.split(None, 1)
                if len(parts) < 2:
                    continue
                nid, name = parts[0].strip(), parts[1].strip()
                if not is_nid(nid) or not name:
                    continue
                self.nid_to_name[nid] = name
                self.name_to_nid[name] = nid
                count += 1
        self.source_path = path
        self.loaded = True
        return count

    def load_json(self, path: Path) -> int:
        """Load a JSON-format NID database ({NID: name, ...}).

        Returns the number of entries loaded.
        """
        path = Path(path)
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        count = 0
        for nid, name in data.items():
            if not is_nid(nid) or not name:
                continue
            self.nid_to_name[nid] = name
            self.name_to_nid[name] = nid
            count += 1
        self.source_path = path
        self.loaded = True
        return count

    def load(self, path: Path) -> int:
        """Auto-detect format and load a NID database file.

        Returns the number of entries loaded.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"NID database not found: {path}")
        if path.suffix.lower() == ".json":
            return self.load_json(path)
        # Default to CSV for .csv, .txt, or unknown extensions
        return self.load_csv(path)

    def lookup(self, nid: str) -> Optional[str]:
        """Return the human-readable name for a NID, or None if unknown."""
        return self.nid_to_name.get(nid)

    def lookup_name(self, name: str) -> Optional[str]:
        """Return the NID for a human-readable name, or None if unknown."""
        return self.name_to_nid.get(name)

    def resolve_name(self, name: str) -> str:
        """If *name* looks like a NID and we have a mapping, return the
        human-readable name. Otherwise return *name* unchanged."""
        if is_nid(name):
            resolved = self.lookup(name)
            if resolved:
                return resolved
        return name

    def __len__(self) -> int:
        return len(self.nid_to_name)

    def __bool__(self) -> bool:
        return self.loaded and len(self.nid_to_name) > 0

    def __contains__(self, nid: str) -> bool:
        return nid in self.nid_to_name


# Global default database instance (lazy-loaded)
_default_db: Optional[NidDatabase] = None


def get_default_db() -> Optional[NidDatabase]:
    """Return the module-level default NID database (lazy-loaded)."""
    global _default_db
    if _default_db is None:
        _default_db = NidDatabase()
        # Try common locations
        for candidate in [
            Path("nid_db.csv"),
            Path("nid_db.json"),
            Path("tools-fetch/nid_db.csv"),
            Path("tools-fetch/nid_db.json"),
            Path.home() / "anyps4-nid-db.csv",
        ]:
            if candidate.exists():
                try:
                    _default_db.load(candidate)
                    break
                except Exception:
                    pass
    return _default_db


def set_default_db(path: Path) -> NidDatabase:
    """Set and load the default NID database from *path*."""
    global _default_db
    db = NidDatabase()
    db.load(path)
    _default_db = db
    return db


def resolve_nid(name: str) -> str:
    """Resolve a NID to its human-readable name using the default database.

    If no database is loaded or the NID is unknown, return *name* unchanged.
    """
    db = get_default_db()
    if db:
        return db.resolve_name(name)
    return name