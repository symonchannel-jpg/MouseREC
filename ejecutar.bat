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
    echo.
    echo No se encontro Python. Instala Python 3.11 o superior desde
    echo https://www.python.org/downloads/  (tilda "Add Python to PATH").
    echo.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Creando entorno virtual...
    %PYEXE% -m venv .venv
    if errorlevel 1 goto error
)

".venv\Scripts\python.exe" -c "import PySide6, pynput" >nul 2>&1
if errorlevel 1 (
    echo Instalando dependencias...
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 goto error
)

echo Iniciando MouseRecorder...
".venv\Scripts\python.exe" main.py
exit /b %errorlevel%

:error
echo.
echo No se pudo iniciar MouseRecorder.
echo Revisa los mensajes anteriores para ver el error exacto.
echo.
pause
endlocal
