@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

echo.
echo ===========================================
echo    MouseRecorder - Iniciando...
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
REM Fallback: usar 'py' (Python Launcher) si existe
if "!PYEXE!"=="" (
    where py >nul 2>&1
    if not errorlevel 1 set "PYEXE=py -3"
)

if "!PYEXE!"=="" (
    echo [ERROR] No se encontro Python real en el sistema.
    echo.
    echo Windows encontro solo el "stub" de Microsoft Store, que no sirve.
    echo.
    echo Pasos para solucionarlo:
    echo   1. Instala Python 3.11 o superior desde:
    echo      https://www.python.org/downloads/
    echo.
    echo   2. MUY IMPORTANTE: en la primera pantalla del instalador,
    echo      tilda "Add Python to PATH" antes de continuar.
    echo.
    echo   3. Si ya tenias Python pero solo aparece el stub,
    echo      desinstala el "Python 3.x" de Microsoft Store:
    echo      Configuracion -^> Aplicaciones -^> Python 3.x -^> Desinstalar
    echo.
    pause
    exit /b 1
)

REM Verificar que el Python elegido realmente funciona
"!PYEXE!" --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] El Python encontrado no responde:
    echo   !PYEXE!
    echo.
    echo Proba reinstalar Python desde python.org
    pause
    exit /b 1
)

echo [OK] Python: !PYEXE!
for /f "delims=" %%V in ('"!PYEXE!" --version 2^>^&1') do echo        %%V
echo.

REM --- Crear venv si no existe ---
if not exist ".venv\Scripts\python.exe" (
    echo [INFO] Creando entorno virtual (primera vez, ~30 segundos)...
    "!PYEXE!" -m venv .venv
    if errorlevel 1 (
        echo.
        echo [ERROR] No se pudo crear el entorno virtual.
        echo Si tu usuario no tiene permisos para escribir en esta carpeta,
        echo proba ejecutar este .bat como Administrador.
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
    echo Si necesitas ayuda, ejecuta diagnostico.bat primero.
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
echo Proba ejecutar como Administrador o revisa tu conexion.
echo.
pause
endlocal & exit /b 1
