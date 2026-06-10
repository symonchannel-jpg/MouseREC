"""Main application window — frameless solid dark UI."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, QPoint, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QCloseEvent, QIcon
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.core.hotkey import HotkeyManager
from src.core.notification_watcher import NotificationWatcher
from src.core.player import MousePlayer
from src.core.recorder import MouseRecorder
from src.core.storage import (
    Recording,
    list_recordings,
    load_recording,
    rename_recording,
    save_recording,
)
from src.ui.theme import QSS
from src.ui.widgets import GlassCard, GlowButton, StatusPill
from src.utils.paths import assets_dir, recordings_dir


# --- Custom title bar ---
class TitleBar(QFrame):
    """Frameless title bar: draggable, with app title and min/close buttons."""

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setObjectName("titleBar")
        self.setFixedHeight(34)
        self._parent = parent
        self._drag_pos: Optional[QPoint] = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 6, 0)
        layout.setSpacing(6)

        self._title = QLabel("MouseRecorder")
        self._title.setObjectName("title")
        layout.addWidget(self._title)
        layout.addStretch(1)

        self._min_btn = QPushButton("—")
        self._min_btn.setObjectName("titleBtn")
        self._min_btn.setCursor(Qt.PointingHandCursor)
        self._min_btn.clicked.connect(parent.showMinimized)
        layout.addWidget(self._min_btn)

        self._close_btn = QPushButton("✕")
        self._close_btn.setObjectName("titleBtn")
        self._close_btn.setProperty("class", "close")
        self._close_btn.setCursor(Qt.PointingHandCursor)
        self._close_btn.clicked.connect(parent.close)
        layout.addWidget(self._close_btn)

    def mousePressEvent(self, ev) -> None:  # noqa: N802
        if ev.button() == Qt.LeftButton:
            # Map to top-level window so dragging works on frameless windows
            self._drag_pos = (
                ev.globalPosition().toPoint() - self._parent.frameGeometry().topLeft()
            )
            ev.accept()

    def mouseMoveEvent(self, ev) -> None:  # noqa: N802
        if self._drag_pos is not None and ev.buttons() & Qt.LeftButton:
            self._parent.move(ev.globalPosition().toPoint() - self._drag_pos)
            ev.accept()

    def mouseReleaseEvent(self, ev) -> None:  # noqa: N802
        self._drag_pos = None
        ev.accept()


# --- Main window ---
class _PlayerBridge(QObject):
    """Thread-safe bridge between worker threads and the UI.

    Qt's Signal.emit() is thread-safe: when emitted from a non-UI thread,
    the connected slot is invoked on the thread the QObject lives in
    (the UI thread, since we create the bridge on the UI thread).
    """

    progress = Signal(int, int)  # (idx, total)
    done = Signal()
    hotkey_play = Signal()
    hotkey_record = Signal()
    hotkey_cancel = Signal()


class _NotificationBridge(QObject):
    """Thread-safe bridge for notification watcher → UI."""

    detected = Signal(str, str)  # (human_text, app_id)


class MouseRecorderApp(QMainWindow):
    APP_NAME = "MouseRecorder"

    def __init__(self, game_mode: bool = False) -> None:
        super().__init__()
        self.setObjectName("root")
        self.setWindowTitle(self.APP_NAME)
        self._setup_window_flags()
        self._setup_icon()

        # State
        self._game_mode = game_mode
        self._auto_play_enabled = True
        self._recorder = MouseRecorder(on_event=None, game_mode=game_mode)
        self._player = MousePlayer(game_mode=game_mode)
        self._hotkey = HotkeyManager(
            on_play=self._handle_hotkey_play,
            on_record=self._handle_hotkey_record,
            on_cancel=self._handle_hotkey_cancel,
        )
        self._current_recording: Optional[Recording] = None
        self._loaded_recording: Optional[Recording] = None
        self._updating_list = False

        # Bridge for thread-safe worker -> UI communication
        self._player_bridge = _PlayerBridge()
        self._player_bridge.progress.connect(self._on_play_progress)
        self._player_bridge.done.connect(self._on_play_done)
        self._player_bridge.hotkey_play.connect(self._on_play_click)
        self._player_bridge.hotkey_record.connect(self._do_hotkey_record)
        self._player_bridge.hotkey_cancel.connect(self._do_hotkey_cancel)

        # Notification watcher (bridge + watcher)
        self._notif_bridge = _NotificationBridge()
        self._notif_bridge.detected.connect(self._on_notification)
        self._notif_watcher = NotificationWatcher()

        # Build UI
        self._build_ui()
        self._refresh_recordings_list()
        self._update_state("idle", "Ready")

        # Start notification watcher (after UI is built)
        self._start_notif_watching()

        # Start global hotkey
        if not self._hotkey.start():
            self._status_pill.set_hotkey_label("F9/F10 (error)")
        else:
            self._status_pill.set_hotkey_label("F9/F10")

    # --- window setup ---
    def _setup_window_flags(self) -> None:
        self.setWindowFlags(
            Qt.Window
            | Qt.FramelessWindowHint
            | Qt.WindowMinimizeButtonHint
            | Qt.WindowSystemMenuHint
        )

    def _setup_icon(self) -> None:
        ico = assets_dir() / "icon.ico"
        if ico.exists():
            self.setWindowIcon(QIcon(str(ico)))

    # --- UI build ---
    def _build_ui(self) -> None:
        central = QWidget()
        central.setObjectName("root")
        self.setCentralWidget(central)
        self.setStyleSheet(QSS)

        outer = QVBoxLayout(central)
        outer.setContentsMargins(14, 0, 14, 14)
        outer.setSpacing(12)

        # Title bar
        self._title_bar = TitleBar(self)
        outer.addWidget(self._title_bar)

        # Status pill
        status_row = QHBoxLayout()
        status_row.setContentsMargins(0, 0, 0, 0)
        self._status_pill = StatusPill()
        status_row.addWidget(self._status_pill)
        status_row.addSpacing(10)
        self._game_check = QCheckBox("Game mode")
        self._game_check.setObjectName("gameCheck")
        self._game_check.setChecked(self._game_mode)
        self._game_check.setCursor(Qt.PointingHandCursor)
        self._game_check.toggled.connect(self._on_game_mode_toggle)
        status_row.addWidget(self._game_check)
        status_row.addSpacing(8)
        self._auto_play_check = QCheckBox("Auto")
        self._auto_play_check.setObjectName("autoPlayCheck")
        self._auto_play_check.setChecked(self._auto_play_enabled)
        self._auto_play_check.setCursor(Qt.PointingHandCursor)
        self._auto_play_check.toggled.connect(self._on_auto_play_toggle)
        status_row.addWidget(self._auto_play_check)
        status_row.addSpacing(16)
        self._notif_pill = QLabel("Notif: ○")
        self._notif_pill.setObjectName("notifPill")
        status_row.addWidget(self._notif_pill)
        status_row.addStretch(1)
        outer.addLayout(status_row)

        # Notification text (below status row)
        self._notif_text = QLabel("")
        self._notif_text.setObjectName("notifText")
        self._notif_text.setVisible(False)
        outer.addWidget(self._notif_text)

        # Card: main actions (4 big buttons in a 2x2 grid)
        actions_card = GlassCard()
        actions_layout = QVBoxLayout(actions_card)
        actions_layout.setContentsMargins(16, 16, 16, 16)
        actions_layout.setSpacing(10)

        row1 = QHBoxLayout()
        row1.setSpacing(10)
        self._btn_record = GlowButton("🔴  Record", role="record")
        self._btn_stop = GlowButton("⏹  Stop", role="stop")
        self._btn_stop.setEnabled(False)
        row1.addWidget(self._btn_record, 1)
        row1.addWidget(self._btn_stop, 1)
        actions_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(10)
        self._btn_play = GlowButton("▶  Play", role="play")
        self._btn_play.setEnabled(False)
        self._btn_save = GlowButton("💾  Save", role="accent")
        self._btn_save.setEnabled(False)
        row2.addWidget(self._btn_play, 1)
        row2.addWidget(self._btn_save, 1)
        actions_layout.addLayout(row2)

        outer.addWidget(actions_card)

        # Card: recordings list
        list_card = GlassCard()
        list_layout = QVBoxLayout(list_card)
        list_layout.setContentsMargins(16, 14, 16, 16)
        list_layout.setSpacing(8)

        list_header = QHBoxLayout()
        list_title = QLabel("Saved Recordings")
        list_title.setObjectName("title")
        list_title.setStyleSheet("font-size: 13px;")
        list_header.addWidget(list_title)
        list_header.addStretch(1)

        self._btn_load = GlowButton("📂  Load", role="accent")
        self._btn_load.setMinimumHeight(32)
        list_header.addWidget(self._btn_load)
        list_layout.addLayout(list_header)

        self._recordings_list = QListWidget()
        self._recordings_list.setObjectName("recordingsList")
        self._recordings_list.setMinimumHeight(110)
        self._recordings_list.itemDoubleClicked.connect(self._on_list_activate)
        list_layout.addWidget(self._recordings_list, 1)

        outer.addWidget(list_card, 1)

        # Footer
        footer = QLabel("F10 = record/stop   •   F9 = replay   •   ESC = cancel")
        footer.setObjectName("muted")
        footer.setAlignment(Qt.AlignCenter)
        outer.addWidget(footer)

        # Wire up
        self._btn_record.clicked.connect(self._on_record_click)
        self._btn_stop.clicked.connect(self._on_stop_click)
        self._btn_play.clicked.connect(self._on_play_click)
        self._btn_save.clicked.connect(self._on_save_click)
        self._btn_load.clicked.connect(self._on_load_click)

        # Set initial size
        self.resize(520, 560)
        self.setMinimumSize(QSize(480, 480))

    # --- state ---
    def _update_state(self, state: str, text: str) -> None:
        self._status_pill.set_state(state, text)
        recording = state == "recording"
        playing = state == "playing"
        self._btn_record.set_active(recording)
        self._btn_record.setEnabled(not playing)
        self._btn_stop.setEnabled(recording or playing)
        self._btn_stop.set_active(playing or recording)
        self._btn_play.setEnabled(
            (not recording) and self._has_playable_recording()
        )
        self._btn_play.set_active(playing)
        self._btn_save.setEnabled(
            not recording and not playing and self._current_recording is not None
        )

    def _has_playable_recording(self) -> bool:
        if self._current_recording is not None and self._current_recording.events:
            return True
        if self._loaded_recording is not None and self._loaded_recording.events:
            return True
        return False

    def _active_events(self) -> Optional[list[dict]]:
        if self._current_recording is not None and self._current_recording.events:
            return self._current_recording.events
        if self._loaded_recording is not None and self._loaded_recording.events:
            return self._loaded_recording.events
        return None

    # --- recorder callbacks ---
    # (No per-event callback: the periodic QTimer in _on_record_click
    #  reads self._recorder.event_count from the UI thread, which is
    #  thread-safe because event_count acquires the recorder's lock.)

    # --- button handlers ---
    def _on_record_click(self) -> None:
        if self._recorder.is_recording:
            return
        self._current_recording = None
        self._loaded_recording = None
        self._recorder.start()
        self._update_state("recording", f"Recording…  {self._recorder.event_count} events")

        # Periodic status update
        self._record_timer = QTimer(self)
        self._record_timer.setInterval(150)
        self._record_timer.timeout.connect(self._refresh_recording_status)
        self._record_timer.start()

    def _refresh_recording_status(self) -> None:
        if not self._recorder.is_recording:
            if hasattr(self, "_record_timer") and self._record_timer is not None:
                self._record_timer.stop()
                self._record_timer = None
            return
        self._update_state(
            "recording", f"Recording…  {self._recorder.event_count} events"
        )

    def _on_stop_click(self) -> None:
        if self._recorder.is_recording:
            events = self._recorder.stop()
            self._current_recording = Recording(
                name="untitled",
                events=events,
                created_at="",
            )
            if hasattr(self, "_record_timer") and self._record_timer is not None:
                self._record_timer.stop()
                self._record_timer = None
            self._update_state(
                "idle", f"Ready — {len(events)} events captured"
            )
            return
        if self._player.is_playing:
            self._player.cancel()
            self._update_state("idle", "Cancelled")

    def _on_play_click(self) -> None:
        events = self._active_events()
        if not events:
            return
        if self._player.is_playing:
            self._player.cancel()
            return
        self._update_state("playing", f"Playing… 0/{len(events)}")
        # Pass signal emitters as callbacks. Signal.emit() is thread-safe
        # and will queue the call onto the UI thread, so the connected
        # slots (_on_play_progress / _on_play_done) run safely.
        self._player.play(
            events,
            on_done=self._player_bridge.done.emit,
            on_progress=self._player_bridge.progress.emit,
        )

    def _on_play_progress(self, idx: int, total: int) -> None:
        self._update_state("playing", f"Playing… {idx}/{total}")

    def _on_play_done(self) -> None:
        self._update_state("idle", "Playback finished")

    def _on_save_click(self) -> None:
        if self._current_recording is None:
            return
        name, ok = QInputDialog.getText(
            self,
            "Save Recording",
            "Recording name:",
            text=self._current_recording.name or "recording",
        )
        if not ok or not name.strip():
            return
        try:
            path = save_recording(name.strip(), self._current_recording.events)
        except Exception as exc:
            QMessageBox.critical(self, "Save error", str(exc))
            return
        self._current_recording = Recording.from_dict(
            {
                "version": 1,
                "name": path.stem,
                "events": self._current_recording.events,
                "created_at": "",
            }
        )
        self._refresh_recordings_list()
        QMessageBox.information(
            self, "Saved", f"Recording saved to:\n{path}"
        )
        self._update_state("idle", f"Saved: {path.stem}")

    def _on_load_click(self) -> None:
        path_str, _ = QFileDialog.getOpenFileName(
            self,
            "Load Recording",
            str(recordings_dir()),
            "MouseRecorder (*.mrcd);;All files (*)",
        )
        if not path_str:
            return
        self._load_from_path(Path(path_str))

    def _on_list_activate(self, item: QListWidgetItem) -> None:
        path = item.data(Qt.UserRole)
        if not path:
            return
        old_name = item.text()
        new_name, ok = QInputDialog.getText(
            self,
            "Rename Recording",
            "New name:",
            text=old_name,
        )
        if not ok or not new_name.strip() or new_name.strip() == old_name:
            return
        try:
            rename_recording(Path(path), new_name.strip())
        except Exception as exc:
            QMessageBox.critical(self, "Rename error", str(exc))
        self._refresh_recordings_list()

    def _load_from_path(self, path: Path) -> None:
        try:
            rec = load_recording(path)
        except Exception as exc:
            QMessageBox.critical(self, "Load error", f"{path.name}\n\n{exc}")
            return
        self._loaded_recording = rec
        self._current_recording = None
        self._update_state("idle", f"Loaded: {rec.name} — {len(rec.events)} events")

    def _refresh_recordings_list(self) -> None:
        self._updating_list = True
        try:
            self._recordings_list.clear()
            for p in list_recordings():
                item = QListWidgetItem(p.stem)
                item.setData(Qt.UserRole, str(p))
                self._recordings_list.addItem(item)
        finally:
            self._updating_list = False

    # --- hotkey ---
    def _handle_hotkey_play(self) -> None:
        # Called from pynput's thread. Signal.emit() is thread-safe and
        # queues the slot onto the bridge's thread (the UI thread).
        self._player_bridge.hotkey_play.emit()

    def _handle_hotkey_record(self) -> None:
        self._player_bridge.hotkey_record.emit()

    def _handle_hotkey_cancel(self) -> None:
        self._player_bridge.hotkey_cancel.emit()

    def _do_hotkey_record(self) -> None:
        if self._recorder.is_recording:
            self._on_stop_click()
        else:
            self._on_record_click()

    def _do_hotkey_cancel(self) -> None:
        if self._player.is_playing:
            self._player.cancel()

    def _on_game_mode_toggle(self, enabled: bool) -> None:
        self._game_mode = enabled
        self._recorder.set_game_mode(enabled)
        self._player.set_game_mode(enabled)

    def _on_auto_play_toggle(self, enabled: bool) -> None:
        self._auto_play_enabled = enabled

    # --- notification watcher ---
    def _start_notif_watching(self) -> None:
        self._notif_pill.setText("Notif: ○")
        self._notif_watcher.start(
            callback=self._on_notification_from_thread,
        )

    def _on_notification_from_thread(
        self, payload: str, text: str, app_id: str
    ) -> None:
        """Called from the watcher background thread — bridge to UI thread."""
        self._notif_bridge.detected.emit(text, app_id)

    def _on_notification(self, text: str, app_id: str) -> None:
        """Runs on the UI thread. Turns indicator green, shows text, auto-plays."""
        self._notif_pill.setProperty("active", "true")
        self._notif_pill.style().unpolish(self._notif_pill)
        self._notif_pill.style().polish(self._notif_pill)
        self._notif_text.setText(f"📩 {text}")
        self._notif_text.setVisible(True)
        QTimer.singleShot(30000, self._reset_notif_indicator)

        # Auto-play on death notification (with 5s delay)
        if not self._auto_play_enabled:
            return
        if self._recorder.is_recording or self._player.is_playing:
            return
        keywords = ("died", "death", "killed", "muerto", "moriste", "has muerto")
        if any(k in text.lower() for k in keywords):
            if hasattr(self, "_auto_play_timer") and self._auto_play_timer is not None:
                self._auto_play_timer.stop()
            self._auto_play_timer = QTimer(self)
            self._auto_play_timer.setSingleShot(True)
            self._auto_play_timer.timeout.connect(self._on_play_click)
            self._auto_play_timer.start(5000)

    def _reset_notif_indicator(self) -> None:
        self._notif_pill.setProperty("active", "false")
        self._notif_pill.style().unpolish(self._notif_pill)
        self._notif_pill.style().polish(self._notif_pill)
        self._notif_text.setVisible(False)

    # --- close ---
    def closeEvent(self, ev: QCloseEvent) -> None:  # noqa: N802
        try:
            if self._recorder.is_recording:
                self._recorder.stop()
            if self._player.is_playing:
                self._player.cancel()
            self._notif_watcher.stop()
            self._hotkey.stop()
        finally:
            super().closeEvent(ev)
