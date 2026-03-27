"""Logging — file + optional console."""

import logging
import sys

from . import BASE_DIR

_log_path = BASE_DIR / "win-whisper.log"

_handlers: list[logging.Handler] = [
    logging.FileHandler(_log_path, encoding="utf-8"),
]
# sys.stdout is None when running via pythonw.exe
if sys.stdout:
    _handlers.append(logging.StreamHandler(sys.stdout))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=_handlers,
)

log = logging.getLogger("win_whisper")
