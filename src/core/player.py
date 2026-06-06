"""Replay recorded mouse events with the original timing.

Runs in its own thread so the UI stays responsive. Cancellable via
``cancel()`` (used by the ESC hotkey).

Game mode playback:
  pynput's ``Controller`` uses ``SendInput`` which marks events as injected
  (``LLMHF_INJECTED``). Games using DirectInput / raw input often detect and
  ignore injected clicks. When ``game_mode=True``, clicks are sent via
  ``SendInput`` through ctypes with ``dwExtraInfo=0``, which some games
  interpret as a legitimate hardware event.
"""
from __future__ import annotations

import ctypes
import threading
import time
from ctypes import wintypes, byref, sizeof, Structure, Union, POINTER
from typing import Iterable, Optional

from pynput.mouse import Button, Controller

_BTN_MAP: dict[str, Button] = {
    "left": Button.left,
    "right": Button.right,
    "middle": Button.middle,
}

# Win32 SendInput types for game_mode clicks
class _MOUSEINPUT(Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", wintypes.LPARAM),
    ]

class _INPUT_UNION(Union):
    _fields_ = [("mi", _MOUSEINPUT)]

class _INPUT(Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("union", _INPUT_UNION),
    ]

INPUT_MOUSE = 0
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040

_user32 = ctypes.windll.user32
_SendInput = _user32.SendInput
_SendInput.argtypes = [wintypes.UINT, POINTER(_INPUT), ctypes.c_int]
_SendInput.restype = wintypes.UINT

_SetCursorPos = _user32.SetCursorPos
_SetCursorPos.argtypes = [ctypes.c_int, ctypes.c_int]
_SetCursorPos.restype = wintypes.BOOL

_CLICK_FLAGS = {
    ("left", True): MOUSEEVENTF_LEFTDOWN,
    ("left", False): MOUSEEVENTF_LEFTUP,
    ("right", True): MOUSEEVENTF_RIGHTDOWN,
    ("right", False): MOUSEEVENTF_RIGHTUP,
    ("middle", True): MOUSEEVENTF_MIDDLEDOWN,
    ("middle", False): MOUSEEVENTF_MIDDLEUP,
}


class MousePlayer:
    def __init__(self, game_mode: bool = False) -> None:
        self._mouse = Controller()
        self._game_mode = game_mode
        self._thread: threading.Thread | None = None
        self._cancel = threading.Event()
        self._done = threading.Event()
        self._on_done: Optional[Callable[[], None]] = None
        self._on_progress: Optional[Callable[[int, int], None]] = None  # (idx, total)

    # --- public API ---
    @property
    def is_playing(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def set_game_mode(self, enabled: bool) -> None:
        self._game_mode = enabled

    def play(
        self,
        events: Iterable[dict],
        on_done: Optional[Callable[[], None]] = None,
        on_progress: Optional[Callable[[int, int], None]] = None,
    ) -> bool:
        """Start playback in a background thread. Returns False if already playing."""
        if self.is_playing:
            return False
        evs = list(events)
        if not evs:
            if on_done is not None:
                on_done()
            return True

        self._cancel.clear()
        self._done.clear()
        self._on_done = on_done
        self._on_progress = on_progress
        self._thread = threading.Thread(
            target=self._run, args=(evs,), daemon=True, name="MousePlayer"
        )
        self._thread.start()
        return True

    def cancel(self) -> None:
        self._cancel.set()

    def wait(self, timeout: Optional[float] = None) -> bool:
        return self._done.wait(timeout)

    # --- internals ---
    def _run(self, events: list[dict]) -> None:
        try:
            start = time.perf_counter()
            total = len(events)
            for i, ev in enumerate(events):
                if self._cancel.is_set():
                    break
                target_ms = int(ev.get("t", 0))
                elapsed_ms = (time.perf_counter() - start) * 1000.0
                wait_ms = target_ms - elapsed_ms
                if wait_ms > 0:
                    # sleep in small chunks so cancel is responsive
                    end = time.perf_counter() + wait_ms / 1000.0
                    while not self._cancel.is_set():
                        now = time.perf_counter()
                        if now >= end:
                            break
                        time.sleep(min(0.02, end - now))
                if self._cancel.is_set():
                    break
                self._play_event(ev)
                if self._on_progress is not None:
                    try:
                        self._on_progress(i + 1, total)
                    except Exception:
                        pass
        finally:
            self._done.set()
            cb = self._on_done
            self._on_done = None
            self._on_progress = None
            if cb is not None:
                try:
                    cb()
                except Exception:
                    pass

    def _play_event(self, ev: dict) -> None:
        typ = ev.get("type")
        try:
            if typ == "move":
                self._mouse.position = (int(ev.get("x", 0)), int(ev.get("y", 0)))
            elif typ == "click":
                x = int(ev.get("x", 0))
                y = int(ev.get("y", 0))
                btn_name = ev.get("button", "left")
                pressed = bool(ev.get("pressed", True))
                if self._game_mode:
                    self._send_click_ctypes(x, y, btn_name, pressed)
                else:
                    btn = _BTN_MAP.get(btn_name, Button.left)
                    if pressed:
                        self._mouse.position = (x, y)
                        self._mouse.press(btn)
                    else:
                        self._mouse.position = (x, y)
                        self._mouse.release(btn)
            elif typ == "scroll":
                x = int(ev.get("x", 0))
                y = int(ev.get("y", 0))
                dx = int(ev.get("dx", 0))
                dy = int(ev.get("dy", 0))
                self._mouse.position = (x, y)
                self._mouse.scroll(dx, dy)
        except Exception:
            pass

    def _send_click_ctypes(self, x: int, y: int, button: str, pressed: bool) -> None:
        """Send a mouse click via SendInput with dwExtraInfo=0.

        Games using DirectInput often check ``GetMessageExtraInfo()`` for the
        injected flag. By setting dwExtraInfo to 0 (instead of pynput's default),
        we masquerade as a legitimate hardware event.
        """
        flags = _CLICK_FLAGS.get((button, pressed))
        if flags is None:
            return
        _SetCursorPos(x, y)
        inp = _INPUT()
        inp.type = INPUT_MOUSE
        inp.union.mi.dx = 0
        inp.union.mi.dy = 0
        inp.union.mi.mouseData = 0
        inp.union.mi.dwFlags = flags
        inp.union.mi.time = 0
        inp.union.mi.dwExtraInfo = 0
        _SendInput(1, byref(inp), sizeof(_INPUT))
