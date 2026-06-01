@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

echo.
echo ===========================================
echo    MouseRecorder - Diagnostico
echo ===========================================
echo.

echo --- Python ---
where py 2>nul
where python 2>nul
echo.

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
    if exist %%P echo Instalado: %%~P
)
echo.

if exist ".venv\Scripts\python.exe" (
    echo --- Entorno virtual ---
    echo Existe: .venv\Scripts\python.exe
    echo Version:
    ".venv\Scripts\python.exe" --version
    echo.
    echo --- Paquetes instalados ---
    ".venv\Scripts\python.exe" -m pip list 2>nul | findstr /i "PySide6 pynput PyInstaller"
) else (
    echo --- Entorno virtual ---
    echo NO existe. Se creara al ejecutar ejecutar.bat.
)
echo.

echo --- Archivos del proyecto ---
if exist "main.py" echo [OK] main.py
if exist "requirements.txt" echo [OK] requirements.txt
if exist "src\ui\app.py" echo [OK] src\ui\app.py
if exist "assets\icon.ico" echo [OK] assets\icon.ico
if exist "ejecutar.bat" echo [OK] ejecutar.bat
if exist "compilar.bat" echo [OK] compilar.bat
echo.

echo --- Probando importacion (si venv existe) ---
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -c "import PySide6, pynput; print('[OK] PySide6 + pynput importan correctamente')" 2>&1
)
echo.

echo ===========================================
echo  Diagnostico terminado.
echo  Captura esta pantalla si necesitas ayuda.
echo ===========================================
echo.
pause
endlocal
