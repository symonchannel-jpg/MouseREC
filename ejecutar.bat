@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

set "LOG=%~dp0last_run.log"
set "STEP=0"

REM --- Log function: appends a timestamped line to LOG ---
call :log "=== MouseRecorder launcher started ==="
call :log "Working dir: %CD%"

echo.
echo ===========================================
echo    MouseRecorder - Starting
echo ===========================================
echo.
echo If this window closes by itself, send me the file:
echo   %LOG%
echo.

REM --- Buscar Python real (skipea el stub de Microsoft Store) ---
set "PYEXE="
for %%V in (312 313 311 310 39) do (
    for %%P in (
        "%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe"
        "%USERPROFILE%\AppData\Local\Programs\Python\Python%%V\python.exe"
        "C:\Python%%V\python.exe"
        "C:\Program Files\Python%%V\python.exe"
    ) do (
        if exist %%P if not defined PYEXE set "PYEXE=%%~P"
    )
)
if "!PYEXE!"=="" (
    where py >nul 2>&1
    if not errorlevel 1 set "PYEXE=py -3"
)

if "!PYEXE!"=="" (
    call :log "[ERROR] Python not found"
    echo [ERROR] Python not found.
    echo Install it from https://www.python.org/downloads/
    echo.
    call :pause_keep
    goto :end
)

call :log "Python found: !PYEXE!"
echo [OK] Python: !PYEXE!
"!PYEXE!" --version >nul 2>&1
if errorlevel 1 (
    call :log "[ERROR] Python --version failed"
    echo [ERROR] The Python found is not responding.
    call :pause_keep
    goto :end
)
for /f "delims=" %%V in ('"!PYEXE!" --version 2^>^&1') do (
    call :log "Python version: %%V"
    echo        %%V
)
echo.

REM --- Crear venv si no existe ---
if not exist ".venv\Scripts\python.exe" (
    echo [INFO] Creating virtual environment (first time, ~30 seconds)
    call :log "Creating venv"
    "!PYEXE!" -m venv .venv > "%LOG%.tmp" 2>&1
    if errorlevel 1 (
        type "%LOG%.tmp" >> "%LOG%"
        del "%LOG%.tmp" 2>nul
        call :log "[ERROR] venv creation failed"
        echo [ERROR] Could not create virtual environment.
        echo Check the log: %LOG%
        call :pause_keep
        goto :end
    )
    del "%LOG%.tmp" 2>nul
    call :log "venv created OK"
    echo [OK] Virtual environment created.
    echo.
) else (
    call :log "venv already exists, skipping"
)

REM --- Instalar dependencias si faltan ---
".venv\Scripts\python.exe" -c "import PySide6, pynput" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing dependencies (first time, 1-3 minutes)
    echo         This may take a while. Please be patient.
    call :log "Installing dependencies (pip install -r requirements.txt)"
    ".venv\Scripts\python.exe" -m pip install --upgrade pip > "%LOG%.pip" 2>&1
    if errorlevel 1 (
        call :log "[ERROR] pip upgrade failed"
        type "%LOG%.pip" >> "%LOG%"
        del "%LOG%.pip" 2>nul
        echo [ERROR] pip upgrade failed. Check the log: %LOG%
        call :pause_keep
        goto :end
    )
    del "%LOG%.pip" 2>nul
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt > "%LOG%.pip" 2>&1
    if errorlevel 1 (
        call :log "[ERROR] pip install -r requirements.txt failed"
        type "%LOG%.pip" >> "%LOG%"
        del "%LOG%.pip" 2>nul
        echo [ERROR] pip install failed. Check the log: %LOG%
        call :pause_keep
        goto :end
    )
    del "%LOG%.pip" 2>nul
    call :log "Dependencies installed OK"
    echo [OK] Dependencies installed.
    echo.
) else (
    call :log "Dependencies already installed"
)

REM --- Lanzar la app ---
echo [INFO] Starting MouseRecorder
call :log "Launching app: .venv\Scripts\python.exe main.py"
echo.
".venv\Scripts\python.exe" main.py > "%LOG%.app" 2>&1
set "RC=%errorlevel%"
call :log "App exited with code !RC!"
type "%LOG%.app" >> "%LOG%"
del "%LOG%.app" 2>nul

if not "!RC!"=="0" (
    echo.
    echo ===========================================
    echo [ERROR] The application exited with code !RC!.
    echo ===========================================
    echo Log: %LOG%
    echo.
)

call :log "=== Launcher finished ==="
echo.
echo ===========================================
echo  MouseRecorder closed. Press any key
echo  to close this window.
echo  (Log saved to last_run.log)
echo ===========================================
pause
goto :end

:end
endlocal
exit /b 0

REM =====================================================
REM  Subroutines
REM =====================================================

:log
set /a STEP+=1 >nul
echo [%date% %time%] STEP!STEP!: %~1 >> "%LOG%"
goto :eof

:pause_keep
echo.
echo ===========================================
echo  Something failed. Check the log for details:
echo    %LOG%
echo  Run diagnostico.bat if you need help.
echo ===========================================
pause
goto :eof
