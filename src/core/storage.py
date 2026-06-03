"""Save/load recordings in the .mrcd JSON format.

Schema (v1)::

    {
        "version": 1,
        "name": "string",
        "created_at": "ISO-8601",
        "events": [
            {"t": int_ms, "type": "move",   "x": int, "y": int},
            {"t": int_ms, "type": "click",  "x": int, "y": int, "button": "left"|"right"|"middle", "pressed": bool},
            {"t": int_ms, "type": "scroll", "x": int, "y": int, "dx": int, "dy": int}
        ]
    }
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from src.utils.paths import recordings_dir

SCHEMA_VERSION = 1
_NAME_RE = re.compile(r"[^A-Za-z0-9 _\-]+")
_VALID_TYPES = {"move", "click", "scroll"}
_VALID_BUTTONS = {"left", "right", "middle"}


def sanitize_filename(name: str) -> str:
    """Make a name safe to use as a filename (keeps spaces, _, -)."""
    name = (name or "").strip()
    if not name:
        name = "recording"
    name = _NAME_RE.sub("", name)
    name = name.strip().strip(".")
    return name[:80] or "recording"


def _validate_event(ev: Any) -> dict:
    if not isinstance(ev, dict):
        raise ValueError(f"invalid event: {ev!r}")
    t = ev.get("t")
    if not isinstance(t, int) or t < 0:
        raise ValueError(f"invalid timestamp: {t!r}")
    typ = ev.get("type")
    if typ not in _VALID_TYPES:
        raise ValueError(f"invalid event type: {typ!r}")
    if typ == "move":
        for k in ("x", "y"):
            if not isinstance(ev.get(k), int):
                raise ValueError(f"move requires x/y int: {ev!r}")
    elif typ == "click":
        for k in ("x", "y"):
            if not isinstance(ev.get(k), int):
                raise ValueError(f"click requires x/y int: {ev!r}")
        btn = ev.get("button", "left")
        if btn not in _VALID_BUTTONS:
            raise ValueError(f"invalid button: {btn!r}")
        ev = {**ev, "button": btn, "pressed": bool(ev.get("pressed", True))}
    elif typ == "scroll":
        for k in ("x", "y", "dx", "dy"):
            if not isinstance(ev.get(k), int):
                raise ValueError(f"scroll requires x/y/dx/dy int: {ev!r}")
    return ev


def _validate_payload(data: Any) -> dict:
    if not isinstance(data, dict):
        raise ValueError("file is not a JSON object")
    if data.get("version") != SCHEMA_VERSION:
        raise ValueError(
            f"unsupported version: {data.get('version')!r} (expected {SCHEMA_VERSION})"
        )
    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("missing 'name'")
    events = data.get("events")
    if not isinstance(events, list):
        raise ValueError("missing 'events' (list)")
    if len(events) > 1_000_000:
        raise ValueError("too many events (>1M), suspicious file")
    return {
        "version": SCHEMA_VERSION,
        "name": name.strip()[:80],
        "created_at": str(data.get("created_at", ""))[:40],
        "events": [_validate_event(e) for e in events],
    }


@dataclass
class Recording:
    """In-memory representation of a recording."""

    name: str
    events: list[dict] = field(default_factory=list)
    created_at: str = ""

    def to_dict(self) -> dict:
        return {
            "version": SCHEMA_VERSION,
            "name": self.name,
            "created_at": self.created_at,
            "events": list(self.events),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Recording":
        return cls(
            name=data["name"],
            events=list(data.get("events", [])),
            created_at=data.get("created_at", ""),
        )


def recording_path(name: str) -> Path:
    safe = sanitize_filename(name)
    return recordings_dir() / f"{safe}.mrcd"


def save_recording(name: str, events: Iterable[dict], path: Path | None = None) -> Path:
    """Persist a recording. Returns the written file path."""
    rec = Recording(
        name=sanitize_filename(name),
        events=list(events),
        created_at=datetime.now().isoformat(timespec="seconds"),
    )
    target = path or recording_path(rec.name)
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        json.dump(rec.to_dict(), f, indent=2, ensure_ascii=False)
    return target


def load_recording(path: Path) -> Recording:
    """Read and validate a .mrcd file."""
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    validated = _validate_payload(raw)
    return Recording.from_dict(validated)


def list_recordings() -> list[Path]:
    """Return available .mrcd files in the recordings directory, sorted by mtime desc."""
    d = recordings_dir()
    return sorted(d.glob("*.mrcd"), key=lambda p: p.stat().st_mtime, reverse=True)
