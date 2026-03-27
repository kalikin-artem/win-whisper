# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec — produces a single win-whisper.exe in dist/"""

import site
from pathlib import Path

_site = Path(site.getsitepackages()[0])
_fw_dir = _site / "faster_whisper"

a = Analysis(
    ["win_whisper/__main__.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("icons", "icons"),
        (str(_fw_dir / "assets"), "faster_whisper/assets"),
    ],
    hiddenimports=[
        "faster_whisper",
        "ctranslate2",
        "huggingface_hub",
        "tokenizers",
        "sounddevice",
        "_sounddevice_data",
        "numpy",
        "pynput",
        "pynput.keyboard",
        "pynput.keyboard._win32",
        "pystray",
        "pystray._win32",
        "PIL",
        "PIL.Image",
        "PIL.ImageDraw",
        "PIL.ImageEnhance",
    ],
    excludes=["pytest", "IPython", "notebook", "matplotlib"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="win-whisper",
    debug=False,
    strip=False,
    upx=True,
    console=False,
    icon="icons/icon.ico",
)
