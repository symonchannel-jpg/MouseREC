@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

set "LOG=%~dp0last_compile.log"
set "STEP=0"

call :log "=== MouseRecorder compiler started ==="
call :log "Working dir: %CD%"

echo.
echo ===========================================
echo    MouseRecorder - Building .exe
echo ===========================================
echo.
echo If this window closes by itself, send me the file:
echo   %LOG%
echo.

REM --- Buscar Python real ---
set "PYEXE="
for %%V in (313 312 311 310 39) do (
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
    call :pause_keep
    goto :end
)
call :log "Python: !PYEXE!"
echo [OK] Python: !PYEXE!
for /f "delims=" %%V in ('"!PYEXE!" --version 2^>^&1') do (
    call :log "Python version: %%V"
    echo        %%V
)
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [INFO] Creating virtual environment
    call :log "Creating venv"
    "!PYEXE!" -m venv .venv > "%LOG%.tmp" 2>&1
    if errorlevel 1 (
        type "%LOG%.tmp" >> "%LOG%"
        del "%LOG%.tmp" 2>nul
        call :log "[ERROR] venv creation failed"
        echo [ERROR] Could not create venv. Check the log.
        call :pause_keep
        goto :end
    )
    del "%LOG%.tmp" 2>nul
    call :log "venv created"
    echo [OK] Virtual environment created.
    echo.
)

".venv\Scripts\python.exe" -c "import PySide6, pynput, PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing dependencies
    call :log "Installing deps"
    ".venv\Scripts\python.exe" -m pip install --upgrade pip > "%LOG%.pip" 2>&1
    if errorlevel 1 goto :pip_failed
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt > "%LOG%.pip" 2>&1
    if errorlevel 1 goto :pip_failed
    del "%LOG%.pip" 2>nul
    call :log "Deps installed"
)

echo [INFO] Building MouseRecorder.exe (may take 1-3 minutes)
echo.
call :log "Running PyInstaller"
".venv\Scripts\python.exe" -m PyInstaller ^
    --noconfirm ^
    --onefile ^
    --windowed ^
    --name "MouseRecorder" ^
    --add-data "assets;assets" ^
    --icon "assets/icon.ico" ^
    --collect-all pynput ^
    --collect-all PySide6 ^
    main.py > "%LOG%.pyi" 2>&1
if errorlevel 1 goto :compile_failed
del "%LOG%.pyi" 2>nul
call :log "PyInstaller OK"

echo.
echo ===========================================
echo [OK] Build successful.
echo ===========================================
echo.
echo The executable is at:
echo   %CD%\dist\MouseRecorder.exe
echo.
echo You can double-click MouseRecorder.exe
echo or copy it anywhere on your PC.
echo.
call :log "=== Compile finished OK ==="
echo Press any key to close.
pause
goto :end

:pip_failed
type "%LOG%.pip" >> "%LOG%" 2>nul
del "%LOG%.pip" 2>nul
call :log "[ERROR] pip install failed"
echo.
echo [ERROR] pip install failed. Check the log: %LOG%
echo.
pause
goto :end

:compile_failed
type "%LOG%.pyi" >> "%LOG%" 2>nul
del "%LOG%.pyi" 2>nul
call :log "[ERROR] PyInstaller failed"
echo.
echo ===========================================
echo [ERROR] Build failed.
echo ===========================================
echo Check the log: %LOG%
echo.
pause
goto :end

:end
endlocal
exit /b 0

REM =====================================================

:log
set /a STEP+=1 >nul
echo [%date% %time%] STEP!STEP!: %~1 >> "%LOG%"
goto :eof

:pause_keep
echo.
echo Something failed. Check the log: %LOG%
echo.
pause
goto :eof
