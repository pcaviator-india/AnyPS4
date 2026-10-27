#!/usr/bin/env python3
"""main_app.py -- AnyPS4 PKG processing GUI with PRX stub deployment.

Pipeline:
    extract PKG -> unwrap ELF/SELF files -> relink eboot.elf -> copy .prx stubs
    -> patch NIDs -> copy runtime DLLs -> deploy app0/

Usage:
    python main_app.py
    python main_app.py --no-gui <export_dir>
"""

import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from phase2_stubs import create_missing_prx_stubs


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PKGTOOL_EXE = os.path.join(BASE_DIR, "pkgtoolx", "PkgTool.exe")
UNFSELF_PY = os.path.join(BASE_DIR, "ps4_unfself.py")
RELINKER_EXE = os.path.abspath(
    os.path.join(
        BASE_DIR, "..", "AnyPS4", "build-relinker", "core", "relinker",
        "relinker.exe",
    )
)
NID_PATCHER_EXE = os.path.abspath(
    os.path.join(
        BASE_DIR, "..", "AnyPS4", "build-full", "core", "libs",
        "nid_patcher.exe",
    )
)
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")

PRX_SOURCE_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "..", "AnyPS4", "build-full", "core", "libs", "libs", "unpatched")
)
PRX_SOURCE_DIR_ALT = os.path.abspath(os.path.join(BASE_DIR, "..", "libs"))

# PRX stubs copied from the build directory. All .prx files found in the
# build source are copied to export/libs/ so that every native library
# implementation is present at load time. This prevents "procedure not found"
# errors caused by missing PRX modules.
# Excluded file names (by basename) are never copied even if present in build.
EXCLUDED_PRX_FILES = set()

DEFAULTS = {
    "pkg_folder": "",
    "output_folder": "",
    "temp_folder": "",
    "relinker_path": RELINKER_EXE,
    "nid_patcher_path": NID_PATCHER_EXE,
    "passcode": "0" * 32,
    "skip_sce_module": True,
    "copy_prx": True,
    "targets": ["windows"],
    "prx_source_dir": PRX_SOURCE_DIR,
    "patch_nids": True,
    "nid_db_path": "",
    "unwrapped_elf_files": [],
    "unwrapped_prx_files": [],
}


def load_settings():
    """Load saved settings, falling back to defaults if unavailable."""
    if os.path.isfile(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as handle:
                settings = json.load(handle)
            if isinstance(settings, dict):
                return {**DEFAULTS, **settings}
        except (json.JSONDecodeError, OSError):
            pass
    return dict(DEFAULTS)


def save_settings(settings):
    """Persist settings without crashing the application on a write error."""
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as handle:
            json.dump(settings, handle, indent=2)
    except OSError as exc:
        print(f"WARN: could not save settings: {exc}", file=sys.stderr)


def find_prx_source_dir(override=None):
    """Return the first candidate directory containing .prx stubs, or None."""
    candidates = [override, PRX_SOURCE_DIR, PRX_SOURCE_DIR_ALT]
    for candidate in candidates:
        if candidate and os.path.isdir(candidate):
            if any(Path(candidate).glob("*.prx")):
                return candidate
    return None


def file_sha256(path):
    """Compute SHA-256 digest of a file in 64 KiB chunks."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.digest()


def copy_prx_stubs(prx_source_dir, export_dir, log_cb=print):
    """Copy ALL .prx stubs from the build source to <export_dir>/libs/.

    Copies every .prx stub available in the build source directory,
    overlaying on top of any original game PRX stubs already copied
    from uroot. This ensures all ~110 native library implementations
    are present so the game never fails with "procedure not found"
    due to a missing PRX module.

    Files whose basename is in EXCLUDED_PRX_FILES are skipped.

    Returns (copied, skipped, errors).
    """
    if not prx_source_dir or not os.path.isdir(prx_source_dir):
        raise RuntimeError(f".prx stub source directory not found: {prx_source_dir}")

    dest_dir = os.path.join(export_dir, "libs")
    os.makedirs(dest_dir, exist_ok=True)

    copied = 0
    skipped = 0
    errors = []

    for src_file in sorted(Path(prx_source_dir).glob("*.prx")):
        stub_name = src_file.name
        if stub_name in EXCLUDED_PRX_FILES:
            log_cb(f"  SKIP (excluded): {stub_name}")
            continue

        dst = os.path.join(dest_dir, stub_name)
        if os.path.exists(dst):
            try:
                if os.path.getsize(src_file) == os.path.getsize(dst) and file_sha256(str(src_file)) == file_sha256(dst):
                    skipped += 1
                    log_cb(f"  skipped (up to date): {stub_name}")
                    continue
            except OSError:
                pass

        try:
            shutil.copy2(str(src_file), dst)
            copied += 1
            log_cb(f"  copied: {stub_name} -> libs/")
        except OSError as exc:
            log_cb(f"  WARN: could not copy {stub_name}: {exc} (file in use)")
            errors.append(stub_name)

    return copied, skipped, errors


def populate_app0(uroot_dir, app0_dir, log_cb=print):
    """Populate export app0/ directory from extracted PKG uroot, preserving structure."""
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
                log_cb(f"  WARN: copying {f} to app0/: {exc}")
    log_cb(f"  Populated app0/ ({copied_files} asset files copied)")


def ensure_param_json(app0_dir, title_id=None, title_name=None, log_cb=print):
    """Ensure app0/sce_sys/param.json exists so AnyPS4 runtime title initialization succeeds."""
    sce_sys = os.path.join(app0_dir, "sce_sys")
    os.makedirs(sce_sys, exist_ok=True)
    param_json = os.path.join(sce_sys, "param.json")
    if os.path.isfile(param_json):
        return
    tid = title_id or "CUSA00000"
    name = title_name or "PS4 Application"
    data = {
        "titleId": tid,
        "contentId": f"IV0000-{tid}_00-0000000000000000",
        "localizedParameters": {
            "defaultLanguage": "en-US",
            "en-US": {
                "titleName": name
            }
        }
    }
    try:
        with open(param_json, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        log_cb(f"  Created default param.json (titleId: {tid}, name: '{name}')")
    except OSError as exc:
        log_cb(f"  WARN: could not write param.json: {exc}")


class App:
    """GUI application that drives the PKG-to-app.exe pipeline."""

    def __init__(self, root):
        self.root = root
        self.root.title("AnyPS4 - PKG Processing")
        self.root.geometry("980x720")
        self.settings = load_settings()

        self.pkg_folder = tk.StringVar(value=self.settings["pkg_folder"])
        self.output_folder = tk.StringVar(value=self.settings["output_folder"])
        self.temp_folder = tk.StringVar(value=self.settings["temp_folder"])
        self.relinker_path = tk.StringVar(value=self.settings["relinker_path"])
        self.nid_patcher_path = tk.StringVar(value=self.settings["nid_patcher_path"])
        self.passcode = tk.StringVar(value=self.settings["passcode"])
        self.skip_sce_module = tk.BooleanVar(
            value=self.settings["skip_sce_module"]
        )
        self.copy_prx = tk.BooleanVar(value=self.settings["copy_prx"])
        self.patch_nids = tk.BooleanVar(value=self.settings.get("patch_nids", True))
        self.prx_source_dir = tk.StringVar(value=self.settings["prx_source_dir"])
        self.nid_db_path = tk.StringVar(value=self.settings.get("nid_db_path", ""))
        self.auto_detect = tk.BooleanVar(value=True)

        self.pkg_list = []
        self.selected_pkgs = set()
        self.worker_thread = None
        self.stop_requested = False

        # Unwrapped file selections (already-unwrapped ELF / PRX files)
        self.unwrapped_elf_files = list(
            self.settings.get("unwrapped_elf_files", [])
        )
        self.unwrapped_prx_files = list(
            self.settings.get("unwrapped_prx_files", [])
        )

        self._build_ui()
        self._refresh_pkg_list()
        self._auto_detect_tools()

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        tab_pkg = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab_pkg, text="PKG Processing")

        self._folder_row(tab_pkg, "PKG folder:", self.pkg_folder,
                         self._browse_pkg_folder)
        self._folder_row(tab_pkg, "Export folder:", self.output_folder,
                         self._browse_output_folder)
        self._folder_row(tab_pkg, "Temp folder:", self.temp_folder,
                         self._browse_temp_folder)

        ttk.Label(tab_pkg, text="Found PKG files:").pack(
            anchor=tk.W, pady=(10, 0)
        )

        list_frame = ttk.Frame(tab_pkg)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=4)
        self.pkg_tree = ttk.Treeview(
            list_frame, columns=("select", "name", "size"), show="headings", height=10
        )
        self.pkg_tree.heading("select", text="\u2713")
        self.pkg_tree.heading("name", text="PKG file")
        self.pkg_tree.heading("size", text="Size")
        self.pkg_tree.column("select", width=45, anchor=tk.CENTER, stretch=False)
        self.pkg_tree.column("name", width=620, anchor=tk.W)
        self.pkg_tree.column("size", width=100, anchor=tk.E)
        scroll = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self.pkg_tree.yview
        )
        self.pkg_tree.configure(yscrollcommand=scroll.set)
        self.pkg_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.pkg_tree.bind("<Button-1>", self._on_tree_click)

        opts = ttk.LabelFrame(tab_pkg, text="Options", padding=6)
        opts.pack(fill=tk.X, pady=8)
        ttk.Checkbutton(
            opts, text="Skip SCE module relinking",
            variable=self.skip_sce_module
        ).pack(side=tk.LEFT, padx=4)
        ttk.Checkbutton(
            opts, text="Copy .prx stubs to export/libs/",
            variable=self.copy_prx
        ).pack(side=tk.LEFT, padx=4)
        ttk.Checkbutton(
            opts, text="Patch NIDs in app.exe",
            variable=self.patch_nids
        ).pack(side=tk.LEFT, padx=4)
        ttk.Checkbutton(
            opts, text="Auto-detect tool paths",
            variable=self.auto_detect
        ).pack(side=tk.LEFT, padx=4)

        prx_row = ttk.Frame(tab_pkg)
        prx_row.pack(fill=tk.X, pady=3)
        ttk.Label(prx_row, text="PRX source:").pack(side=tk.LEFT)
        ttk.Entry(prx_row, textvariable=self.prx_source_dir).pack(
            side=tk.LEFT, padx=4, fill=tk.X, expand=True
        )
        ttk.Button(
            prx_row, text="Browse",
            command=self._browse_prx_source
        ).pack(side=tk.LEFT)

        nid_db_row = ttk.Frame(tab_pkg)
        nid_db_row.pack(fill=tk.X, pady=3)
        ttk.Label(nid_db_row, text="NID database:").pack(side=tk.LEFT)
        ttk.Entry(nid_db_row, textvariable=self.nid_db_path).pack(
            side=tk.LEFT, padx=4, fill=tk.X, expand=True
        )
        ttk.Button(
            nid_db_row, text="Browse",
            command=self._browse_nid_db
        ).pack(side=tk.LEFT)
        ttk.Label(
            nid_db_row,
            text="(CSV: NID name per line, or JSON)",
            foreground="gray",
            font=("TkDefaultFont", 8),
        ).pack(side=tk.LEFT, padx=4)

        rel_row = ttk.Frame(tab_pkg)
        rel_row.pack(fill=tk.X, pady=3)
        ttk.Label(rel_row, text="Relinker:").pack(side=tk.LEFT)
        ttk.Entry(rel_row, textvariable=self.relinker_path).pack(
            side=tk.LEFT, padx=4, fill=tk.X, expand=True
        )
        ttk.Button(
            rel_row, text="Browse",
            command=self._browse_relinker
        ).pack(side=tk.LEFT)

        nid_row = ttk.Frame(tab_pkg)
        nid_row.pack(fill=tk.X, pady=3)
        ttk.Label(nid_row, text="NID patcher:").pack(side=tk.LEFT)
        ttk.Entry(nid_row, textvariable=self.nid_patcher_path).pack(
            side=tk.LEFT, padx=4, fill=tk.X, expand=True
        )
        ttk.Button(
            nid_row, text="Browse",
            command=self._browse_nid_patcher
        ).pack(side=tk.LEFT)

        self.progress = ttk.Progressbar(tab_pkg, orient=tk.HORIZONTAL, mode="determinate")
        self.progress.pack(fill=tk.X, pady=(10, 0))

        btn_frame = ttk.Frame(tab_pkg)
        btn_frame.pack(fill=tk.X, pady=8)
        self.btn_process = ttk.Button(
            btn_frame, text="Process Selected PKGs",
            command=self._start_processing
        )
        self.btn_process.pack(side=tk.LEFT, padx=4)
        ttk.Button(
            btn_frame, text="Validate Setup", command=self._validate_setup
        ).pack(side=tk.LEFT, padx=4)
        ttk.Button(
            btn_frame, text="Save Settings", command=self._save_settings
        ).pack(side=tk.LEFT, padx=4)
        ttk.Button(
            btn_frame, text="Refresh", command=self._refresh_pkg_list
        ).pack(side=tk.LEFT, padx=4)
        ttk.Button(
            btn_frame, text="Select All", command=self._select_all
        ).pack(side=tk.LEFT, padx=4)
        ttk.Button(
            btn_frame, text="Stop After Current Step",
            command=self._request_stop
        ).pack(side=tk.LEFT, padx=4)

        ttk.Label(tab_pkg, text="Log:").pack(anchor=tk.W, pady=(8, 0))
        log_frame = ttk.Frame(tab_pkg)
        log_frame.pack(fill=tk.BOTH, expand=True)
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD)
        log_scroll = ttk.Scrollbar(
            log_frame, orient=tk.VERTICAL, command=self.log_text.yview
        )
        self.log_text.configure(yscrollcommand=log_scroll.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.status = tk.StringVar(value="Ready")
        ttk.Label(
            tab_pkg, textvariable=self.status, relief=tk.SUNKEN, anchor=tk.W
        ).pack(fill=tk.X, pady=(6, 0))

        # ---- Tab 2: Unwrapped Files ----
        tab_unwrapped = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab_unwrapped, text="Unwrapped Files")

        # --- ELF files section ---
        ttk.Label(tab_unwrapped, text="Unwrapped ELF / eboot files:").pack(
            anchor=tk.W, pady=(0, 4)
        )
        elf_frame = ttk.Frame(tab_unwrapped)
        elf_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        self.elf_listbox = tk.Listbox(elf_frame, height=8, selectmode=tk.EXTENDED)
        elf_scroll = ttk.Scrollbar(elf_frame, orient=tk.VERTICAL,
                                   command=self.elf_listbox.yview)
        self.elf_listbox.configure(yscrollcommand=elf_scroll.set)
        self.elf_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        elf_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        elf_btn_frame = ttk.Frame(tab_unwrapped)
        elf_btn_frame.pack(fill=tk.X, pady=(0, 8))
        ttk.Button(
            elf_btn_frame, text="Add ELF file(s)",
            command=self._add_elf_files
        ).pack(side=tk.LEFT, padx=4)
        ttk.Button(
            elf_btn_frame, text="Remove selected",
            command=self._remove_selected_elf
        ).pack(side=tk.LEFT, padx=4)
        ttk.Button(
            elf_btn_frame, text="Clear all",
            command=self._clear_elf_files
        ).pack(side=tk.LEFT, padx=4)

        # --- PRX files section ---
        ttk.Label(tab_unwrapped, text="Unwrapped PRX / module files:").pack(
            anchor=tk.W, pady=(12, 4)
        )
        prx_frame = ttk.Frame(tab_unwrapped)
        prx_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        self.prx_listbox = tk.Listbox(prx_frame, height=8, selectmode=tk.EXTENDED)
        prx_scroll = ttk.Scrollbar(prx_frame, orient=tk.VERTICAL,
                                   command=self.prx_listbox.yview)
        self.prx_listbox.configure(yscrollcommand=prx_scroll.set)
        self.prx_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        prx_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        prx_btn_frame = ttk.Frame(tab_unwrapped)
        prx_btn_frame.pack(fill=tk.X, pady=(0, 8))
        ttk.Button(
            prx_btn_frame, text="Add PRX file(s)",
            command=self._add_prx_files
        ).pack(side=tk.LEFT, padx=4)
        ttk.Button(
            prx_btn_frame, text="Remove selected",
            command=self._remove_selected_prx
        ).pack(side=tk.LEFT, padx=4)
        ttk.Button(
            prx_btn_frame, text="Clear all",
            command=self._clear_prx_files
        ).pack(side=tk.LEFT, padx=4)

        # --- Confirm / Load button ---
        confirm_frame = ttk.Frame(tab_unwrapped)
        confirm_frame.pack(fill=tk.X, pady=(16, 0))
        self.btn_confirm_unwrapped = ttk.Button(
            confirm_frame, text="Confirm / Load Unwrapped Files",
            command=self._confirm_unwrapped_files
        )
        self.btn_confirm_unwrapped.pack(side=tk.LEFT, padx=4)
        self.unwrapped_status = tk.StringVar(value="No files loaded")
        ttk.Label(
            confirm_frame, textvariable=self.unwrapped_status,
            relief=tk.SUNKEN, anchor=tk.W
        ).pack(side=tk.LEFT, padx=12, fill=tk.X, expand=True)

        # Populate lists from saved settings
        self._refresh_elf_listbox()
        self._refresh_prx_listbox()
        self._update_unwrapped_status()

    # -------------------------------------------------------------- unwrapped files tab
    def _refresh_elf_listbox(self):
        self.elf_listbox.delete(0, tk.END)
        for path in self.unwrapped_elf_files:
            self.elf_listbox.insert(tk.END, path)

    def _refresh_prx_listbox(self):
        self.prx_listbox.delete(0, tk.END)
        for path in self.unwrapped_prx_files:
            self.prx_listbox.insert(tk.END, path)

    def _update_unwrapped_status(self):
        n_elf = len(self.unwrapped_elf_files)
        n_prx = len(self.unwrapped_prx_files)
        self.unwrapped_status.set(
            f"{n_elf} ELF file(s), {n_prx} PRX file(s) loaded"
        )

    def _add_elf_files(self):
        files = filedialog.askopenfilenames(
            title="Select unwrapped ELF / eboot files",
            filetypes=[("ELF files", "*.elf"), ("All files", "*.*")],
        )
        if not files:
            return
        for f in files:
            if f not in self.unwrapped_elf_files:
                self.unwrapped_elf_files.append(f)
        self._refresh_elf_listbox()
        self._update_unwrapped_status()
        self._save_settings(silent=True)

    def _remove_selected_elf(self):
        selection = list(self.elf_listbox.curselection())
        selection.reverse()
        for idx in selection:
            self.unwrapped_elf_files.pop(idx)
        self._refresh_elf_listbox()
        self._update_unwrapped_status()
        self._save_settings(silent=True)

    def _clear_elf_files(self):
        self.unwrapped_elf_files.clear()
        self._refresh_elf_listbox()
        self._update_unwrapped_status()
        self._save_settings(silent=True)

    def _add_prx_files(self):
        files = filedialog.askopenfilenames(
            title="Select unwrapped PRX / module files",
            filetypes=[("PRX files", "*.prx"), ("All files", "*.*")],
        )
        if not files:
            return
        for f in files:
            if f not in self.unwrapped_prx_files:
                self.unwrapped_prx_files.append(f)
        self._refresh_prx_listbox()
        self._update_unwrapped_status()
        self._save_settings(silent=True)

    def _remove_selected_prx(self):
        selection = list(self.prx_listbox.curselection())
        selection.reverse()
        for idx in selection:
            self.unwrapped_prx_files.pop(idx)
        self._refresh_prx_listbox()
        self._update_unwrapped_status()
        self._save_settings(silent=True)

    def _clear_prx_files(self):
        self.unwrapped_prx_files.clear()
        self._refresh_prx_listbox()
        self._update_unwrapped_status()
        self._save_settings(silent=True)

    def _confirm_unwrapped_files(self):
        self._save_settings(silent=True)
        self._log(
            "Unwrapped files confirmed: "
            f"{len(self.unwrapped_elf_files)} ELF, "
            f"{len(self.unwrapped_prx_files)} PRX"
        )
        self._log(f"  ELF files: {self.unwrapped_elf_files}")
        self._log(f"  PRX files: {self.unwrapped_prx_files}")
        messagebox.showinfo(
            "Unwrapped files loaded",
            f"Loaded {len(self.unwrapped_elf_files)} ELF file(s) and "
            f"{len(self.unwrapped_prx_files)} PRX file(s).\n"
            "These paths are saved and available for import analysis, "
            "stub generation, or relinking.",
        )

    def _folder_row(self, parent, label, variable, browse_command):
        row = ttk.Frame(parent)
        row.pack(fill=tk.X, pady=4)
        ttk.Label(row, text=label, width=13).pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=variable).pack(
            side=tk.LEFT, padx=4, fill=tk.X, expand=True
        )
        ttk.Button(row, text="Browse", command=browse_command).pack(side=tk.LEFT)

    def _ui(self, callback, *args):
        """Schedule a UI operation on Tk's main thread."""
        self.root.after(0, lambda: callback(*args))

    def _log(self, msg):
        self._ui(self._append_log, str(msg))

    def _append_log(self, msg):
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)

    def _set_status(self, msg):
        self._ui(self.status.set, msg)

    def _set_progress(self, value, maximum=100):
        self._ui(self._update_progress, value, maximum)

    def _update_progress(self, value, maximum=100):
        self.progress["maximum"] = maximum
        self.progress["value"] = value

    def _browse_pkg_folder(self):
        folder = filedialog.askdirectory(
            initialdir=self.pkg_folder.get() or os.path.expanduser("~")
        )
        if folder:
            self.pkg_folder.set(folder)
            self._refresh_pkg_list()

    def _browse_output_folder(self):
        folder = filedialog.askdirectory(
            initialdir=self.output_folder.get() or os.path.expanduser("~")
        )
        if folder:
            self.output_folder.set(folder)

    def _browse_temp_folder(self):
        folder = filedialog.askdirectory(
            initialdir=self.temp_folder.get() or os.path.expanduser("~")
        )
        if folder:
            self.temp_folder.set(folder)

    def _browse_prx_source(self):
        folder = filedialog.askdirectory(
            initialdir=self.prx_source_dir.get() or os.path.expanduser("~")
        )
        if folder:
            self.prx_source_dir.set(folder)

    def _browse_relinker(self):
        folder = filedialog.askopenfilename(
            initialdir=os.path.dirname(self.relinker_path.get()) or os.path.expanduser("~"),
            title="Select relinker.exe",
            filetypes=[("Executable", "*.exe"), ("All files", "*.*")],
        )
        if folder:
            self.relinker_path.set(folder)

    def _browse_nid_patcher(self):
        folder = filedialog.askopenfilename(
            initialdir=os.path.dirname(self.nid_patcher_path.get()) or os.path.expanduser("~"),
            title="Select nid_patcher.exe",
            filetypes=[("Executable", "*.exe"), ("All files", "*.*")],
        )
        if folder:
            self.nid_patcher_path.set(folder)

    def _browse_nid_db(self):
        folder = filedialog.askopenfilename(
            initialdir=os.path.dirname(self.nid_db_path.get()) or os.path.expanduser("~"),
            title="Select NID database CSV or JSON",
            filetypes=[("CSV database", "*.csv"), ("JSON database", "*.json"), ("All files", "*.*")],
        )
        if folder:
            self.nid_db_path.set(folder)


    def _refresh_pkg_list(self):
        if not hasattr(self, "pkg_tree"):
            return
        for item in self.pkg_tree.get_children():
            self.pkg_tree.delete(item)
        self.pkg_list = []
        self.selected_pkgs.clear()

        folder = self.pkg_folder.get().strip()
        if not folder or not os.path.isdir(folder):
            return

        for path in sorted(Path(folder).rglob("*")):
            if path.is_file() and path.suffix.lower() == ".pkg":
                full_path = str(path)
                size = path.stat().st_size
                size_str = self._format_size(size)
                self.pkg_list.append(full_path)
                self.pkg_tree.insert(
                    "", tk.END, values=("", str(path.relative_to(folder)), size_str),
                    tags=(full_path,)
                )

    @staticmethod
    def _format_size(size_bytes):
        for unit in ("B", "KB", "MB", "GB"):
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"

    def _on_tree_click(self, event):
        if self.pkg_tree.identify_region(event.x, event.y) != "cell":
            return
        item = self.pkg_tree.identify_row(event.y)
        if not item or self.pkg_tree.identify_column(event.x) != "#1":
            return
        tags = self.pkg_tree.item(item, "tags")
        if not tags:
            return
        path = tags[0]
        if path in self.selected_pkgs:
            self.selected_pkgs.discard(path)
            self.pkg_tree.set(item, "select", "")
        else:
            self.selected_pkgs.add(path)
            self.pkg_tree.set(item, "select", "\u2713")
        return "break"

    def _select_all(self):
        children = self.pkg_tree.get_children()
        if children and all(
            self.pkg_tree.item(item, "tags")[0] in self.selected_pkgs
            for item in children
        ):
            self.selected_pkgs.clear()
            for item in children:
                self.pkg_tree.set(item, "select", "")
        else:
            for item in children:
                tags = self.pkg_tree.item(item, "tags")
                if tags:
                    self.selected_pkgs.add(tags[0])
                    self.pkg_tree.set(item, "select", "\u2713")


    def _auto_detect_tools(self):
        """Auto-detect tool paths if enabled."""
        if not self.auto_detect.get():
            return
        candidates = {
            "relinker_path": [
                os.path.abspath(os.path.join(BASE_DIR, "..", "AnyPS4", "build-relinker", "core", "relinker", "relinker.exe")),
                r"C:/PersonalProjects/AnyPs4/AnyPS4/build-relinker/core/relinker/relinker.exe",
            ],
            "nid_patcher_path": [
                os.path.abspath(os.path.join(BASE_DIR, "..", "AnyPS4", "build-full", "core", "libs", "nid_patcher.exe")),
                r"C:/PersonalProjects/AnyPs4/AnyPS4/build-full/core/libs/nid_patcher.exe",
            ],
            "prx_source_dir": [
                os.path.abspath(os.path.join(BASE_DIR, "..", "AnyPS4", "build-full", "core", "libs", "libs", "unpatched")),
                r"C:/PersonalProjects/AnyPs4/AnyPS4/build-full/core/libs/libs/unpatched",
            ],
        }
        for key, paths in candidates.items():
            var = getattr(self, key)
            current = var.get().strip()
            if current and os.path.exists(current):
                continue
            for p in paths:
                if os.path.exists(p):
                    var.set(p)
                    self._log(f"Auto-detected {key}: {p}")
                    break

    def _validate_setup(self):
        """Validate all required tools and paths before processing."""
        self._log("=== Validating setup ===")
        ok = True

        checks = [
            ("PKG folder", self.pkg_folder.get().strip(), lambda p: os.path.isdir(p)),
            ("Export folder", self.output_folder.get().strip(), lambda p: os.path.isdir(p) or self._try_mkdir(p)),
            ("Temp folder", self.temp_folder.get().strip(), lambda p: os.path.isdir(p) or self._try_mkdir(p)),
            ("PkgTool.exe", PKGTOOL_EXE, os.path.isfile),
            ("ps4_unfself.py", UNFSELF_PY, os.path.isfile),
            ("Relinker", self.relinker_path.get().strip(), os.path.isfile),
            ("NID patcher", self.nid_patcher_path.get().strip(), os.path.isfile),
        ]

        if self.copy_prx.get():
            prx_src = self.prx_source_dir.get().strip()
            checks.append(("PRX source dir", prx_src, lambda p: os.path.isdir(p) and any(Path(p).glob("*.prx"))))

        for name, path, check_fn in checks:
            if not path:
                self._log(f"  FAIL: {name} - not set")
                ok = False
            elif not check_fn(path):
                self._log(f"  FAIL: {name} - not found: {path}")
                ok = False
            else:
                self._log(f"  OK: {name} - {path}")

        # Check MinGW runtime DLLs
        self._log("  Checking MinGW runtime DLLs...")
        dll_found = False
        for dll_dir in [
            r"C:/winlibs/mingw64/bin",
            os.path.join(BASE_DIR, "mingw15", "mingw64", "bin"),
            os.path.join(BASE_DIR, "mingw16", "mingw64", "bin"),
            os.path.abspath(os.path.join(BASE_DIR, "..", "mingw16", "mingw64", "bin")),
            r"C:/PersonalProjects/AnyPs4/mingw16/mingw64/bin",
            r"C:/PersonalProjects/AnyPs4/mingw15/mingw64/bin",
        ]:
            if os.path.isdir(dll_dir):
                dlls = ["libgcc_s_seh-1.dll", "libstdc++-6.dll", "libwinpthread-1.dll"]
                missing = [d for d in dlls if not os.path.isfile(os.path.join(dll_dir, d))]
                if not missing:
                    self._log(f"  OK: MinGW runtime at {dll_dir}")
                    dll_found = True
                    break
                else:
                    self._log(f"  WARN: {dll_dir} missing: {', '.join(missing)}")
        if not dll_found:
            self._log("  WARN: No complete MinGW runtime DLL directory found")

        if ok:
            self._log("Setup validation PASSED")
            self.status.set("Validation passed")
        else:
            self._log("Setup validation FAILED - fix issues above")
            self.status.set("Validation failed")
        return ok

    @staticmethod
    def _try_mkdir(path):
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except OSError:
            return False


    # -------------------------------------------------------------- pipeline
    def _run_command(self, cmd, description):
        self._log("$ " + subprocess.list2cmdline(cmd))
        try:
            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, errors="replace", bufsize=1
            )
            if proc.stdout is not None:
                for line in proc.stdout:
                    self._log(line.rstrip())
            rc = proc.wait()
        except OSError as exc:
            raise RuntimeError(f"Could not start {description}: {exc}") from exc
        if rc != 0:
            raise RuntimeError(f"{description} exited with code {rc}")

    def _extract_pkg(self, pkg_path, out_dir):
        if not os.path.isfile(PKGTOOL_EXE):
            raise RuntimeError(f"PkgTool.exe not found: {PKGTOOL_EXE}")
        os.makedirs(out_dir, exist_ok=True)
        cmd = [
            PKGTOOL_EXE, "pkg_extract", "--passcode",
            self.passcode.get().strip() or ("0" * 32), pkg_path, out_dir
        ]
        self._run_command(cmd, "PkgTool extraction")

    def _unwrap_self(self, self_path, elf_path=None):
        if not os.path.isfile(UNFSELF_PY):
            raise RuntimeError(f"ps4_unfself.py not found: {UNFSELF_PY}")
        sys.path.insert(0, os.path.dirname(UNFSELF_PY))
        import ps4_unfself as unfself
        try:
            unfself.unwrap_self(self_path, elf_path, log=self._log)
        except Exception as exc:
            raise RuntimeError(f"SELF unwrap failed for {self_path}: {exc}") from exc
        if elf_path is not None and not os.path.isfile(elf_path):
            raise RuntimeError(f"ps4_unfself.py did not produce expected output: {elf_path}")

    def _find_eboot(self, extract_dir):
        """Find eboot.elf anywhere under uroot, with flexible search."""
        uroot = os.path.join(extract_dir, "uroot")
        if not os.path.isdir(uroot):
            return None
        eboot = os.path.join(uroot, "eboot.elf")
        if os.path.isfile(eboot):
            return eboot
        for p in Path(uroot).rglob("eboot.elf"):
            return str(p)
        for p in Path(uroot).rglob("*.elf"):
            return str(p)
        return None

    def _relink_eboot(self, extract_dir, out_dir):
        relinker = self.relinker_path.get().strip() or RELINKER_EXE
        if not os.path.isfile(relinker):
            raise RuntimeError(f"Relinker not found: {relinker}")

        eboot = self._find_eboot(extract_dir)
        if not eboot:
            raise RuntimeError(f"eboot.elf not found in {extract_dir}")

        os.makedirs(out_dir, exist_ok=True)
        out_exe = os.path.join(out_dir, "app.exe")
        cmd = [relinker, "--ps4", "--lazy-binding"]
        if self.skip_sce_module.get():
            cmd.append("--skip-sce-module")
        cmd += ["--windows", eboot, out_exe]
        self._run_command(cmd, "Relinker (Windows)")
        if not os.path.isfile(out_exe):
            raise RuntimeError(f"Relinker reported success but output is missing: {out_exe}")

        targets = self.settings.get("targets", ["windows"])
        if "linux" in targets:
            out_elf = os.path.join(out_dir, "app.elf")
            cmd_linux = [relinker, "--ps4", "--lazy-binding"]
            cmd_linux += [eboot, out_elf]
            self._run_command(cmd_linux, "Relinker (Linux)")

        return out_exe


    def _patch_nids(self, export_dir, log_cb=print):
        """Phase 2: Create NotImplemented stubs for unresolved imports.

        NID patching removed — app.exe's PE import table only has
        KERNEL32.dll, not PS4 imports, so the NID patcher cannot patch it.
        Phase 2 stubs are loaded by the runtime which scans all PRXs
        in libs/ (Option 2 approach, matching AnyPS5).
        """
        libs_dir = os.path.join(export_dir, "libs")
        if not os.path.isdir(libs_dir):
            log_cb("  SKIP Phase 2: export/libs/ not found")
            return

        log_cb("[4.6/5] Creating NotImplemented stubs for unresolved imports...")
        nid_db_path = self.nid_db_path.get().strip() or None
        create_missing_prx_stubs(export_dir, log_cb=self._log, nid_db_path=nid_db_path)

        # Remove intermediate export-list .txt files from libs/
        for txt_file in Path(libs_dir).glob("*_exports.txt"):
            try:
                txt_file.unlink()
            except OSError:
                pass

    def _process_single_pkg(self, pkg_path):
        pkg_name = Path(pkg_path).name
        safe_name = Path(pkg_name).stem
        for char in "[] ":
            safe_name = safe_name.replace(char, "_")
        extract_dir = os.path.join(self.temp_folder.get(), f"temp_{safe_name}")
        export_dir = os.path.join(self.output_folder.get(), f"export_{safe_name}")

        self._log(f"=== Processing: {pkg_name} ===")
        self._log(f"  extract dir: {extract_dir}")
        self._log(f"  export dir:  {export_dir}")

        self._log("[1/5] Extracting PKG...")
        self._extract_pkg(pkg_path, extract_dir)

        self._log("[2/5] Unwrapping SELF/ELF files...")
        uroot = os.path.join(extract_dir, "uroot")
        if not os.path.isdir(uroot):
            raise RuntimeError(f"No uroot directory after extraction in {uroot}")

        self_files = sorted(
            p for p in Path(uroot).rglob("*")
            if p.is_file() and p.suffix.lower() in (".elf", ".bin", ".prx", ".sprx")
        )
        if not self_files:
            raise RuntimeError(f"No SELF/ELF files found after extraction in {uroot}")

        elf_files = []
        for src_file in self_files:
            if src_file.suffix.lower() == ".elf":
                elf_files.append(src_file)
                self._log(f"  already ELF: {src_file.name}")
            else:
                elf_path = str(src_file.with_suffix(".elf"))
                self._log(f"  unwrapping {src_file.name} -> {Path(elf_path).name}...")
                self._unwrap_self(str(src_file), elf_path)
                elf_files.append(Path(elf_path))

        if not elf_files:
            raise RuntimeError(f"No .elf files found after unwrapping in {uroot}")
        self._log(f"  Unwrap done: {len(elf_files)} ELF file(s) ready")

        self._log("[3/5] Relinking to final binary...")
        out_exe = self._relink_eboot(extract_dir, export_dir)
        self._log(f"Output file: {out_exe}")

        # Deploy app0/ game assets and metadata
        self._log("  Deploying game assets to app0/...")
        app0_dir = os.path.join(export_dir, "app0")
        populate_app0(uroot, app0_dir, log_cb=self._log)

        # Detect Title ID & Name from PKG name
        tid_match = re.search(r'(CUSA\d{5})', pkg_name, re.IGNORECASE)
        title_id = tid_match.group(1).upper() if tid_match else None
        title_name = safe_name.replace("_", " ").strip()
        ensure_param_json(app0_dir, title_id=title_id, title_name=title_name, log_cb=self._log)

        if self.copy_prx.get():
            # Step 4a: Copy original game PRX files from uroot to export/libs/
            self._log("[4a/5] Copying original game PRX stubs from extraction...")
            libs_dir = os.path.join(export_dir, "libs")
            os.makedirs(libs_dir, exist_ok=True)
            orig_copied = 0
            orig_skipped = 0
            for src_file in Path(uroot).rglob("*.prx"):
                # Only copy Windows PE DLLs (MZ signature). Game PRX files from
                # uroot are ELF/SELF containers -- loading them as DLLs causes
                # "Bad Image" (0xc000012f). Build stubs overlay these later.
                try:
                    with open(src_file, "rb") as sf:
                        magic = sf.read(2)
                    if magic != b"MZ":
                        orig_skipped += 1
                        self._log(f"  SKIP (not a PE DLL): {src_file.name}")
                        continue
                except OSError:
                    pass
                dst = os.path.join(libs_dir, src_file.name)
                try:
                    shutil.copy2(str(src_file), dst)
                    orig_copied += 1
                except OSError as exc:
                    self._log(f"  WARN: could not copy {src_file.name}: {exc}")
            self._log(f"  Copied {orig_copied} original PRX stub(s) from uroot, "
                      f"skipped {orig_skipped} non-PE file(s)")

            # Step 4b: Overlay our custom PRX stubs on top
            prx_src = find_prx_source_dir(self.prx_source_dir.get().strip())
            if prx_src:
                self._log("[4b/5] Overlaying custom .prx stubs from build...")
                self._log(f"  source: {prx_src}")
                copied, skipped, errors = copy_prx_stubs(
                    prx_src, export_dir, log_cb=self._log
                )
                if errors:
                    raise RuntimeError(
                        f"{len(errors)} .prx copy error(s): " + "; ".join(errors)
                    )
                self._log(
                    f"  Copied {copied} custom .prx stub(s), {skipped} already up to date "
                    f"-> {os.path.join(export_dir, 'libs')}"
                )
            else:
                self._log("  WARN: No custom PRX build source found; skipping overlay")
        else:
            self._log("[4/5] Skipping .prx stub copy (disabled in options)")

        # Patch NIDs so the game calls our native PRX implementations
        if self.patch_nids.get():
            self._log("[4.5/5] Patching NIDs in app.exe...")
            self._patch_nids(export_dir, log_cb=self._log)

        # Copy toolchain runtime DLLs needed by .prx stubs (PE/DLL) to load.
        self._log("[5/5] Copying runtime DLLs...")
        mingw_candidates = [
            r"C:/winlibs/mingw64/bin",
            os.path.join(BASE_DIR, "mingw15", "mingw64", "bin"),
            os.path.join(BASE_DIR, "mingw16", "mingw64", "bin"),
            os.path.abspath(os.path.join(BASE_DIR, "..", "mingw16", "mingw64", "bin")),
            r"C:/PersonalProjects/AnyPs4/mingw16/mingw64/bin",
            r"C:/PersonalProjects/AnyPs4/mingw15/mingw64/bin",
        ]
        mingw_bin = None
        for c in mingw_candidates:
            if os.path.isdir(c):
                mingw_bin = c
                break
        if mingw_bin:
            self._log(f"  using runtime DLL source: {mingw_bin}")
            for dll in ("libgcc_s_seh-1.dll", "libstdc++-6.dll", "libwinpthread-1.dll"):
                src = os.path.join(mingw_bin, dll)
                dst = os.path.join(export_dir, dll)
                if os.path.isfile(src):
                    try:
                        shutil.copy2(src, dst)
                        self._log(f"  copied {dll}")
                    except OSError as exc:
                        self._log(f"  WARN: could not copy {dll}: {exc}")
        else:
            self._log("  WARN: runtime DLL directory not found; .prx stubs may fail to load")

        self._log(f"[OK] {pkg_name} complete -> {export_dir}")
        return export_dir


    def _start_processing(self):
        if self.worker_thread and self.worker_thread.is_alive():
            return
        if not self.selected_pkgs:
            messagebox.showwarning("No PKGs selected", "Select one or more PKG files first.")
            return
        if not self.output_folder.get().strip():
            messagebox.showerror("Missing output folder", "Please set an export folder.")
            return
        if not self.temp_folder.get().strip():
            messagebox.showerror("Missing temp folder", "Please set a temp folder.")
            return

        if not self._validate_setup():
            messagebox.showerror("Setup validation failed", "See log for details.")
            return

        self._save_settings(silent=True)
        self.stop_requested = False
        self.btn_process.config(state=tk.DISABLED)
        total = len(self.selected_pkgs)
        self._set_progress(0, total)
        self.worker_thread = threading.Thread(
            target=self._process_pipeline,
            args=(sorted(self.selected_pkgs),),
            daemon=True,
        )
        self.worker_thread.start()

    def _request_stop(self):
        self.stop_requested = True
        self._log("Stop requested; will stop before the next PKG.")

    def _process_pipeline(self, selected_pkgs):
        total = len(selected_pkgs)
        failures = 0
        for index, pkg_path in enumerate(selected_pkgs, 1):
            if self.stop_requested:
                self._log("Stopped by user.")
                break
            self._set_status(f"[{index}/{total}] {Path(pkg_path).name}")
            self._set_progress(index - 1, total)
            try:
                self._process_single_pkg(pkg_path)
            except Exception as exc:
                failures += 1
                self._log(f"FAIL: {pkg_path}: {exc}")
        if self.stop_requested:
            final_status = "Stopped"
        elif failures:
            final_status = f"Done with {failures} failure(s)"
        else:
            final_status = "Done"
        self._set_progress(total, total)
        self._ui(self._processing_finished, final_status)

    def _processing_finished(self, final_status):
        self.status.set(final_status)
        self.btn_process.config(state=tk.NORMAL)
        self.worker_thread = None

    def _save_settings(self, silent=False):
        self.settings.update({
            "pkg_folder": self.pkg_folder.get(),
            "output_folder": self.output_folder.get(),
            "temp_folder": self.temp_folder.get(),
            "relinker_path": self.relinker_path.get(),
            "nid_patcher_path": self.nid_patcher_path.get(),
            "passcode": self.passcode.get(),
            "skip_sce_module": self.skip_sce_module.get(),
            "copy_prx": self.copy_prx.get(),
            "patch_nids": self.patch_nids.get(),
            "prx_source_dir": self.prx_source_dir.get(),
            "nid_db_path": self.nid_db_path.get(),
            "unwrapped_elf_files": self.unwrapped_elf_files,
            "unwrapped_prx_files": self.unwrapped_prx_files,
        })
        save_settings(self.settings)
        if not silent:
            self._log("Settings saved.")


def run_nid_and_phase2(export_dir, log_cb=print):
    """Phase 2 stub creation (no GUI needed). NID patcher removed —
    app.exe's PE import table only has KERNEL32.dll, not PS4 imports,
    so the NID patcher cannot patch it. Phase 2 stubs are loaded by the
    runtime which scans all PRXs in libs/ (Option 2 approach)."""
    libs_dir = os.path.join(export_dir, "libs")
    if not os.path.isdir(libs_dir):
        log_cb("  SKIP: export/libs/ not found")
        return

    app_exe = os.path.join(export_dir, "app.exe")
    if not os.path.isfile(app_exe):
        log_cb("  SKIP: app.exe not found in export dir")
        return

    # Phase 2: Create NotImplemented stubs for unresolved imports
    log_cb("  Phase 2: Creating NotImplemented stubs for unresolved imports...")
    create_missing_prx_stubs(export_dir, log_cb=log_cb)

    # Remove intermediate export-list .txt files from libs/
    for txt_file in Path(libs_dir).glob("*_exports.txt"):
        try:
            txt_file.unlink()
        except OSError:
            pass


def main():
    if "--no-gui" in sys.argv:
        args = [arg for arg in sys.argv[1:] if arg != "--no-gui"]
        if not args:
            print("Usage: main_app.py --no-gui <export_dir>", file=sys.stderr)
            return 2
        export_dir = args[0]
        try:
            prx_src = find_prx_source_dir()
            if not prx_src:
                raise RuntimeError(
                    f"No .prx stub source found (tried {PRX_SOURCE_DIR} "
                    f"and {PRX_SOURCE_DIR_ALT})"
                )
            copied, skipped, errors = copy_prx_stubs(prx_src, export_dir)
            if errors:
                print(f"FAIL: {len(errors)} copy error(s): " + "; ".join(errors),
                      file=sys.stderr)
                return 1
            print(
                f"Copied {copied} .prx stub(s), {skipped} already up to date "
                f"-> {os.path.join(export_dir, 'libs')}"
            )

            # Run NID patching + Phase 2 stub creation
            run_nid_and_phase2(export_dir, log_cb=print)

            return 0
        except RuntimeError as exc:
            print(f"FAIL: {exc}", file=sys.stderr)
            return 1

    root = tk.Tk()
    App(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
