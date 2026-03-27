"""Win32 helpers: clipboard, SendInput, window focus.

Pointer-returning calls use ``restype = c_void_p`` to prevent
ctypes from truncating 64-bit addresses.
"""

import ctypes
import ctypes.wintypes

from .log import log

_u32 = ctypes.windll.user32
_k32 = ctypes.windll.kernel32

_u32.GetForegroundWindow.restype = ctypes.c_void_p
_u32.GetClipboardData.restype = ctypes.c_void_p
_k32.GlobalAlloc.restype = ctypes.c_void_p
_k32.GlobalAlloc.argtypes = [ctypes.c_uint, ctypes.c_size_t]
_k32.GlobalLock.restype = ctypes.c_void_p
_k32.GlobalLock.argtypes = [ctypes.c_void_p]
_k32.GlobalUnlock.argtypes = [ctypes.c_void_p]
_u32.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]

CF_UNICODETEXT = 13


def clip_get() -> str:
    if not _u32.IsClipboardFormatAvailable(CF_UNICODETEXT):
        return ""
    try:
        _u32.OpenClipboard(None)
        try:
            h = _u32.GetClipboardData(CF_UNICODETEXT)
            if not h:
                return ""
            ptr = _k32.GlobalLock(h)
            try:
                return ctypes.wstring_at(ptr)
            finally:
                _k32.GlobalUnlock(h)
        finally:
            _u32.CloseClipboard()
    except Exception as e:
        log.error("Clipboard read error: %s", e)
        return ""


def clip_set(text: str) -> None:
    try:
        enc = text.encode("utf-16-le") + b"\x00\x00"
        _u32.OpenClipboard(None)
        try:
            _u32.EmptyClipboard()
            h = _k32.GlobalAlloc(0x0002, len(enc))
            ptr = _k32.GlobalLock(h)
            ctypes.memmove(ptr, enc, len(enc))
            _k32.GlobalUnlock(h)
            _u32.SetClipboardData(CF_UNICODETEXT, h)
        finally:
            _u32.CloseClipboard()
    except Exception as e:
        log.error("Clipboard write error: %s", e)


# sizeof(INPUT) on 64-bit Windows = 40 bytes. The union must include
# MOUSEINPUT (32 bytes) for correct struct size; KEYBDINPUT alone is
# 24 bytes, making sizeof(INPUT)=32, which causes SendInput to silently
# reject every call.

class _MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long), ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong), ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong), ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


class _KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.wintypes.WORD), ("wScan", ctypes.wintypes.WORD),
        ("dwFlags", ctypes.wintypes.DWORD), ("time", ctypes.wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


class _INPUT(ctypes.Structure):
    class _U(ctypes.Union):
        _fields_ = [("mi", _MOUSEINPUT), ("ki", _KEYBDINPUT)]
    _anonymous_ = ("_u",)
    _fields_ = [("type", ctypes.wintypes.DWORD), ("_u", _U)]


_VK: dict[str, int] = {
    "ctrl": 0x11, "control": 0x11, "alt": 0x12, "shift": 0x10, "win": 0x5B,
    **{chr(0x61 + i): 0x41 + i for i in range(26)},
    **{str(i): 0x30 + i for i in range(10)},
}


def send_hotkey(combo: str) -> None:
    null = ctypes.cast(0, ctypes.POINTER(ctypes.c_ulong))
    vks = [
        _VK[p]
        for p in (part.strip().lower() for part in combo.split("+"))
        if p in _VK
    ]
    if not vks:
        log.error("Unknown hotkey: %r", combo)
        return
    downs = [_INPUT(type=1, ki=_KEYBDINPUT(wVk=v, dwExtraInfo=null)) for v in vks]
    ups = [
        _INPUT(type=1, ki=_KEYBDINPUT(wVk=v, dwFlags=0x0002, dwExtraInfo=null))
        for v in reversed(vks)
    ]
    seq = (_INPUT * len(downs + ups))(*downs, *ups)
    _u32.SendInput(len(seq), seq, ctypes.sizeof(_INPUT))


def get_foreground_window() -> int:
    return _u32.GetForegroundWindow() or 0


def focus_window(hwnd: int) -> None:
    if not hwnd:
        return
    try:
        fg = _u32.GetForegroundWindow()
        fg_tid = _u32.GetWindowThreadProcessId(fg, None)
        my_tid = _k32.GetCurrentThreadId()
        _u32.AttachThreadInput(my_tid, fg_tid, True)
        _u32.SetForegroundWindow(hwnd)
        _u32.BringWindowToTop(hwnd)
        _u32.AttachThreadInput(my_tid, fg_tid, False)
    except Exception:
        pass
