"""Win Whisper — local, offline voice-to-text for Windows."""

import sys
from pathlib import Path

VERSION = "1.0.1"

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
    BUNDLE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).resolve().parent.parent
    BUNDLE_DIR = BASE_DIR
