"""Poll-based watcher for Windows Toast notifications via wpndatabase.db."""
from __future__ import annotations

import sqlite3
import threading
import time
from typing import Callable, Optional

from src.utils.paths import notifications_db_path


def get_available_apps() -> list[str]:
    """Return sorted list of AppIds that have sent notifications recently."""
    db = notifications_db_path()
    if not db.exists():
        return []
    try:
        conn = sqlite3.connect(str(db))
        try:
            cursor = conn.execute(
                "SELECT DISTINCT h.PrimaryId"
                " FROM Notification n"
                " JOIN NotificationHandler h ON n.HandlerId = h.RecordId"
                " WHERE h.PrimaryId IS NOT NULL AND h.PrimaryId != ''"
                " ORDER BY h.PrimaryId"
            )
            return [r[0] for r in cursor.fetchall()]
        finally:
            conn.close()
    except (sqlite3.Error, OSError):
        return []


def _parse_toast_text(payload: str) -> str:
    """Extract human-readable text from a Toast XML payload."""
    texts = []
    i = 0
    while True:
        start = payload.find("<text>", i)
        if start == -1:
            break
        end = payload.find("</text>", start)
        if end == -1:
            break
        texts.append(payload[start + 6 : end])
        i = end + 7
    return " | ".join(texts) if texts else payload[:200]


class NotificationWatcher:
    """Polls wpndatabase.db from a daemon thread for new notifications.

    Calls ``callback(payload_xml, payload_text, app_id)`` on the background
    thread for each new notification detected across all apps.
    """

    POLL_INTERVAL = 0.5

    def __init__(self) -> None:
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._callback: Optional[Callable[[str, str, str], None]] = None
        self._last_max_id = 0

    def start(self, callback: Callable[[str, str, str], None]) -> None:
        self._callback = callback
        self._last_max_id = self._query_max_id()
        self._running = True
        self._thread = threading.Thread(target=self._poll, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        self._thread = None

    @property
    def is_running(self) -> bool:
        return self._running

    def _poll(self) -> None:
        while self._running:
            try:
                self._check()
            except Exception:
                pass
            time.sleep(self.POLL_INTERVAL)

    def _check(self) -> None:
        db = notifications_db_path()
        if not db.exists():
            return
        try:
            conn = sqlite3.connect(str(db))
        except sqlite3.Error:
            return
        try:
            cursor = conn.execute(
                "SELECT n.Id, n.Payload, h.PrimaryId"
                " FROM Notification n"
                " JOIN NotificationHandler h ON n.HandlerId = h.RecordId"
                " WHERE n.Id > ?"
                " ORDER BY n.Id",
                (self._last_max_id,),
            )
            new_max = self._last_max_id
            for row in cursor.fetchall():
                nid, payload_blob, app_id = row
                if nid > new_max:
                    new_max = nid
                if payload_blob:
                    payload = payload_blob.decode("utf-8", errors="replace")
                    text = _parse_toast_text(payload)
                    if self._callback:
                        self._callback(payload, text, app_id or "?")
            self._last_max_id = new_max
        finally:
            conn.close()

    def _query_max_id(self) -> int:
        try:
            conn = sqlite3.connect(str(notifications_db_path()))
            try:
                cursor = conn.execute(
                    "SELECT COALESCE(MAX(Id), 0) FROM Notification"
                )
                row = cursor.fetchone()
                return row[0] if row else 0
            finally:
                conn.close()
        except (sqlite3.Error, OSError, AttributeError):
            return 0
