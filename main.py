"""MouseRecorder — entry point.

Run with:
    python main.py
"""
from __future__ import annotations

import faulthandler
import os
import sys
import traceback

# --- Crash diagnostics ---
# faulthandler: writes Python traceback + C stack on segfault/abort
log_dir = os.path.dirname(os.path.abspath(__file__))
_crash_log = os.path.join(log_dir, "crash_traceback.log")
try:
    faulthandler.enable(file=open(_crash_log, "w"))
except Exception:
    pass  # best-effort


def _global_excepthook(exc_type, exc_value, exc_tb):
    """Log any unhandled Python exception before propagating."""
    tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    try:
        with open(_crash_log, "a") as f:
            f.write(f"\n=== UNHANDLED EXCEPTION: {exc_type.__name__} ===\n{tb_str}\n")
    except Exception:
        pass
    # Call original hook (usually prints to stderr)
    sys.__excepthook__(exc_type, exc_value, exc_tb)


sys.excepthook = _global_excepthook


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
