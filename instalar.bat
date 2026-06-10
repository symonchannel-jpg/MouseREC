@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

set "REPO_URL=https://github.com/symonchannel-jpg/MouseREC.git"
set "FOLDER=MouseRecorder"

echo.
echo    /'\_/`\                            /\ \
echo   /\      \    ___     ___     ____   \ \ \____    ___     ___
echo   \ \ \__\ \  / __`\ /' _ `\  /',__\   \ \ '__`\  / __`\ /' _ `\
echo    \ \ \_/\ \/\ \L\ \/\ \/\ \/\__, `\   \ \ \L\ \/\ \L\ \/\ \/\ \
echo     \ \_\\ \_\ \____/\ \_\ \_\/\____/    \ \_,__/\ \____/\ \_\ \_\
echo      \/_/ \/_/\/___/  \/_/\/_/\/___/      \/___/  \/___/  \/_/\/_/
echo                         by Simon
echo.
echo ===========================================
echo   One-click installer
echo ===========================================
echo.

REM --- Check git ---
echo [1/3] Checking for Git...
where git >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git not found.
    echo Download from: https://git-scm.com/download/win
    pause
    exit /b 1
)
echo [OK] Git found
echo.

REM --- Clone repo ---
if exist "%FOLDER%" (
    echo [2/3] Folder exists, updating...
    cd "%FOLDER%"
    git pull
    cd ..
) else (
    echo [2/3] Cloning repository...
    git clone "%REPO_URL%" "%FOLDER%"
    if errorlevel 1 (
        echo [ERROR] Clone failed. Check your internet.
        pause
        exit /b 1
    )
)
echo [OK] Repository ready
echo.

echo [3/3] Launching setup...
cd "%FOLDER%"
call ejecutar.bat
