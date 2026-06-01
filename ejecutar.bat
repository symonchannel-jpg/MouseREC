@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

echo.
echo ===========================================
echo    MouseRecorder - Iniciando...
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

REM Si no se encontro en PATH, buscar en rutas comunes de Windows
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
    echo [ERROR] No se encontro Python en el sistema.
    echo.
    echo Pasos para solucionarlo:
    echo   1. Instala Python 3.11 o superior desde:
    echo      https://www.python.org/downloads/
    echo.
    echo   2. MUY IMPORTANTE: en la primera pantalla del instalador,
    echo      tilda la casilla "Add Python to PATH" antes de continuar.
    echo.
    echo   3. Reinstala si ya lo tenias y te olvidaste de ese paso.
    echo.
    pause
    exit /b 1
)

echo [OK] Python: !PYEXE!
echo.

REM --- Crear venv si no existe ---
if not exist ".venv\Scripts\python.exe" (
    echo [INFO] Creando entorno virtual (primera vez, ~30 segundos)...
    "!PYEXE!" -m venv .venv
    if errorlevel 1 (
        echo.
        echo [ERROR] No se pudo crear el entorno virtual.
        echo.
        echo Si tu usuario no tiene permisos para escribir en esta carpeta,
        echo proba ejecutar este .bat como Administrador (clic derecho -^
        " Ejecutar como administrador).
        echo.
        pause
        exit /b 1
    )
    echo [OK] Entorno virtual creado.
    echo.
)

REM --- Instalar dependencias si faltan ---
".venv\Scripts\python.exe" -c "import PySide6, pynput" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Instalando dependencias (primera vez, 1-2 minutos)...
    echo.
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    if errorlevel 1 goto :pip_failed
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 goto :pip_failed
    echo.
    echo [OK] Dependencias instaladas.
    echo.
)

REM --- Lanzar la app ---
echo [INFO] Iniciando MouseRecorder...
echo.
".venv\Scripts\python.exe" main.py
set "RC=%errorlevel%"

if not "!RC!"=="0" (
    echo.
    echo ===========================================
    echo [ERROR] La aplicacion termino con codigo !RC!.
    echo ===========================================
    echo.
    echo Posibles causas:
    echo   - Antivirus bloqueando pynput o PySide6
    echo   - Permisos insuficientes
    echo.
    echo Proba ejecutar como Administrador.
    echo.
)

echo.
echo Presiona cualquier tecla para cerrar...
pause >nul
endlocal & exit /b %RC%

:pip_failed
echo.
echo [ERROR] No se pudieron instalar las dependencias.
echo.
echo Posibles causas:
echo   - Sin conexion a internet
echo   - Firewall o proxy bloqueando pip
echo   - Permisos insuficientes
echo.
echo Proba ejecutar como Administrador o revis tu conexion.
echo.
pause
endlocal & exit /b 1
