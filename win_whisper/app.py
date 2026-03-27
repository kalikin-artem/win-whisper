"""System-tray icon, global hotkeys, paste workflow."""

import os
import threading
import time

import pystray
from PIL import Image, ImageDraw, ImageEnhance
from pynput import keyboard as kb

from . import BUNDLE_DIR, VERSION
from .engine import Engine
from .log import log
from .overlay import Overlay
from .win32 import clip_get, clip_set, focus_window, get_foreground_window, send_hotkey

_ICONS_DIR = BUNDLE_DIR / "icons"
_REPO_URL = "https://github.com/kalikin-artem/win-whisper"

_READY = "ready"
_LOADING = "loading"
_RECORDING = "recording"
_ERROR = "error"


class App:
    MODELS = ["tiny", "base", "small", "medium"]

    def __init__(
        self, *,
        model_size: str = "base",
        hotkey: str = "f9",
        paste_hotkey: str = "ctrl+v",
        language: str | None = None,
        device: str = "cpu",
    ) -> None:
        self._overlay = Overlay()
        self._engine = Engine()
        self._model_size = model_size
        self._device = device
        self._hotkey = getattr(kb.Key, hotkey.lower(), kb.Key.f9)
        self._hotkey_name = hotkey.upper()
        self._paste_hotkey = paste_hotkey
        self._language = language
        self._recording = False
        self._stop = threading.Event()
        self._target_hwnd: int = 0
        self._listener: kb.Listener | None = None
        self._tray: pystray.Icon | None = None
        self._base_icon: Image.Image = self._load_icon()

    # -- tray --

    @staticmethod
    def _load_icon() -> Image.Image:
        path = _ICONS_DIR / "icon_64.png"
        if path.exists():
            return Image.open(path).convert("RGBA")
        img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        ImageDraw.Draw(img).ellipse([6, 6, 58, 58], fill="#4c8bf5")
        return img

    @staticmethod
    def _tint_icon(icon: Image.Image, state: str) -> Image.Image:
        if state == _READY:
            return icon.copy()
        img = icon.copy()
        if state == _LOADING:
            return ImageEnhance.Brightness(img).enhance(0.6)
        if state == _RECORDING:
            overlay = Image.new("RGBA", img.size, (220, 40, 40, 120))
            return Image.alpha_composite(img, overlay)
        if state == _ERROR:
            return ImageEnhance.Color(img).enhance(0.3)
        return img

    def _build_tray(self) -> None:
        def model_item(m: str) -> pystray.MenuItem:
            return pystray.MenuItem(
                m, lambda *_, m=m: self._change_model(m),
                checked=lambda item, m=m: self._model_size == m, radio=True,
            )

        menu = pystray.Menu(
            pystray.MenuItem(
                lambda _: f"Faster Whisper: {self._model_size}",
                pystray.Menu(*[model_item(m) for m in self.MODELS]),
            ),
            pystray.MenuItem("Reload model", lambda *_: self._reload()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(f"Win Whisper v{VERSION}", None, enabled=False),
            pystray.MenuItem("Artem Kalikin  <artem@kalikin.org>", None, enabled=False),
            pystray.MenuItem("GitHub", lambda *_: os.startfile(_REPO_URL)),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", lambda *_: self._exit()),
        )
        self._tray = pystray.Icon(
            "Win Whisper", self._base_icon.copy(),
            f"Win Whisper v{VERSION}  |  {self._hotkey_name} = record & paste", menu,
        )
        self._tray.run_detached()

    def _set_state(self, state: str) -> None:
        if self._tray:
            self._tray.icon = self._tint_icon(self._base_icon, state)

    # -- model --

    def _change_model(self, model: str) -> None:
        if model == self._model_size and self._engine.model is not None:
            return
        self._model_size = model
        self._reload()

    def _reload(self) -> None:
        if self._recording:
            self._recording = False
            self._stop.set()
        self._engine.model = None
        threading.Thread(target=self._load_model, daemon=True).start()

    def _load_model(self) -> None:
        self._set_state(_LOADING)
        self._overlay.show(f"Loading {self._model_size}...")
        try:
            self._engine.load(self._model_size, device=self._device)
            self._set_state(_READY)
            self._overlay.show("Ready", ms=2000)
        except Exception as e:
            log.error("Model load failed: %s", e)
            self._set_state(_ERROR)
            self._overlay.show("Load failed", ms=5000)

    # -- recording --

    def _on_press(self, key: kb.Key) -> None:
        if key == self._hotkey and not self._recording and self._engine.model:
            self._target_hwnd = get_foreground_window()
            self._recording = True
            self._stop.clear()
            self._set_state(_RECORDING)
            self._overlay.show("Recording...")
            threading.Thread(target=self._process, daemon=True).start()

    def _on_release(self, key: kb.Key) -> None:
        if key == self._hotkey and self._recording:
            self._stop.set()

    def _process(self) -> None:
        try:
            audio = self._engine.record(self._stop)
        except Exception as e:
            log.error("Audio error: %s", e)
            audio = None
        finally:
            self._recording = False
            self._set_state(_READY)

        if audio is None:
            self._overlay.show("Too short", ms=1500)
            return

        self._overlay.show("Transcribing...")
        try:
            text = self._engine.transcribe(audio, language=self._language)
        except Exception as e:
            log.error("Transcription error: %s", e)
            self._overlay.show("Error", ms=3000)
            return

        if not text:
            self._overlay.show("No speech", ms=2000)
            return

        saved = clip_get()
        clip_set(text)
        time.sleep(0.1)
        focus_window(self._target_hwnd)
        time.sleep(0.05)
        send_hotkey(self._paste_hotkey)
        time.sleep(0.2)
        clip_set(saved)
        self._overlay.show("Pasted", ms=1500)

    # -- lifecycle --

    def _exit(self) -> None:
        self._recording = False
        self._stop.set()
        if self._tray:
            self._tray.stop()
        if self._listener:
            self._listener.stop()
        self._overlay.quit()

    def run(self) -> None:
        log.info(
            "Win Whisper v%s  model=%s  device=%s  hotkey=%s  paste=%s  lang=%s",
            VERSION, self._model_size, self._device, self._hotkey_name,
            self._paste_hotkey, self._language,
        )
        self._build_tray()
        threading.Thread(target=self._load_model, daemon=True).start()
        self._listener = kb.Listener(on_press=self._on_press, on_release=self._on_release)
        self._listener.start()
        try:
            self._overlay.run()
        finally:
            self._listener.stop()
            log.info("Stopped.")
