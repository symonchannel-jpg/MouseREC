"""Main application window — frameless solid dark UI."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, QPoint, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QCloseEvent, QIcon
from PySide6.QtWidgets import (
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
from src.core.player import MousePlayer
from src.core.recorder import MouseRecorder
from src.core.storage import (
    Recording,
    list_recordings,
    load_recording,
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
    """Thread-safe bridge between MousePlayer (worker thread) and the UI.

    Qt's Signal.emit() is thread-safe: when emitted from a non-UI thread,
    the connected slot is invoked on the thread the QObject lives in
    (the UI thread, since we create the bridge on the UI thread).
    """

    progress = Signal(int, int)  # (idx, total)
    done = Signal()


class MouseRecorderApp(QMainWindow):
    APP_NAME = "MouseRecorder"

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("root")
        self.setWindowTitle(self.APP_NAME)
        self._setup_window_flags()
        self._setup_icon()

        # State
        self._recorder = MouseRecorder(on_event=None)  # we update via QTimer instead
        self._player = MousePlayer()
        self._hotkey = HotkeyManager(
            on_play=self._handle_hotkey_play, on_cancel=self._handle_hotkey_cancel
        )
        self._current_recording: Optional[Recording] = None  # last captured
        self._loaded_recording: Optional[Recording] = None  # currently loaded for play
        self._updating_list = False

        # Bridge for thread-safe player -> UI communication
        self._player_bridge = _PlayerBridge()
        self._player_bridge.progress.connect(self._on_play_progress)
        self._player_bridge.done.connect(self._on_play_done)

        # Build UI
        self._build_ui()
        self._refresh_recordings_list()
        self._update_state("idle", "Listo")

        # Start global hotkey
        if not self._hotkey.start():
            self._status_pill.set_hotkey_label("F9 (error)")
        else:
            self._status_pill.set_hotkey_label("F9")

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
        status_row.addStretch(1)
        outer.addLayout(status_row)

        # Card: main actions (4 big buttons in a 2x2 grid)
        actions_card = GlassCard()
        actions_layout = QVBoxLayout(actions_card)
        actions_layout.setContentsMargins(16, 16, 16, 16)
        actions_layout.setSpacing(10)

        row1 = QHBoxLayout()
        row1.setSpacing(10)
        self._btn_record = GlowButton("🔴  Grabar Mouse", role="record")
        self._btn_stop = GlowButton("⏹  Detener", role="stop")
        self._btn_stop.setEnabled(False)
        row1.addWidget(self._btn_record, 1)
        row1.addWidget(self._btn_stop, 1)
        actions_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(10)
        self._btn_play = GlowButton("▶  Reproducir", role="play")
        self._btn_play.setEnabled(False)
        self._btn_save = GlowButton("💾  Guardar", role="accent")
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
        list_title = QLabel("Grabaciones guardadas")
        list_title.setObjectName("title")
        list_title.setStyleSheet("font-size: 13px;")
        list_header.addWidget(list_title)
        list_header.addStretch(1)

        self._btn_load = GlowButton("📂  Cargar", role="accent")
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
        footer = QLabel("ESC cancela reproducción   •   F9 reproduce la última grabación")
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
        self._update_state("recording", f"Grabando…  {self._recorder.event_count} eventos")

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
            "recording", f"Grabando…  {self._recorder.event_count} eventos"
        )

    def _on_stop_click(self) -> None:
        if self._recorder.is_recording:
            events = self._recorder.stop()
            self._current_recording = Recording(
                name="sin título",
                events=events,
                created_at="",
            )
            if hasattr(self, "_record_timer") and self._record_timer is not None:
                self._record_timer.stop()
                self._record_timer = None
            self._update_state(
                "idle", f"Listo — {len(events)} eventos capturados"
            )
            return
        if self._player.is_playing:
            self._player.cancel()
            self._update_state("idle", "Cancelado")

    def _on_play_click(self) -> None:
        events = self._active_events()
        if not events:
            return
        if self._player.is_playing:
            self._player.cancel()
            return
        self._update_state("playing", f"Reproduciendo… 0/{len(events)}")
        # Pass signal emitters as callbacks. Signal.emit() is thread-safe
        # and will queue the call onto the UI thread, so the connected
        # slots (_on_play_progress / _on_play_done) run safely.
        self._player.play(
            events,
            on_done=self._player_bridge.done.emit,
            on_progress=self._player_bridge.progress.emit,
        )

    def _on_play_progress(self, idx: int, total: int) -> None:
        self._update_state("playing", f"Reproduciendo… {idx}/{total}")

    def _on_play_done(self) -> None:
        self._update_state("idle", "Reproducción terminada")

    def _on_save_click(self) -> None:
        if self._current_recording is None:
            return
        name, ok = QInputDialog.getText(
            self,
            "Guardar grabación",
            "Nombre de la grabación:",
            text=self._current_recording.name or "recording",
        )
        if not ok or not name.strip():
            return
        try:
            path = save_recording(name.strip(), self._current_recording.events)
        except Exception as exc:
            QMessageBox.critical(self, "Error al guardar", str(exc))
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
            self, "Guardado", f"Grabación guardada en:\n{path}"
        )
        self._update_state("idle", f"Guardado: {path.stem}")

    def _on_load_click(self) -> None:
        path_str, _ = QFileDialog.getOpenFileName(
            self,
            "Cargar grabación",
            str(recordings_dir()),
            "MouseRecorder (*.mrcd);;Todos los archivos (*)",
        )
        if not path_str:
            return
        self._load_from_path(Path(path_str))

    def _on_list_activate(self, item: QListWidgetItem) -> None:
        path = item.data(Qt.UserRole)
        if path:
            self._load_from_path(Path(path))

    def _load_from_path(self, path: Path) -> None:
        try:
            rec = load_recording(path)
        except Exception as exc:
            QMessageBox.critical(self, "Error al cargar", f"{path.name}\n\n{exc}")
            return
        self._loaded_recording = rec
        self._current_recording = None
        self._update_state("idle", f"Cargado: {rec.name} — {len(rec.events)} eventos")

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
        # Called from pynput's thread, defer to UI thread
        QTimer.singleShot(0, self._on_play_click)

    def _handle_hotkey_cancel(self) -> None:
        # Called from pynput's thread (keyboard listener).
        # Defer to UI thread so we never touch _player from a foreign thread.
        QTimer.singleShot(0, self._do_hotkey_cancel)

    def _do_hotkey_cancel(self) -> None:
        if self._player.is_playing:
            self._player.cancel()

    # --- close ---
    def closeEvent(self, ev: QCloseEvent) -> None:  # noqa: N802
        try:
            if self._recorder.is_recording:
                self._recorder.stop()
            if self._player.is_playing:
                self._player.cancel()
            self._hotkey.stop()
        finally:
            super().closeEvent(ev)
