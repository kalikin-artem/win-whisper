"""Always-on-top status pill (bottom-right corner, above taskbar)."""

import ctypes
import ctypes.wintypes
import tkinter as tk

# Must be called before any Tk window, otherwise text renders blurry.
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    pass

_GWL_EXSTYLE = -20
_WS_EX_NOACTIVATE = 0x08000000
_WS_EX_TOOLWINDOW = 0x00000080


class Overlay:
    _BG = "#0c0c0c"
    _FG = "#f0f0f0"
    _FONT = ("Segoe UI", 9)
    _MARGIN_RIGHT = 12
    _MARGIN_BOTTOM = 8

    def __init__(self) -> None:
        self._root = tk.Tk()
        self._root.overrideredirect(True)
        self._root.attributes("-topmost", True)
        self._root.attributes("-alpha", 0.95)
        self._root.configure(bg=self._BG)

        self._label = tk.Label(
            self._root, bg=self._BG, fg=self._FG,
            font=self._FONT, padx=10, pady=4,
        )
        self._label.pack()
        self._root.withdraw()

        self._timer: str | None = None
        self._no_activate_applied = False

    def show(self, msg: str, ms: int = 0) -> None:
        self._root.after(0, self._show, msg, ms)

    def run(self) -> None:
        self._root.mainloop()

    def quit(self) -> None:
        self._root.after(0, self._root.quit)

    @staticmethod
    def _get_work_area() -> tuple[int, int, int, int]:
        rect = ctypes.wintypes.RECT()
        ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rect), 0)
        return rect.left, rect.top, rect.right, rect.bottom

    def _show(self, msg: str, ms: int) -> None:
        self._label.config(text=msg)
        self._root.update_idletasks()

        w = self._label.winfo_reqwidth()
        h = self._label.winfo_reqheight()
        _, _, wa_right, wa_bottom = self._get_work_area()
        self._root.geometry(
            f"{w}x{h}+{wa_right - w - self._MARGIN_RIGHT}+{wa_bottom - h - self._MARGIN_BOTTOM}"
        )

        self._root.deiconify()
        self._root.update()

        if not self._no_activate_applied:
            self._apply_no_activate()
            self._no_activate_applied = True

        if self._timer:
            self._root.after_cancel(self._timer)
            self._timer = None
        if ms > 0:
            self._timer = self._root.after(ms, self._hide)

    def _hide(self) -> None:
        self._root.withdraw()
        self._timer = None

    def _apply_no_activate(self) -> None:
        try:
            u32 = ctypes.windll.user32
            hwnd = int(self._root.frame(), 16)
            style = u32.GetWindowLongW(hwnd, _GWL_EXSTYLE)
            u32.SetWindowLongW(hwnd, _GWL_EXSTYLE, style | _WS_EX_NOACTIVATE | _WS_EX_TOOLWINDOW)
        except Exception:
            pass
