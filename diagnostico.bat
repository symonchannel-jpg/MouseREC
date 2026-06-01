@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

echo.
echo ===========================================
echo    MouseRecorder - Diagnostico
echo ===========================================
echo.

echo --- Python en PATH (puede incluir el stub de Microsoft Store) ---
where py 2>nul
where python 2>nul
echo.

echo --- Python REAL instalado (sin contar el stub de Microsoft Store) ---
set "FOUND_PY="
for %%V in (313 312 311 310 39) do (
    for %%P in (
        "%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe"
        "%USERPROFILE%\AppData\Local\Programs\Python\Python%%V\python.exe"
        "C:\Python%%V\python.exe"
        "C:\Program Files\Python%%V\python.exe"
    ) do (
        if exist %%P (
            echo   - %%~P
            if not defined FOUND_PY set "FOUND_PY=%%~P"
        )
    )
)
echo.

echo --- Python que va a usar ejecutar.bat ---
if defined FOUND_PY (
    echo   !FOUND_PY!
    echo.
    echo   Probando:
    "!FOUND_PY!" --version 2>&1
) else (
    echo   [NO ENCONTRADO]
    echo   Instala Python 3.11+ desde https://www.python.org/downloads/
)
echo.

echo --- Entorno virtual ---
if exist ".venv\Scripts\python.exe" (
    echo   Existe: .venv\Scripts\python.exe
    ".venv\Scripts\python.exe" --version
    echo.
    echo --- Paquetes en el venv ---
    ".venv\Scripts\python.exe" -m pip list 2>nul | findstr /i "PySide6 pynput PyInstaller"
) else (
    echo   NO existe. Se creara al ejecutar ejecutar.bat.
)
echo.

echo --- Archivos del proyecto ---
if exist "main.py"              echo   [OK] main.py
if exist "requirements.txt"     echo   [OK] requirements.txt
if exist "src\ui\app.py"        echo   [OK] src\ui\app.py
if exist "assets\icon.ico"      echo   [OK] assets\icon.ico
if exist "ejecutar.bat"         echo   [OK] ejecutar.bat
if exist "compilar.bat"         echo   [OK] compilar.bat
if exist "diagnostico.bat"      echo   [OK] diagnostico.bat
echo.

echo --- Test rapido de importacion (si venv existe) ---
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -c "import sys, PySide6, pynput; print('   [OK] Python', sys.version.split()[0], '| PySide6', PySide6.__version__, '| pynput', pynput.__version__)" 2>&1
) else (
    echo   (sin venv todavia - ejecuta ejecutar.bat primero)
)
echo.

echo ===========================================
echo  Diagnostico terminado.
echo  Si algo falla, mandame esta salida.
echo ===========================================
echo.
pause
endlocal
