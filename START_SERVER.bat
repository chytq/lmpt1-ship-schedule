@echo off
chcp 65001 >nul
REM Start the LNG Vessel Schedule web server on this PC
title LNG Vessel Schedule Server
cd /d "%~dp0"
call "%~dp0_findpython.bat" || exit /b 1
%PY% serve.py
echo.
echo Server stopped. Press any key to close.
pause >nul
