@echo off
REM =============================================================
REM  iniciar.cmd - ejecuta la app con doble clic
REM
REM  La ventana queda abierta porque ejecutar.bat
REM  termina con un 'pause'.
REM =============================================================
cd /d "%~dp0"
call "%~dp0ejecutar.bat"
