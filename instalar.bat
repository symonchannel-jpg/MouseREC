@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

set "REPO_URL=https://github.com/symonchannel-jpg/MouseREC.git"
set "FOLDER=MouseRecorder"

echo ===========================================
echo    MouseRecorder - One-click installer
echo ===========================================
echo.

REM --- Check git ---
where git >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git not found.
    echo Download from: https://git-scm.com/download/win
    pause
    exit /b 1
)
echo [OK] Git found

REM --- Clone repo ---
if exist "%FOLDER%" (
    echo [INFO] Folder exists, updating...
    cd "%FOLDER%"
    git pull
    cd ..
) else (
    echo [INFO] Cloning repository...
    git clone "%REPO_URL%" "%FOLDER%"
    if errorlevel 1 (
        echo [ERROR] Clone failed. Check your internet.
        pause
        exit /b 1
    )
)
echo [OK] Repository ready

REM --- Delegate to the launcher ---
cd "%FOLDER%"
call ejecutar.bat
