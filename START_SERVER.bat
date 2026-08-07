@echo off
chcp 65001 >nul
REM Start the LNG Vessel Schedule web server on this PC
title LNG Vessel Schedule Server
cd /d "%~dp0"
"C:\Users\lng660008\AppData\Local\Python\pythoncore-3.14-64\python.exe" serve.py
echo.
echo Server stopped. Press any key to close.
pause >nul
