#!/usr/bin/env python3
"""convert_pkg.py -- Headless PKG extraction, ELF unwrapping, relinking, and stub deployment."""

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PKGTOOL_EXE = os.path.join(BASE_DIR, "pkgtoolx", "PkgTool.exe")
UNFSELF_PY = os.path.join(BASE_DIR, "ps4_unfself.py")
RELINKER_EXE = os.path.abspath(
    os.path.join(BASE_DIR, "..", "AnyPS4", "build-relinker", "core", "relinker", "relinker.exe")
)
PRX_SOURCE_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "..", "AnyPS4", "build-full", "core", "libs", "libs")
)
PRX_SOURCE_DIR_ALT = os.path.abspath(os.path.join(BASE_DIR, "..", "libs"))

def log(msg):
    print(f"[AnyPS4 Toolchain] {msg}", flush=True)

def run_command(cmd, description):
    log(f"$ {' '.join(cmd)}")
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, errors="replace", bufsize=1
    )
    if proc.stdout:
        for line in proc.stdout:
            print(f"  {line.rstrip()}", flush=True)
    rc = proc.wait()
    if rc != 0:
        raise RuntimeError(f"{description} failed with exit code {rc}")

def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.digest()

def copy_prx_stubs(prx_source_dir, export_dir):
    dest_dir = os.path.join(export_dir, "libs")
    os.makedirs(dest_dir, exist_ok=True)
    stubs = sorted(Path(prx_source_dir).glob("*.prx"))
    log(f"Copying {len(stubs)} .prx stubs to {dest_dir}...")
    copied, skipped = 0, 0
    for src in stubs:
        dst = os.path.join(dest_dir, src.name)
        if os.path.exists(dst):
            try:
                if os.path.getsize(src) == os.path.getsize(dst) and file_sha256(src) == file_sha256(dst):
                    skipped += 1
                    continue
            except OSError:
                pass
        shutil.copy2(src, dst)
        copied += 1
    log(f"Stubs copied: {copied}, skipped (up-to-date): {skipped}")

def populate_app0(uroot_dir, app0_dir):
    if not os.path.isdir(uroot_dir):
        return
    os.makedirs(app0_dir, exist_ok=True)
    copied_files = 0
    for root, dirs, files in os.walk(uroot_dir):
        rel_root = os.path.relpath(root, uroot_dir)
        target_dir = os.path.join(app0_dir, rel_root) if rel_root != "." else app0_dir
        os.makedirs(target_dir, exist_ok=True)
        for f in files:
            if f.lower().endswith(".elf"):
                continue
            src_path = os.path.join(root, f)
            dst_path = os.path.join(target_dir, f)
            try:
                if not os.path.exists(dst_path) or os.path.getsize(src_path) != os.path.getsize(dst_path):
                    shutil.copy2(src_path, dst_path)
                    copied_files += 1
            except OSError as exc:
                log(f"WARN copying {f} to app0/: {exc}")
    log(f"Populated app0/ ({copied_files} asset files copied)")

def ensure_param_json(app0_dir, title_id, title_name):
    sce_sys = os.path.join(app0_dir, "sce_sys")
    os.makedirs(sce_sys, exist_ok=True)
    param_json = os.path.join(sce_sys, "param.json")
    if os.path.isfile(param_json):
        return
    data = {
        "titleId": title_id or "CUSA00000",
        "contentId": f"IV0000-{title_id or 'CUSA00000'}_00-0000000000000000",
        "localizedParameters": {
            "defaultLanguage": "en-US",
            "en-US": {"titleName": title_name or "PS4 Application"}
        }
    }
    with open(param_json, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    log(f"Created param.json for {title_id}")

def process_pkg(pkg_path, output_base, temp_base):
    pkg_name = Path(pkg_path).name
    safe_name = Path(pkg_name).stem
    for char in "[] ":
        safe_name = safe_name.replace(char, "_")
    
    extract_dir = os.path.join(temp_base, f"temp_{safe_name}")
    export_dir = os.path.join(output_base, f"export_{safe_name}")
    
    log(f"Starting conversion for: {pkg_name}")
    log(f"Extract Dir: {extract_dir}")
    log(f"Export Dir:  {export_dir}")
    
    # 1. Extract
    log("[1/5] Extracting PKG with PkgTool...")
    os.makedirs(extract_dir, exist_ok=True)
    run_command([PKGTOOL_EXE, "pkg_extract", "--passcode", "0" * 32, pkg_path, extract_dir], "PkgTool")
    
    # 2. Unwrap SELF
    log("[2/5] Unwrapping SELF/ELF files...")
    uroot = os.path.join(extract_dir, "uroot")
    if not os.path.isdir(uroot):
        raise RuntimeError(f"uroot missing in {extract_dir}")
    
    sys.path.insert(0, os.path.dirname(UNFSELF_PY))
    import ps4_unfself as unfself
    
    self_files = sorted(
        p for p in Path(uroot).rglob("*")
        if p.is_file() and p.suffix.lower() in (".elf", ".bin", ".prx", ".sprx")
    )
    for src in self_files:
        if src.suffix.lower() == ".elf":
            log(f"  Existing ELF: {src.name}")
        else:
            elf_dst = str(src.with_suffix(".elf"))
            log(f"  Unwrapping {src.name} -> {Path(elf_dst).name}...")
            unfself.unwrap_self(str(src), elf_dst, log=print)
    
    # 3. Relink
    log("[3/5] Relinking eboot.elf to native app.exe...")
    eboot = os.path.join(uroot, "eboot.elf")
    if not os.path.isfile(eboot):
        # Look for eboot.bin -> eboot.elf
        alt_eboot = os.path.join(uroot, "eboot.bin")
        if os.path.isfile(alt_eboot):
            eboot = str(Path(alt_eboot).with_suffix(".elf"))
    if not os.path.isfile(eboot):
        raise RuntimeError(f"Could not locate eboot.elf in {uroot}")
    
    os.makedirs(export_dir, exist_ok=True)
    out_exe = os.path.join(export_dir, "app.exe")
    relink_cmd = [RELINKER_EXE, "--ps4", "--lazy-binding", "--skip-sce-module", "--windows", eboot, out_exe]
    run_command(relink_cmd, "Relinker (Windows)")
    
    # 4. Deploy Assets
    log("[4/5] Deploying game assets & metadata...")
    app0_dir = os.path.join(export_dir, "app0")
    populate_app0(uroot, app0_dir)
    
    tid_match = re.search(r'(CUSA\d{5})', pkg_name, re.IGNORECASE)
    title_id = tid_match.group(1).upper() if tid_match else "CUSA00000"
    title_name = safe_name.replace("_", " ").strip()
    ensure_param_json(app0_dir, title_id, title_name)
    
    # 5. Copy PRX stubs & Mingw DLLs
    log("[5/5] Copying .prx libraries and runtime DLLs...")
    prx_src = PRX_SOURCE_DIR if os.path.isdir(PRX_SOURCE_DIR) else PRX_SOURCE_DIR_ALT
    copy_prx_stubs(prx_src, export_dir)
    
    for mingw_dir in [r"C:\msys64\ucrt64\bin", r"C:\PersonalProjects\AnyPs4\mingw15\mingw64\bin"]:
        if os.path.isdir(mingw_dir):
            for dll in ("libgcc_s_seh-1.dll", "libstdc++-6.dll", "libwinpthread-1.dll"):
                s = os.path.join(mingw_dir, dll)
                d = os.path.join(export_dir, dll)
                if os.path.isfile(s) and not os.path.isfile(d):
                    shutil.copy2(s, d)
                    log(f"Copied {dll}")
            break
            
    log(f"SUCCESS! Game converted successfully to: {export_dir}")
    return export_dir

if __name__ == "__main__":
    pkg = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\Info-Tech\Downloads\Games\ps4\[SuperPSX.com]-PC.Building.Simulator-CUSA14566-Game-v1.00_[6.72]_OPOISSO893.pkg"
    out_dir = r"C:\Users\Info-Tech\Downloads\Games\ps4\export"
    temp_dir = r"C:\Users\Info-Tech\Downloads\Games\ps4\temp"
    process_pkg(pkg, out_dir, temp_dir)
