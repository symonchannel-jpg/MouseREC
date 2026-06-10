"""Monochromatic dark theme — high contrast, near-black, no color noise."""
from __future__ import annotations

BG_BASE = "#050505"
BG_PANEL = "#0f0f0f"
BG_ELEVATED = "#1a1a1a"
BG_INSET = "#252525"

BORDER = "#2a2a2a"
BORDER_HOVER = "#444444"

TEXT_PRIMARY = "#f5f5f5"
TEXT_SECONDARY = "#aaaaaa"
TEXT_MUTED = "#777777"

ACCENT = "#d4d4d4"
ACCENT_HOVER = "#e8e8e8"
ACCENT_PRESSED = "#999999"

RECORD = "#cc3b3b"
RECORD_HOVER = "#e05555"
RECORD_ACTIVE = "#992222"

PLAY = "#3bb65b"
PLAY_HOVER = "#4fc970"
PLAY_ACTIVE = "#268a40"

WARN = "#b8a030"
WARN_HOVER = "#cbb34a"

QSS = f"""
* {{
    font-family: "Segoe UI Variable", "Segoe UI", "Inter", "Helvetica Neue", Arial, sans-serif;
}}

QMainWindow, QWidget#root {{
    background: {BG_BASE};
    color: {TEXT_PRIMARY};
}}

QLabel {{
    color: {TEXT_PRIMARY};
    background: transparent;
}}

QLabel#muted {{
    color: {TEXT_MUTED};
}}

QLabel#title {{
    color: {TEXT_PRIMARY};
    font-size: 18px;
    font-weight: 600;
}}

QLabel#subtitle {{
    color: {TEXT_SECONDARY};
    font-size: 12px;
    font-weight: 400;
}}

QLabel#statusText {{
    color: {TEXT_PRIMARY};
    font-size: 13px;
    font-weight: 500;
}}

/* --- Title bar --- */
QFrame#titleBar {{
    background: {BG_BASE};
    border: none;
}}

QFrame#titleBar QLabel#title {{
    color: {TEXT_PRIMARY};
    font-size: 13px;
    font-weight: 600;
    padding-left: 4px;
}}

QFrame#titleBar QPushButton#titleBtn {{
    background: transparent;
    border: none;
    color: {TEXT_SECONDARY};
    font-size: 14px;
    padding: 0 10px;
    min-width: 32px;
    min-height: 28px;
    border-radius: 6px;
}}
QFrame#titleBar QPushButton#titleBtn:hover {{
    background: {BG_ELEVATED};
    color: {TEXT_PRIMARY};
}}
QFrame#titleBar QPushButton#titleBtn[class="close"]:hover {{
    background: {RECORD};
    color: white;
}}

/* --- Checkboxes --- */
QCheckBox#gameCheck, QCheckBox#autoPlayCheck {{
    color: {TEXT_MUTED};
    font-size: 12px;
    font-weight: 500;
    spacing: 6px;
}}
QCheckBox#gameCheck:hover, QCheckBox#autoPlayCheck:hover {{
    color: {TEXT_SECONDARY};
}}
QCheckBox#gameCheck::indicator, QCheckBox#autoPlayCheck::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {BORDER};
    border-radius: 4px;
    background: {BG_PANEL};
}}
QCheckBox#gameCheck::indicator:hover, QCheckBox#autoPlayCheck::indicator:hover {{
    border-color: {BORDER_HOVER};
    background: {BG_ELEVATED};
}}
QCheckBox#gameCheck::indicator:checked {{
    background: {ACCENT};
    border-color: {ACCENT};
}}
QCheckBox#gameCheck::indicator:checked:hover {{
    background: {ACCENT_HOVER};
    border-color: {ACCENT_HOVER};
}}
QCheckBox#autoPlayCheck::indicator:checked {{
    background: {PLAY};
    border-color: {PLAY};
}}
QCheckBox#autoPlayCheck::indicator:checked:hover {{
    background: {PLAY_HOVER};
    border-color: {PLAY_HOVER};
}}

/* --- Notification indicator --- */
QLabel#notifPill {{
    color: {TEXT_MUTED};
    font-size: 11px;
    font-weight: 500;
    padding: 0 4px;
}}
QLabel#notifPill[active="true"] {{
    color: {TEXT_PRIMARY};
}}
QLabel#notifText {{
    color: {TEXT_MUTED};
    font-size: 11px;
    padding: 0 4px;
}}

/* --- Panel card --- */
QFrame#panelCard {{
    background: {BG_PANEL};
    border: 1px solid {BORDER};
    border-radius: 14px;
}}

/* --- Main action buttons --- */
QPushButton#primary {{
    background: {BG_PANEL};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 14px 18px;
    font-size: 13px;
    font-weight: 600;
    text-align: center;
}}
QPushButton#primary:hover {{
    background: {BG_ELEVATED};
    border-color: {BORDER_HOVER};
}}
QPushButton#primary:pressed {{
    background: {BG_INSET};
}}
QPushButton#primary:disabled {{
    color: {TEXT_MUTED};
    background: {BG_PANEL};
    border-color: {BORDER};
    opacity: 0.5;
}}

/* record variant */
QPushButton#primary[role="record"] {{
    color: {RECORD};
    border-color: rgba(204, 59, 59, 0.35);
}}
QPushButton#primary[role="record"]:hover {{
    background: rgba(204, 59, 59, 0.12);
    border-color: rgba(204, 59, 59, 0.55);
}}
QPushButton#primary[role="record"][active="true"] {{
    background: {RECORD_ACTIVE};
    color: white;
    border-color: {RECORD};
}}

/* play variant */
QPushButton#primary[role="play"] {{
    color: {PLAY};
    border-color: rgba(59, 182, 91, 0.35);
}}
QPushButton#primary[role="play"]:hover {{
    background: rgba(59, 182, 91, 0.12);
    border-color: rgba(59, 182, 91, 0.55);
}}
QPushButton#primary[role="play"][active="true"] {{
    background: {PLAY_ACTIVE};
    color: white;
    border-color: {PLAY};
}}

/* stop variant */
QPushButton#primary[role="stop"] {{
    color: {WARN};
    border-color: rgba(184, 160, 48, 0.35);
}}
QPushButton#primary[role="stop"]:hover {{
    background: rgba(184, 160, 48, 0.12);
    border-color: rgba(184, 160, 48, 0.55);
}}

/* accent (Save / Load) */
QPushButton#primary[role="accent"] {{
    color: {ACCENT};
    border-color: rgba(212, 212, 212, 0.35);
}}
QPushButton#primary[role="accent"]:hover {{
    background: rgba(212, 212, 212, 0.12);
    border-color: rgba(212, 212, 212, 0.55);
}}

/* --- Status pill --- */
QFrame#statusPill {{
    background: {BG_PANEL};
    border: 1px solid {BORDER};
    border-radius: 18px;
    padding: 6px 12px;
}}
QFrame#statusPill[state="recording"] {{
    background: rgba(204, 59, 59, 0.12);
    border-color: rgba(204, 59, 59, 0.45);
}}
QFrame#statusPill[state="playing"] {{
    background: rgba(59, 182, 91, 0.12);
    border-color: rgba(59, 182, 91, 0.45);
}}

/* --- Recordings list --- */
QListWidget#recordingsList {{
    background: {BG_BASE};
    border: 1px solid {BORDER};
    border-radius: 10px;
    color: {TEXT_PRIMARY};
    padding: 4px;
    outline: 0;
}}
QListWidget#recordingsList::item {{
    padding: 8px 10px;
    border-radius: 6px;
    margin: 2px 0;
    color: {TEXT_PRIMARY};
}}
QListWidget#recordingsList::item:hover {{
    background: {BG_ELEVATED};
}}
QListWidget#recordingsList::item:selected {{
    background: rgba(212, 212, 212, 0.15);
    color: {TEXT_PRIMARY};
}}

/* --- Input --- */
QLineEdit {{
    background: {BG_INSET};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 6px 10px;
    selection-background-color: rgba(212, 212, 212, 0.3);
}}
QLineEdit:focus {{
    border-color: {ACCENT};
    background: {BG_ELEVATED};
}}

/* --- Scrollbars --- */
QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 4px 2px;
}}
QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 4px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background: {BORDER_HOVER};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

/* --- Dialog adapt --- */
QMessageBox {{
    background: {BG_BASE};
}}
QMessageBox QLabel {{
    color: {TEXT_PRIMARY};
}}
QMessageBox QPushButton {{
    background: {BG_PANEL};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 6px 18px;
    min-width: 60px;
}}
QMessageBox QPushButton:hover {{
    background: {BG_ELEVATED};
    border-color: {BORDER_HOVER};
}}
"""
