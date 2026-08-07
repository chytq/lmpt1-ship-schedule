@echo off
chcp 65001 >nul
REM Turn ON auto-update. No administrator rights needed.
title Setup Auto Update - LNG Vessel Schedule
cd /d "%~dp0"
"C:\Users\lng660008\AppData\Local\Python\pythoncore-3.14-64\python.exe" setup_auto.py on
echo.
pause
