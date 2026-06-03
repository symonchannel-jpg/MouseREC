"""Global hotkey listener.

Default: F9 = play last recording, ESC = cancel playback.
"""
from __future__ import annotations

import threading
from typing import Callable, Optional

from pynput import keyboard


class HotkeyManager:
    def __init__(
        self,
        on_play: Optional[Callable[[], None]] = None,
        on_cancel: Optional[Callable[[], None]] = None,
    ) -> None:
        self._on_play = on_play
        self._on_cancel = on_cancel
        self._listener: keyboard.Listener | None = None
        self._pressed: set[keyboard.Key | keyboard.KeyCode] = set()
        self._lock = threading.Lock()
        self._play_key = keyboard.Key.f9
        self._cancel_key = keyboard.Key.esc

    @property
    def is_active(self) -> bool:
        return self._listener is not None and self._listener.is_alive()

    def set_callbacks(
        self,
        on_play: Optional[Callable[[], None]] = None,
        on_cancel: Optional[Callable[[], None]] = None,
    ) -> None:
        with self._lock:
            if on_play is not None:
                self._on_play = on_play
            if on_cancel is not None:
                self._on_cancel = on_cancel

    def start(self) -> bool:
        if self.is_active:
            return True
        self._pressed.clear()
        self._listener = keyboard.Listener(
            on_press=self._on_press, on_release=self._on_release
        )
        try:
            self._listener.start()
            return True
        except Exception:
            self._listener = None
            return False

    def stop(self) -> None:
        if self._listener is not None:
            try:
                self._listener.stop()
            except Exception:
                pass
            self._listener = None
        self._pressed.clear()

    # --- internals ---
    def _on_press(self, key) -> None:
        with self._lock:
            self._pressed.add(key)
            cb = self._on_play
        if key == self._play_key and cb is not None:
            try:
                cb()
            except Exception:
                pass

    def _on_release(self, key) -> None:
        with self._lock:
            self._pressed.discard(key)
            cb = self._on_cancel
        if key == self._cancel_key and cb is not None:
            try:
                cb()
            except Exception:
                pass
