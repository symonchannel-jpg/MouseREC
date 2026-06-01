@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

echo.
echo ===========================================
echo    MouseRecorder - Compilando .exe
echo ===========================================
echo.

REM --- Buscar Python real (skipea el stub de Microsoft Store) ---
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
    echo [ERROR] No se encontro Python real.
    echo Instala Python 3.11 o superior desde https://www.python.org/downloads/
    echo (tildando "Add Python to PATH" durante la instalacion).
    pause
    exit /b 1
)

echo [OK] Python: !PYEXE!
for /f "delims=" %%V in ('"!PYEXE!" --version 2^>^&1') do echo        %%V
echo.

REM --- Crear venv si no existe ---
if not exist ".venv\Scripts\python.exe" (
    echo [INFO] Creando entorno virtual...
    "!PYEXE!" -m venv .venv
    if errorlevel 1 (
        echo [ERROR] No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
)

REM --- Instalar dependencias si faltan ---
".venv\Scripts\python.exe" -c "import PySide6, pynput, PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Instalando dependencias...
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    if errorlevel 1 goto :failed
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 goto :failed
)

echo [INFO] Compilando MouseRecorder.exe (puede tardar 1-2 minutos)...
echo.

".venv\Scripts\python.exe" -m PyInstaller ^
    --noconfirm ^
    --onefile ^
    --windowed ^
    --name "MouseRecorder" ^
    --add-data "assets;assets" ^
    --icon "assets/icon.ico" ^
    --collect-all pynput ^
    --collect-all PySide6 ^
    main.py

if errorlevel 1 goto :failed

echo.
echo ===========================================
echo [OK] Compilacion exitosa.
echo ===========================================
echo.
echo El ejecutable quedo en:
echo   %CD%\dist\MouseRecorder.exe
echo.
echo Ya podes hacer doble clic en MouseRecorder.exe
echo o copiarlo a cualquier parte de tu PC.
echo.
pause
endlocal & exit /b 0

:failed
echo.
echo ===========================================
echo [ERROR] Fallo la compilacion.
echo ===========================================
echo.
echo Revisa los mensajes anteriores. Causas comunes:
echo  - Antivirus bloqueando PyInstaller
echo  - Permisos insuficientes (proba como Administrador)
echo  - Falta de espacio en disco
echo.
pause
endlocal & exit /b 1
