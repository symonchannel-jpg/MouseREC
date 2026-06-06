"""Solid dark theme — palette, QSS, and shared colors.

No glass, no Mica, no translucency. Just solid dark surfaces with
high-contrast text and restrained accent colors.
"""

# --- Palette (GitHub-dark inspired, professional, not oversaturated) ---
BG_BASE = "#0d1117"         # main background
BG_PANEL = "#161b22"        # cards, panels
BG_ELEVATED = "#1c2128"     # hover / active surfaces
BG_INSET = "#21262d"        # inputs, list items

BORDER = "#30363d"          # subtle borders
BORDER_HOVER = "#484f58"    # brighter border on hover

TEXT_PRIMARY = "#e6edf3"    # main text (≥10:1 contrast)
TEXT_SECONDARY = "#8b949e"  # secondary text (≥5:1)
TEXT_MUTED = "#7d8590"      # muted text (≥4.5:1)

ACCENT = "#58a6ff"          # blue accent
ACCENT_HOVER = "#79c0ff"
ACCENT_PRESSED = "#1f6feb"

RECORD = "#da3633"          # red (restrained)
RECORD_HOVER = "#f85149"
RECORD_ACTIVE = "#b62324"

PLAY = "#3fb950"            # green (restrained)
PLAY_HOVER = "#56d364"
PLAY_ACTIVE = "#2ea043"

WARN = "#d29922"            # amber
WARN_HOVER = "#e3b341"

# --- QSS ---
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

/* --- Game mode checkbox --- */
QCheckBox#gameCheck {{
    color: {TEXT_MUTED};
    font-size: 12px;
    font-weight: 500;
    spacing: 6px;
}}
QCheckBox#gameCheck:hover {{
    color: {TEXT_SECONDARY};
}}
QCheckBox#gameCheck::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {BORDER};
    border-radius: 4px;
    background: {BG_PANEL};
}}
QCheckBox#gameCheck::indicator:hover {{
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

/* --- Notification indicator --- */
QLabel#notifPill {{
    color: {TEXT_MUTED};
    font-size: 11px;
    font-weight: 500;
    padding: 0 4px;
}}
QLabel#notifPill[active="true"] {{
    color: {PLAY};
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
    border-color: rgba(218, 54, 51, 0.35);
}}
QPushButton#primary[role="record"]:hover {{
    background: rgba(218, 54, 51, 0.12);
    border-color: rgba(218, 54, 51, 0.55);
}}
QPushButton#primary[role="record"][active="true"] {{
    background: {RECORD_ACTIVE};
    color: white;
    border-color: {RECORD};
}}

/* play variant */
QPushButton#primary[role="play"] {{
    color: {PLAY};
    border-color: rgba(63, 185, 80, 0.35);
}}
QPushButton#primary[role="play"]:hover {{
    background: rgba(63, 185, 80, 0.12);
    border-color: rgba(63, 185, 80, 0.55);
}}
QPushButton#primary[role="play"][active="true"] {{
    background: {PLAY_ACTIVE};
    color: white;
    border-color: {PLAY};
}}

/* stop variant */
QPushButton#primary[role="stop"] {{
    color: {WARN};
    border-color: rgba(210, 153, 34, 0.35);
}}
QPushButton#primary[role="stop"]:hover {{
    background: rgba(210, 153, 34, 0.12);
    border-color: rgba(210, 153, 34, 0.55);
}}

/* accent (Save / Load) */
QPushButton#primary[role="accent"] {{
    color: {ACCENT};
    border-color: rgba(88, 166, 255, 0.35);
}}
QPushButton#primary[role="accent"]:hover {{
    background: rgba(88, 166, 255, 0.12);
    border-color: rgba(88, 166, 255, 0.55);
}}

/* --- Status pill --- */
QFrame#statusPill {{
    background: {BG_PANEL};
    border: 1px solid {BORDER};
    border-radius: 18px;
    padding: 6px 12px;
}}
QFrame#statusPill[state="recording"] {{
    background: rgba(218, 54, 51, 0.12);
    border-color: rgba(218, 54, 51, 0.45);
}}
QFrame#statusPill[state="playing"] {{
    background: rgba(63, 185, 80, 0.12);
    border-color: rgba(63, 185, 80, 0.45);
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
    background: rgba(88, 166, 255, 0.18);
    color: {TEXT_PRIMARY};
}}

/* --- Input --- */
QLineEdit {{
    background: {BG_INSET};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 6px 10px;
    selection-background-color: rgba(88, 166, 255, 0.35);
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
