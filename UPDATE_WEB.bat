@echo off
chcp 65001 >nul
title Update LNG Vessel Schedule Website
cd /d "%~dp0"
"C:\Users\lng660008\AppData\Local\Python\pythoncore-3.14-64\python.exe" update_web.py %*
echo.
pause
