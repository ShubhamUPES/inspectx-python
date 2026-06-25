# -*- mode: python ; coding: utf-8 -*-
"""
InspectX — PyInstaller build spec
Build:  pyinstaller inspectx.spec
Output: dist/InspectX/   (one-folder bundle)

Why one-folder instead of --onefile?
  PyQt6 ships large shared libraries.  --onefile works but forces a slow
  extraction to %TEMP% on every launch (5-15 s on Windows).  One-folder
  starts in under 2 s and is still easy to zip for distribution.
"""

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# ── Hidden imports PyInstaller misses ─────────────────────────────────────────
hidden = [
    "PyQt6.QtCore",
    "PyQt6.QtGui",
    "PyQt6.QtWidgets",
    "sqlalchemy.dialects.sqlite",
    "sqlalchemy.pool",
    "bcrypt",
    "PIL._imaging",
    "PIL.Image",
]
hidden += collect_submodules("sqlalchemy")

# ── Data files ────────────────────────────────────────────────────────────────
datas = [
    ("assets",            "assets"),           # logo + README
    ("app/database/inspectx.db", "app/database"),  # pre-seeded DB shipped with bundle
]
datas += collect_data_files("PyQt6")

# ── Analysis ──────────────────────────────────────────────────────────────────
a = Analysis(
    ["main.py"],
    pathex=["."],
    binaries=[],
    datas=datas,
    hiddenimports=hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "numpy", "pandas", "scipy"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="InspectX",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # no terminal window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="assets/hestabit-logo.jpg",   # swap for a .ico/.icns for a real icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="InspectX",
)

# ── macOS .app bundle ─────────────────────────────────────────────────────────
app = BUNDLE(
    coll,
    name="InspectX.app",
    icon="assets/hestabit-logo.jpg",
    bundle_identifier="ai.inspectx.desktop",
    info_plist={
        "NSPrincipalClass": "NSApplication",
        "NSHighResolutionCapable": True,
        "CFBundleShortVersionString": "1.0.0",
    },
)
