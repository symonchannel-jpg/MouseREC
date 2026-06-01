"""Replay recorded mouse events with the original timing.

Runs in its own thread so the UI stays responsive. Cancellable via
``cancel()`` (used by the ESC hotkey).
"""
from __future__ import annotations

import threading
import time
from typing import Iterable, Optional

from pynput.mouse import Button, Controller

_BTN_MAP: dict[str, Button] = {
    "left": Button.left,
    "right": Button.right,
    "middle": Button.middle,
}


class MousePlayer:
    def __init__(self) -> None:
        self._mouse = Controller()
        self._thread: threading.Thread | None = None
        self._cancel = threading.Event()
        self._done = threading.Event()
        self._on_done: Optional[Callable[[], None]] = None
        self._on_progress: Optional[Callable[[int, int], None]] = None  # (idx, total)

    # --- public API ---
    @property
    def is_playing(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

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
                btn = _BTN_MAP.get(ev.get("button", "left"), Button.left)
                pressed = bool(ev.get("pressed", True))
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
            # Never let a single bad event kill playback
            pass
