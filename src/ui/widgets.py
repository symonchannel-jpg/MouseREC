"""Reusable custom widgets: GlassCard, GlowButton, StatusPill."""
from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QPainter, QPaintEvent, QPen
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.ui.theme import (
    BG_ELEVATED,
    BG_PANEL,
    BORDER,
    RECORD,
    RECORD_HOVER,
    PLAY,
    PLAY_HOVER,
    WARN,
    TEXT_MUTED,
    TEXT_PRIMARY,
    ACCENT,
)


class GlassCard(QFrame):
    """A rounded panel card with solid dark background."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("panelCard")
        self.setAttribute(Qt.WA_StyledBackground, True)


class GlowButton(QPushButton):
    """QPushButton styled by the QSS #primary role variants.

    Set ``role`` to one of: ``"default"``, ``"record"``, ``"stop"``, ``"play"``,
    ``"accent"`` to get the right color treatment.
    """

    def __init__(
        self,
        text: str = "",
        role: str = "default",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(text, parent)
        self.setObjectName("primary")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(48)
        self.setProperty("role", role)
        self._role = role
        self.set_active(False)

    @property
    def role(self) -> str:
        return self._role

    def set_role(self, role: str) -> None:
        self._role = role
        self.setProperty("role", role)
        # re-polish so the new property takes effect
        self.style().unpolish(self)
        self.style().polish(self)

    def set_active(self, active: bool) -> None:
        self.setProperty("active", "true" if active else "false")
        self.style().unpolish(self)
        self.style().polish(self)


class StatusPill(QFrame):
    """A small rounded pill showing a colored dot + text + (optional) hotkey."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("statusPill")
        self.setProperty("state", "idle")
        self.setAttribute(Qt.WA_StyledBackground, True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 4, 12, 4)
        layout.setSpacing(8)

        self._dot = QLabel()
        self._dot.setFixedSize(10, 10)
        self._dot.setStyleSheet(
            f"background: {TEXT_MUTED}; border-radius: 5px;"
        )
        layout.addWidget(self._dot)

        self._text = QLabel("Listo")
        self._text.setObjectName("statusText")
        layout.addWidget(self._text)

        layout.addStretch(1)

        self._hotkey = QLabel("F9")
        self._hotkey.setStyleSheet(
            f"color: {TEXT_MUTED}; background: {BG_ELEVATED};"
            f" border: 1px solid {BORDER}; border-radius: 5px;"
            f" padding: 1px 7px; font-size: 11px; font-weight: 600;"
        )
        layout.addWidget(self._hotkey)

        self.set_state("idle", "Listo")

    def set_state(self, state: str, text: str) -> None:
        """state ∈ 'idle' | 'recording' | 'playing'"""
        self.setProperty("state", state)
        self.style().unpolish(self)
        self.style().polish(self)
        self._text.setText(text)
        if state == "recording":
            color = RECORD
        elif state == "playing":
            color = PLAY
        else:
            color = TEXT_MUTED
        self._dot.setStyleSheet(
            f"background: {color}; border-radius: 5px;"
        )

    def set_hotkey_label(self, text: str) -> None:
        self._hotkey.setText(text)
