@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

echo.
echo ===========================================
echo    MouseRecorder - Diagnostics
echo ===========================================
echo.

echo --- Python in PATH (may include the Microsoft Store stub) ---
where py 2>nul
where python 2>nul
echo.

echo --- Installed Python ---
set "FOUND_PY="
for %%V in (313 312 311 310 39) do (
    for %%P in (
        "%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe"
        "%USERPROFILE%\AppData\Local\Programs\Python\Python%%V\python.exe"
        "C:\Python%%V\python.exe"
        "C:\Program Files\Python%%V\python.exe"
    ) do (
        if exist %%P (
            echo   - %%~P
            if not defined FOUND_PY set "FOUND_PY=%%~P"
        )
    )
)
echo.

echo --- Python que va a usar ejecutar.bat ---
if defined FOUND_PY (
    echo   !FOUND_PY!
    echo   Probando:
    "!FOUND_PY!" --version 2>&1
) else (
    echo   [NOT FOUND]
    echo   Install Python 3.11+ from https://www.python.org/downloads/
)
echo.

echo --- Virtual environment ---
if exist ".venv\Scripts\python.exe" (
    echo   Exists: .venv\Scripts\python.exe
    ".venv\Scripts\python.exe" --version
    echo.
    echo --- Paquetes en el venv ---
    ".venv\Scripts\python.exe" -m pip list 2>nul | findstr /i "PySide6 pynput PyInstaller"
) else (
    echo   Does NOT exist. It will be created when running ejecutar.bat.
)
echo.

echo --- Project files ---
if exist "main.py"              echo   [OK] main.py
if exist "requirements.txt"     echo   [OK] requirements.txt
if exist "src\ui\app.py"        echo   [OK] src\ui\app.py
if exist "assets\icon.ico"      echo   [OK] assets\icon.ico
if exist "ejecutar.bat"         echo   [OK] ejecutar.bat
if exist "compilar.bat"         echo   [OK] compilar.bat
if exist "diagnostico.bat"      echo   [OK] diagnostico.bat
echo.

echo --- Last run log (last_run.log) ---
if exist "last_run.log" (
    echo   Exists. Contents:
    echo   ----------------------------------------
    type "last_run.log"
    echo   ----------------------------------------
) else (
    echo   No log yet. Run ejecutar.bat first.
)
echo.

echo --- Quick import test (if venv exists) ---
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -c "import sys, PySide6, pynput; print('   [OK] Python', sys.version.split()[0], '| PySide6', PySide6.__version__, '| pynput', pynput.__version__)" 2>&1
) else (
    echo   (no venv yet - run ejecutar.bat first)
)
echo.

echo ===========================================
echo  Diagnostics complete.
echo  If something fails, send me this output.
echo ===========================================
echo.
pause
endlocal
