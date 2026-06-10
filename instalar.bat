@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

set "REPO_URL=https://github.com/symonchannel-jpg/MouseREC.git"
set "FOLDER=MouseRecorder"

echo.
echo ÛÛÛ»   ÛÛÛ» ÛÛÛÛÛÛ» ÛÛ»   ÛÛ»ÛÛÛÛÛÛÛ»ÛÛÛÛÛÛÛ»    ÛÛÛÛÛÛ» ÛÛÛÛÛÛÛ» ÛÛÛÛÛÛ»
echo ÛÛÛÛ» ÛÛÛÛºÛÛÉÍÍÍÛÛ»ÛÛº   ÛÛºÛÛÉÍÍÍÍ¼ÛÛÉÍÍÍÍ¼    ÛÛÉÍÍÛÛ»ÛÛÉÍÍÍÍ¼ÛÛÉÍÍÍÍ¼
echo ÛÛÉÛÛÛÛÉÛÛºÛÛº   ÛÛºÛÛº   ÛÛºÛÛÛÛÛÛÛ»ÛÛÛÛÛ»      ÛÛÛÛÛÛÉ¼ÛÛÛÛÛ»  ÛÛº
echo ÛÛºÈÛÛÉ¼ÛÛºÛÛº   ÛÛºÛÛº   ÛÛºÈÍÍÍÍÛÛºÛÛÉÍÍ¼      ÛÛÉÍÍÛÛ»ÛÛÉÍÍ¼  ÛÛº
echo ÛÛº ÈÍ¼ ÛÛºÈÛÛÛÛÛÛÉ¼ÈÛÛÛÛÛÛÉ¼ÛÛÛÛÛÛÛºÛÛÛÛÛÛÛ»    ÛÛº  ÛÛºÛÛÛÛÛÛÛ»ÈÛÛÛÛÛÛ»
echo ÈÍ¼     ÈÍ¼ ÈÍÍÍÍÍ¼  ÈÍÍÍÍÍ¼ ÈÍÍÍÍÍÍ¼ÈÍÍÍÍÍÍ¼    ÈÍ¼  ÈÍ¼ÈÍÍÍÍÍÍ¼ ÈÍÍÍÍÍ¼
echo                         by Simon
echo.
echo ===========================================
echo   One-click installer
echo ===========================================
echo.

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

echo [2/3] Setting up repository...
if exist "%FOLDER%" (
    echo [INFO] Folder exists, updating...
    cd "%FOLDER%"
    git pull
    cd ..
) else (
    git clone "%REPO_URL%" "%FOLDER%"
    if errorlevel 1 (
        echo [ERROR] Clone failed.
        pause
        exit /b 1
    )
)
echo [OK] Repository ready
echo.

echo [3/3] Launching setup...
cd "%FOLDER%"
call ejecutar.bat