# MouseRecorder — Agent Memory

## Project overview
Desktop app for Windows 11 that records and replays mouse activity (movement, clicks, scroll). Built with Python 3.11 + PySide6 + pynput. Designed to be a single portable `.exe`.

## Target user
Non-technical end user. Everything is one-click (ejecutar.bat / compilar.bat). Spanish UI copy.

## File format `.mrcd`
JSON with structure:
```json
{
  "version": 1,
  "name": "string",
  "created_at": "ISO 8601",
  "events": [
    {"t": int_ms, "type": "move"|"click"|"scroll", ...}
  ]
}
```
Stored in `recordings/` folder next to the .exe (portable).

## Architecture
- **main.py** → `src.ui.app.MouseRecorderApp.run()`
- **src/core/** — pure logic, no Qt imports. Easy to test.
  - `recorder.py` — `MouseRecorder` wrapping `pynput.mouse.Listener`. Throttles move events to ~8ms to avoid huge files. Emits events via callback.
  - `player.py` — `MousePlayer` reads events, uses `pynput.mouse.Controller`, sleeps between offsets. Cancellable via threading.Event.
  - `storage.py` — `save_recording(name, events, path)` / `load_recording(path)`. JSON, indent=2, validates schema.
  - `hotkey.py` — global F9 listener via `pynput.keyboard.Listener`. Triggers a callback.
- **src/ui/** — Qt layer
  - `app.py` — `QMainWindow` with `FramelessWindowHint` + `WA_TranslucentBackground`. Custom title bar (drag region + min/close). Mica/Acrylic applied via `DwmSetWindowAttribute` (DWMWA_SYSTEMBACKDROP_TYPE = 2 for Mica).
  - `theme.py` — `QSS_DARK_GLASS` string. Palette: bg #0d0d10, glass rgba(255,255,255,0.06), border rgba(255,255,255,0.12), accent #7c5cff, record #ef4444, play #10b981. Font: Segoe UI Variable.
  - `widgets.py` — `GlassCard` (QFrame with rounded corners + translucent bg) and `GlowButton` (QPushButton with hover glow).
- **src/utils/paths.py** — `app_dir()`, `recordings_dir()`, `assets_dir()`. PyInstaller-aware (uses `sys._MEIPASS` for assets in frozen builds).

## Mica/Acrylic on Windows 11
We call `DwmSetWindowAttribute` with `DWMWA_SYSTEMBACKDROP_TYPE`:
- 0 = auto (follow system)
- 1 = none
- 2 = Mica
- 3 = Acrylic
- 4 = Tabbed (Mica Alt)

We use Mica (2) by default, fall back to Acrylic (3) if Mica not available, fall back to plain translucency on Win10.

Function: `apply_backdrop(hwnd, kind=2)` in `src/ui/app.py`.

## Threading model
- Mouse listener runs in pynput's own thread.
- Player runs in a QThread (`PlayerWorker`) to keep UI responsive.
- Hotkey listener runs in pynput's own thread, posts Qt signals to UI via `Signal`.

## How to add a new event type
1. Add parser/serializer in `src/core/storage.py` (`_validate_event`).
2. Add handler in `src/core/recorder.py` (`on_move`, `on_click`, `on_scroll`).
3. Add playback in `src/core/player.py` (`_play_event`).

## Release process
1. Update version in `src/core/storage.py` (if schema changes) and bump in `README.md` roadmap.
2. Commit.
3. Tag: `git tag -a v0.X.Y -m "v0.X.Y — description"`.
4. Build: double-click `compilar.bat` → `dist/MouseRecorder.exe`.

## Known issues / gotchas
- **pynput + admin**: on some Windows configs, recording requires admin rights. Documented in README troubleshooting.
- **PyInstaller antivirus false positives**: some AVs flag the .exe. User must add exception.
- **SendInput in games**: anti-cheat systems may block simulated input. Out of scope, documented.
- **Mica on Windows 10**: not supported by OS. App still works, just with plain translucency.
- **F9 conflict**: some apps (VLC, Discord) capture F9. We chose F9 as default; user can change in `src/core/hotkey.py`.

## Dependencies (requirements.txt)
- `PySide6>=6.7` — Qt 6 Python bindings
- `pynput>=1.7.7` — mouse/keyboard hooks
- `pyinstaller>=6.10` — build to .exe
