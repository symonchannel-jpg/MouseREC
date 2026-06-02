"""Dark glass theme — palette, QSS, and shared colors."""
from __future__ import annotations

# --- Palette ---
BG_BASE = "#0d0d10"
BG_PANEL = "rgba(255, 255, 255, 0.04)"
GLASS_FILL = "rgba(255, 255, 255, 0.06)"
GLASS_FILL_HOVER = "rgba(255, 255, 255, 0.10)"
GLASS_FILL_PRESSED = "rgba(255, 255, 255, 0.14)"
GLASS_BORDER = "rgba(255, 255, 255, 0.12)"
GLASS_BORDER_HOVER = "rgba(255, 255, 255, 0.22)"

TEXT_PRIMARY = "#f5f5fa"
TEXT_SECONDARY = "rgba(245, 245, 250, 0.65)"
TEXT_MUTED = "rgba(245, 245, 250, 0.42)"

ACCENT = "#7c5cff"
ACCENT_HOVER = "#9277ff"
ACCENT_PRESSED = "#6849e6"

RECORD = "#ef4444"
RECORD_HOVER = "#f87171"
PLAY = "#10b981"
PLAY_HOVER = "#34d399"
WARN = "#f59e0b"

# --- QSS ---
QSS = f"""
* {{
    font-family: "Segoe UI Variable", "Segoe UI", "Inter", "Helvetica Neue", Arial, sans-serif;
}}

QMainWindow, QWidget#root {{
    background: transparent;
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
    letter-spacing: 0.3px;
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

QFrame#titleBar {{
    background: transparent;
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
    background: {GLASS_FILL_HOVER};
    color: {TEXT_PRIMARY};
}}
QFrame#titleBar QPushButton#titleBtn[class="close"]:hover {{
    background: {RECORD};
    color: white;
}}

/* --- Glass card container --- */
QFrame#glassCard {{
    background: {GLASS_FILL};
    border: 1px solid {GLASS_BORDER};
    border-radius: 14px;
}}

/* --- Main action buttons (Record / Stop / Play / Save / Load) --- */
QPushButton#primary {{
    background: {GLASS_FILL};
    color: {TEXT_PRIMARY};
    border: 1px solid {GLASS_BORDER};
    border-radius: 12px;
    padding: 14px 18px;
    font-size: 13px;
    font-weight: 600;
    text-align: center;
}}
QPushButton#primary:hover {{
    background: {GLASS_FILL_HOVER};
    border-color: {GLASS_BORDER_HOVER};
}}
QPushButton#primary:pressed {{
    background: {GLASS_FILL_PRESSED};
}}
QPushButton#primary:disabled {{
    color: {TEXT_MUTED};
    background: {GLASS_FILL};
    border-color: rgba(255,255,255,0.06);
}}

/* record variant */
QPushButton#primary[role="record"] {{
    color: {RECORD};
    border-color: rgba(239, 68, 68, 0.35);
}}
QPushButton#primary[role="record"]:hover {{
    background: rgba(239, 68, 68, 0.15);
    border-color: rgba(239, 68, 68, 0.6);
}}
QPushButton#primary[role="record"][active="true"] {{
    background: {RECORD};
    color: white;
    border-color: {RECORD};
}}

/* play variant */
QPushButton#primary[role="play"] {{
    color: {PLAY};
    border-color: rgba(16, 185, 129, 0.35);
}}
QPushButton#primary[role="play"]:hover {{
    background: rgba(16, 185, 129, 0.15);
    border-color: rgba(16, 185, 129, 0.6);
}}
QPushButton#primary[role="play"][active="true"] {{
    background: {PLAY};
    color: #061b14;
    border-color: {PLAY};
}}

/* stop variant */
QPushButton#primary[role="stop"] {{
    color: {WARN};
    border-color: rgba(245, 158, 11, 0.35);
}}
QPushButton#primary[role="stop"]:hover {{
    background: rgba(245, 158, 11, 0.15);
    border-color: rgba(245, 158, 11, 0.6);
}}

/* accent (Save) */
QPushButton#primary[role="accent"] {{
    color: {ACCENT};
    border-color: rgba(124, 92, 255, 0.35);
}}
QPushButton#primary[role="accent"]:hover {{
    background: rgba(124, 92, 255, 0.15);
    border-color: rgba(124, 92, 255, 0.6);
}}

/* --- Status pill --- */
QFrame#statusPill {{
    background: {GLASS_FILL};
    border: 1px solid {GLASS_BORDER};
    border-radius: 18px;
    padding: 6px 12px;
}}
QFrame#statusPill[state="recording"] {{
    background: rgba(239, 68, 68, 0.15);
    border-color: rgba(239, 68, 68, 0.45);
}}
QFrame#statusPill[state="playing"] {{
    background: rgba(16, 185, 129, 0.15);
    border-color: rgba(16, 185, 129, 0.45);
}}

/* --- Recordings list --- */
QListWidget#recordingsList {{
    background: transparent;
    border: 1px solid {GLASS_BORDER};
    border-radius: 10px;
    color: {TEXT_PRIMARY};
    padding: 4px;
    outline: 0;
}}
QListWidget#recordingsList::item {{
    padding: 8px 10px;
    border-radius: 6px;
    margin: 2px 0;
}}
QListWidget#recordingsList::item:hover {{
    background: {GLASS_FILL_HOVER};
}}
QListWidget#recordingsList::item:selected {{
    background: rgba(124, 92, 255, 0.25);
    color: {TEXT_PRIMARY};
}}

/* --- Input --- */
QLineEdit {{
    background: {GLASS_FILL};
    color: {TEXT_PRIMARY};
    border: 1px solid {GLASS_BORDER};
    border-radius: 8px;
    padding: 6px 10px;
    selection-background-color: {ACCENT};
}}
QLineEdit:focus {{
    border-color: {ACCENT};
    background: {GLASS_FILL_HOVER};
}}

/* --- Scrollbars --- */
QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 4px 2px;
}}
QScrollBar::handle:vertical {{
    background: rgba(255,255,255,0.15);
    border-radius: 4px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background: rgba(255,255,255,0.25);
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

/* --- QInputDialog / QMessageBox adapt --- */
QMessageBox {{
    background: {BG_BASE};
}}
QMessageBox QLabel {{
    color: {TEXT_PRIMARY};
}}
"""
