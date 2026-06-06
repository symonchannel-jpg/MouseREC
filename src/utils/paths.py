"""Path helpers, PyInstaller-aware.

When the app is frozen (built with PyInstaller), assets live in ``sys._MEIPASS``.
Otherwise they live next to this file's parent's parent (the project root).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path


def project_root() -> Path:
    """Root of the project (or the bundle dir when frozen)."""
    if getattr(sys, "frozen", False):
        # PyInstaller: dist/MouseRecorder.exe → exe dir is the app home
        return Path(sys.executable).resolve().parent
    # src/utils/paths.py → project root is two levels up
    return Path(__file__).resolve().parents[2]


def assets_dir() -> Path:
    """Where icon/banner live. Inside the bundle when frozen, else in assets/."""
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", project_root())) / "assets"
    return project_root() / "assets"


def recordings_dir() -> Path:
    """Where .mrcd files are stored. Always next to the executable for portability."""
    d = project_root() / "recordings"
    d.mkdir(parents=True, exist_ok=True)
    return d


def notifications_db_path() -> Path:
    """Path to Windows Toast notification database."""
    return Path(os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\Notifications\wpndatabase.db"))
