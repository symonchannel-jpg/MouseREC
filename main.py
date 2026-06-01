"""MouseRecorder — entry point.

Run with:
    python main.py
"""
from __future__ import annotations

import sys


def main() -> int:
    from PySide6.QtWidgets import QApplication

    from src.ui.app import MouseRecorderApp
    from src.ui.theme import QSS

    app = QApplication(sys.argv)
    app.setApplicationName("MouseRecorder")
    app.setStyleSheet(QSS)

    win = MouseRecorderApp()
    win.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
