# MouseRecorder — Agent Memory

> **This file is the source of truth for future agents working on this project.**
> Read it first. It documents not just WHAT the code does, but WHY it is the way it is,
> including the hard-won lessons from v0.1.0 → v0.1.5 debugging.

## Project overview
Desktop app for Windows 11 that records and replays mouse activity (movement, clicks, scroll). Built with Python 3.11 + PySide6 + pynput. Designed as a single portable `.exe` for a non-technical end user.

## Target user
**Non-technical end user.** Everything is one-click (`ejecutar.bat` / `compilar.bat`). All UI copy is in Spanish. Never assume the user knows what Python is.

## Current status
**v0.1.8 — solid dark theme + stable.** v0.1.0 → v0.1.5 was a marathon of debugging .bat and Qt issues. See "Hard-won lessons" below. The app works end-to-end: record → stop → save → load → play → F9 hotkey.

v0.1.7 added faulthandler + sys.excepthook instrumentation. v0.1.8 replaces the Mica/Acrylic translucent UI with a solid dark palette (`#0d1117`) — no more "white" appearance, high contrast text, desaturated accent colors, and fully opaque surfaces.

## File format `.mrcd` (v1)
JSON in `recordings/` folder next to the .exe (portable):
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

## Architecture

### `src/core/` — pure logic, no Qt imports
- **`recorder.py`** — `MouseRecorder` wraps `pynput.mouse.Listener`. Throttles move events to ~8ms. **No UI callback is invoked from the listener thread** — instead, a QTimer in the UI reads `event_count` (which is lock-protected) at 150ms intervals. This avoids the threading pitfalls documented below.
- **`player.py`** — `MousePlayer` reads events, uses `pynput.mouse.Controller`, sleeps between offsets in 20ms chunks so cancel is responsive. Cancellable via `threading.Event`. **Calls back into UI only via Qt Signals** (passed by the UI as `Signal.emit` methods), never via direct method calls.
- **`storage.py`** — `save_recording` / `load_recording`. JSON, indent=2, validates schema strictly (`_validate_payload` raises on bad input).
- **`hotkey.py`** — global F9 listener via `pynput.keyboard.Listener`. Triggers a callback. The callback for F9 uses `QTimer.singleShot(0, ...)` to hop to the UI thread. The ESC callback (`_handle_hotkey_cancel`) only sets a flag, which is inherently thread-safe.

### `src/ui/` — Qt layer
- **`app.py`** — `QMainWindow` with `FramelessWindowHint` + `WA_TranslucentBackground`. Custom title bar (drag region + min/close). Mica/Acrylic applied via `DwmSetWindowAttribute` (`DWMWA_SYSTEMBACKDROP_TYPE` = 2 for Mica, 3 for Acrylic fallback). **Contains `_PlayerBridge(QObject)`** — a tiny QObject with two Signals (`progress(int, int)` and `done()`) used for thread-safe worker → UI communication. Constructed on the UI thread, so its Signal emissions automatically queue slots back onto the UI thread.
- **`theme.py`** — `QSS` string. Palette: bg `#0d0d10`, glass `rgba(255,255,255,0.06)`, border `rgba(255,255,255,0.12)`, accent `#7c5cff`, record `#ef4444`, play `#10b981`. Font: Segoe UI Variable (with fallbacks).
- **`widgets.py`** — `GlassCard` (QFrame with rounded corners + translucent bg), `GlowButton` (QPushButton with role-based variants: record/stop/play/accent), `StatusPill` (colored dot + text + hotkey label).

### `src/utils/paths.py`
PyInstaller-aware. `sys.frozen` ⇒ use `sys.executable`'s dir for `recordings/` and `sys._MEIPASS` for `assets/`. Otherwise use the project root.

## Threading model (the part that took 3 versions to get right)

| Thread                       | Runs                              | Can touch Qt widgets? |
| ---------------------------- | --------------------------------- | --------------------- |
| **UI thread (main)**         | All QWidget, MouseRecorderApp methods | ✅ Yes                |
| **pynput mouse listener**    | `pynput.mouse.Listener` (Recorder) | ❌ No — use QTimer polling |
| **pynput keyboard listener** | `pynput.keyboard.Listener` (Hotkey) | ❌ No — use `QTimer.singleShot(0, ...)` for F9, flag-only for ESC |
| **Player worker**            | `MousePlayer._run` (Python `threading.Thread`) | ❌ No — emit Signals, never call slots directly |

**The cardinal rule:** the player thread and the pynput listener threads must NEVER call any QWidget/QObject method directly. The bridge (`_PlayerBridge`) is the only sanctioned way to talk to the UI from those threads.

**Why this matters:** violating it produces `0xC0000005` (STATUS_ACCESS_VIOLATION) at seemingly random points. This is exactly what happened in v0.1.0–v0.1.4 — see "Hard-won lessons".

## Solid dark background (no Mica/Acrylic)

Since v0.1.8 the window uses a solid `#0d1117` background instead of the translucent Mica/Acrylic effect. The `WA_TranslucentBackground` flag and `DwmSetWindowAttribute` calls were removed entirely. This eliminates:
- The "white" appearance when the desktop wallpaper is light
- The race condition with `winId()` deferred initialization
- The complexity of frameless translucent window handling

If you want to add a backdrop effect in the future, the old code is in git history at tag v0.1.6 (`_apply_backdrop` in `src/ui/app.py`).

## How to add a new event type
1. Add parser/serializer in `src/core/storage.py` (`_validate_event`).
2. Add handler in `src/core/recorder.py` (`_on_move`, `_on_click`, `_on_scroll`).
3. Add playback in `src/core/player.py` (`_play_event`).
4. (If the UI needs to know per-event) add a new Signal to `_PlayerBridge` and a slot in `MouseRecorderApp`.

## Release process
1. Update README roadmap (mark completed v0.X.Y items as `[x]`).
2. Commit.
3. Tag: `git tag -a v0.X.Y -m "v0.X.Y — description"`.
4. Build: double-click `compilar.bat` → `dist/MouseRecorder.exe`.

---

# Hard-won lessons (READ THESE BEFORE EDITING .BAT OR UI CODE)

## L1. .bat files have 6 characters that are NEVER allowed unquoted at end of line

`&`, `|`, `<`, `>`, `^`, `` ` `` (backtick).

Specifically:
- **`...`** is a wildcard. The error message is: `No se esperaba ... en este momento.` (English: `... was not unexpected at this time`). It comes from the line *after* the message with `...`, not the line itself.
- **`|`** is the pipe operator. The error is: `La sintaxis del comando no es correcta.` ("Command syntax is incorrect"). Triggered by `echo ...mensaje|` because cmd expects another command after the pipe.
- Both errors abort the script immediately, often with NO `pause` reached, hence "the window closes silently".

**Rule:** end every `echo` with a space, a period, or just nothing. NEVER with `...` or `|`.

## L2. .bat files are ANSI, not UTF-8

Any non-ASCII character (`á`, `é`, `ñ`, `…`, `—`) saved as UTF-8 will be **corrupted** (`á` → `�`) and the script may silently fail or produce garbled output. 

**Rule:** `.bat` and `.cmd` files must be **pure ASCII**. Write in English or remove accents (`ejecuta` not `ejecutá`).

To verify: `file ejecutar.bat` should say "ASCII text", not "Unicode text, UTF-8".

## L3. The Microsoft Store Python stub

`%LOCALAPPDATA%\\Microsoft\\WindowsApps\\python.exe` is a stub that opens the Store (or does nothing) instead of running Python. Windows PATH often lists it **first**, so `python` resolves to the stub and breaks the script.

**Rule:** in any launcher .bat, search Python in real install paths first (`%LOCALAPPDATA%\\Programs\\Python\\Python313\\python.exe`, etc.) and skip the WindowsApps stub. Only fall back to `where python` or `py` if those searches fail.

## L4. The Windows console window closes when the .bat exits

When you double-click a .bat, the cmd window opens, runs the script, and **closes when the script exits**. The only ways to keep it open:
- A bare `pause` at the end (no `>nul` redirect — `pause >nul` works but is less reliable).
- `cmd /k ejecutar.bat` from a wrapper.
- Wrapping the call in `start "Title" cmd /k ...`.

The `iniciar.cmd` wrapper uses `cd /d "%~dp0"` + `call "%~dp0ejecutar.bat"` and relies on the final `pause` in `ejecutar.bat` to keep the window open. This works because `call` returns to the parent .cmd only after `ejecutar.bat` finishes (including its pause), but the parent .cmd also has no further commands and `iniciar.cmd` has no `exit` either, so the console stays open.

**Rule:** any launcher .bat that the user might run with a double-click MUST end with `pause` and have no `exit` before it.

## L5. Qt widgets are NOT thread-safe

Calling a slot that touches a QWidget from any thread other than the UI thread will eventually crash with `0xC0000005` (STATUS_ACCESS_VIOLATION). This is what happened in v0.1.0 — the player's `on_done` and `on_progress` callbacks were called from the player thread and called `_update_state` which set widget properties.

**Rule:** for worker-thread → UI communication in Qt, use **QObject Signals**. `Signal.emit()` is thread-safe and queues the slot onto the thread the QObject lives in. Construct the bridge QObject on the UI thread.

The pattern is documented in `src/ui/app.py` with `_PlayerBridge`. Copy this pattern for any new worker threads.

## L6. pynput listeners are also separate threads

`pynput.mouse.Listener` and `pynput.keyboard.Listener` each spawn their own thread. Callbacks from those threads must not touch Qt widgets. For our app:
- **Recorder:** instead of a per-event callback, a QTimer in the UI polls `MouseRecorder.event_count` (which is lock-protected). Simple and safe.
- **Hotkey (F9):** callback uses `QTimer.singleShot(0, self._on_play_click)` to hop to the UI thread.
- **Hotkey (ESC):** callback only sets `threading.Event` flag — no UI access needed.

## L7. The `errorlevel` check after `goto` and `if`

In .bat, `if errorlevel 1` means "if errorlevel >= 1". That's almost always what you want, but be aware. `set /a` with a failed parse returns `1`, which can trip unexpected branches.

## L8. pynput.Listener.stop() joins the thread internally — it blocks

`pynput.Listener.stop()` calls `self._thread.join()`, which blocks the caller until the listener thread exits. If called from the UI thread (e.g., `_on_stop_click` → `recorder.stop()`), **the UI freezes** for up to several hundred ms.

**Rule:** Never call `Listener.stop()` synchronously from the UI thread. Delegate to a short-lived daemon thread:

```python
threading.Thread(target=lambda: recorder._listener.stop(), daemon=True).start()
```

## L9. All pynput hotkey callbacks must be deferred to the UI thread

Both `pynput.keyboard.Listener.on_press` and `.on_release` callbacks run on the pynput listener thread. While simple operations (`Event.set()`, `is_alive()`) are thread-safe in Python, touching ANY Qt API, reading `self._player.is_playing`, or calling `self._player.cancel()` from the pynput thread is a race condition waiting to happen.

**Rule:** ALL hotkey callbacks (both F9 and ESC) MUST use `QTimer.singleShot(0, self._handler_method)` to defer to the UI thread. The ESC cancel callback in v0.1.6 and earlier ran directly on the pynput thread — this was fixed in v0.1.7.

---

# Known issues / gotchas (runtime)

- **pynput + admin**: on some Windows configs, recording requires admin rights. Documented in README troubleshooting.
- **PyInstaller antivirus false positives**: some AVs flag the .exe. User must add exception for `dist\MouseRecorder.exe`.
- **SendInput in games**: anti-cheat systems may block simulated input. Out of scope.
- **Mica on Windows 10**: not supported by OS. App still works, just with plain translucency.
- **F9 conflict**: some apps (VLC, Discord) capture F9. We chose F9 as default; user can change in `src/core/hotkey.py`.
- **PySide6 3.13 wheels**: as of early 2026, PySide6 publishes Windows wheels for Python 3.13. If a future user has a Python version that lacks wheels, pip install will fail and the user must install a different Python (3.11 or 3.12 are safe bets).

# Dependencies (requirements.txt)
- `PySide6>=6.7` — Qt 6 Python bindings
- `pynput>=1.7.7` — mouse/keyboard hooks
- `pyinstaller>=6.10` — build to .exe
