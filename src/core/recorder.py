"""Capture mouse activity using pynput.

Emits a list of event dicts (see storage.SCHEMA_VERSION) once ``stop()`` is
called. Move events are throttled to avoid huge files when the user moves the
mouse rapidly.
"""
from __future__ import annotations

import threading
import time
from typing import Callable, Optional

from pynput import mouse
from pynput.mouse import Button

_MOVE_THROTTLE_MS = 8  # ~125 events/sec max for movement


def _button_name(btn: Button) -> str:
    if btn == Button.left:
        return "left"
    if btn == Button.right:
        return "right"
    if btn == Button.middle:
        return "middle"
    return "unknown"


class MouseRecorder:
    """Listens to global mouse events and accumulates them with relative timestamps."""

    def __init__(
        self,
        on_event: Optional[Callable[[dict], None]] = None,
        move_throttle_ms: int = _MOVE_THROTTLE_MS,
        game_mode: bool = False,
    ) -> None:
        self._on_event = on_event
        self._move_throttle_ms = move_throttle_ms
        self._game_mode = game_mode
        self._events: list[dict] = []
        self._lock = threading.Lock()
        self._listener: mouse.Listener | None = None
        self._start_time: float = 0.0
        self._last_move_ms: int = -1_000_000
        self._last_x: int = 0
        self._last_y: int = 0
        self._running = False

    # --- public API ---
    @property
    def is_recording(self) -> bool:
        return self._running

    @property
    def event_count(self) -> int:
        with self._lock:
            return len(self._events)

    def start(self) -> None:
        if self._running:
            return
        self._events.clear()
        self._start_time = time.perf_counter()
        self._listener = mouse.Listener(
            on_move=self._on_move,
            on_click=self._on_click,
            on_scroll=self._on_scroll,
        )
        self._listener.start()
        self._running = True

    def stop(self) -> list[dict]:
        """Stop the listener and return the captured events (relative timestamps).

        Does NOT block the caller — the pynput listener is stopped in a
        short-lived daemon thread so the UI thread stays responsive.
        """
        if not self._running:
            return list(self._events)
        with self._lock:
            events = list(self._events)
        self._running = False
        if self._listener is not None:
            _old = self._listener
            self._listener = None

            def _do_stop():
                try:
                    _old.stop()
                except Exception:
                    pass

            threading.Thread(target=_do_stop, daemon=True).start()
        return events

    def get_events(self) -> list[dict]:
        with self._lock:
            return list(self._events)

    def set_game_mode(self, enabled: bool) -> None:
        self._game_mode = enabled

    # --- internal callbacks ---
    def _now_ms(self) -> int:
        return int((time.perf_counter() - self._start_time) * 1000)

    def _append(self, ev: dict) -> None:
        with self._lock:
            self._events.append(ev)
        if self._on_event is not None:
            try:
                self._on_event(ev)
            except Exception:
                pass

    def _on_move(self, x: int, y: int) -> None:
        now = self._now_ms()
        if (
            now - self._last_move_ms < self._move_throttle_ms
            and x == self._last_x
            and y == self._last_y
        ):
            return
        self._last_move_ms = now
        self._last_x, self._last_y = x, y
        self._append({"t": now, "type": "move", "x": int(x), "y": int(y)})

    def _on_click(self, x: int, y: int, button: Button, pressed: bool) -> None:
        self._append(
            {
                "t": self._now_ms(),
                "type": "click",
                "x": int(x),
                "y": int(y),
                "button": _button_name(button),
                "pressed": bool(pressed),
            }
        )

    def _on_scroll(self, x: int, y: int, dx: int, dy: int) -> None:
        self._append(
            {
                "t": self._now_ms(),
                "type": "scroll",
                "x": int(x),
                "y": int(y),
                "dx": int(dx),
                "dy": int(dy),
            }
        )
