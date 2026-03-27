"""Win Whisper — local, offline voice-to-text for Windows."""

import sys
from pathlib import Path

VERSION = "1.0"

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent
