@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

echo.
echo ===========================================
echo    MouseRecorder - Compilando .exe
echo ===========================================
echo.

REM --- Buscar Python en PATH y en rutas comunes ---
set "PYEXE="
where py >nul 2>&1
if not errorlevel 1 set "PYEXE=py -3"
if "!PYEXE!"=="" (
    where python >nul 2>&1
    if not errorlevel 1 set "PYEXE=python"
)
if "!PYEXE!"=="" (
    for %%P in (
        "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
        "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
        "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
        "C:\Python311\python.exe"
        "C:\Python312\python.exe"
        "C:\Python313\python.exe"
        "%USERPROFILE%\AppData\Local\Programs\Python\Python311\python.exe"
        "%USERPROFILE%\AppData\Local\Programs\Python\Python312\python.exe"
        "%USERPROFILE%\AppData\Local\Programs\Python\Python313\python.exe"
    ) do (
        if exist %%P (
            set "PYEXE=%%~P"
            goto :py_found
        )
    )
)

:py_found
if "!PYEXE!"=="" (
    echo [ERROR] No se encontro Python.
    echo Instala Python 3.11 o superior desde https://www.python.org/downloads/
    echo (tildando "Add Python to PATH" durante la instalacion).
    echo.
    pause
    exit /b 1
)

echo [OK] Python: !PYEXE!
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
echo  - Permisos insuficientes (proba ejecutar como Administrador)
echo  - Falta de espacio en disco
echo.
pause
endlocal & exit /b 1
