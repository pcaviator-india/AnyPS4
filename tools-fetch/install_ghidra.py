"""Download and install Ghidra 12.1.4 and GhidraOrbis extension into c:\PersonalProjects\ghidra."""
import os
import sys
import urllib.request
import zipfile
import shutil

GHIDRA_ZIP_URL = "https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_12.1.4_build/ghidra_12.1.4_PUBLIC_20260921.zip"
ORBIS_ZIP_URL = "https://github.com/astrelsky/GhidraOrbis/releases/download/1.0156/ghidra_12.1.4_PUBLIC_20261013_GhidraOrbis.zip"
DEST_DIR = r"c:\PersonalProjects\ghidra"

os.makedirs(DEST_DIR, exist_ok=True)
ghidra_zip_path = os.path.join(DEST_DIR, "ghidra.zip")
orbis_zip_path = os.path.join(DEST_DIR, "GhidraOrbis.zip")

def download_with_progress(url, dest_path):
    print(f"Downloading {url} -> {dest_path}...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp, open(dest_path, "wb") as out:
        total = int(resp.headers.get("content-length", 0))
        downloaded = 0
        chunk_size = 1024 * 1024
        while True:
            chunk = resp.read(chunk_size)
            if not chunk:
                break
            out.write(chunk)
            downloaded += len(chunk)
            if total > 0:
                percent = (downloaded / total) * 100
                print(f"\rDownloaded {downloaded // (1024*1024)}MB / {total // (1024*1024)}MB ({percent:.1f}%)", end="", flush=True)
            else:
                print(f"\rDownloaded {downloaded // (1024*1024)}MB", end="", flush=True)
    print("\nDownload finished.")

if not os.path.exists(ghidra_zip_path) or os.path.getsize(ghidra_zip_path) < 500 * 1024 * 1024:
    download_with_progress(GHIDRA_ZIP_URL, ghidra_zip_path)
else:
    print("Ghidra zip already exists.")

if not os.path.exists(orbis_zip_path):
    download_with_progress(ORBIS_ZIP_URL, orbis_zip_path)
else:
    print("GhidraOrbis zip already exists.")

print("Extracting Ghidra...")
with zipfile.ZipFile(ghidra_zip_path, 'r') as zf:
    zf.extractall(DEST_DIR)
print("Ghidra extracted.")

# Find extracted ghidra folder (e.g. ghidra_12.1.4_PUBLIC)
ghidra_home = None
for name in os.listdir(DEST_DIR):
    p = os.path.join(DEST_DIR, name)
    if os.path.isdir(p) and name.startswith("ghidra_"):
        ghidra_home = p
        break

if not ghidra_home:
    raise RuntimeError("Could not find extracted Ghidra directory in " + DEST_DIR)

print(f"Ghidra Home: {ghidra_home}")

# Install GhidraOrbis into Ghidra/Extensions/Ghidra/
ext_dir = os.path.join(ghidra_home, "Ghidra", "Extensions")
os.makedirs(ext_dir, exist_ok=True)
print("Extracting GhidraOrbis extension into Extensions/...")
with zipfile.ZipFile(orbis_zip_path, 'r') as zf:
    zf.extractall(ext_dir)

print(f"Ghidra + GhidraOrbis installation complete in {ghidra_home}!")
