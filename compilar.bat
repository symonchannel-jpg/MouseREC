@echo off
setlocal
cd /d "%~dp0"

set "PYEXE="
where py >nul 2>&1
if not errorlevel 1 set "PYEXE=py -3"
if "%PYEXE%"=="" (
    where python >nul 2>&1
    if not errorlevel 1 set "PYEXE=python"
)
if "%PYEXE%"=="" (
    echo No se encontro Python. Instala Python 3.11 o superior primero.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Creando entorno virtual...
    %PYEXE% -m venv .venv
    if errorlevel 1 goto error
)

".venv\Scripts\python.exe" -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo Instalando PyInstaller y dependencias...
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 goto error
)

echo.
echo Compilando MouseRecorder.exe (puede tardar 1-2 minutos)...
echo.

".venv\Scripts\python.exe" -m PyInstaller ^
    --noconfirm ^
    --onefile ^
    --windowed ^
    --name "MouseRecorder" ^
    --add-data "assets;assets" ^
    --icon "assets/icon.ico" ^
    --collect-all pynput ^
    main.py

if errorlevel 1 goto error

echo.
echo Listo. El ejecutable quedo en:
echo   %CD%\dist\MouseRecorder.exe
echo.
pause
exit /b 0

:error
echo.
echo Fallo la compilacion. Revisa los mensajes anteriores.
echo.
pause
endlocal
