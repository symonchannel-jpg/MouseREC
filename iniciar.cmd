@echo off
REM =============================================================
REM  iniciar.cmd - runs the app with a double-click
REM
REM  The window stays open because ejecutar.bat
REM  ends with a 'pause'.
REM =============================================================
cd /d "%~dp0"
call "%~dp0ejecutar.bat"
