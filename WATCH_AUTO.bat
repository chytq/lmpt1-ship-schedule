@echo off
chcp 65001 >nul
REM Watch the Excel file and auto-publish to GitHub Pages when it changes.
REM Keep this window open. Closing it stops the auto-update.
title Auto Update - LNG Vessel Schedule
cd /d "%~dp0"
"C:\Users\lng660008\AppData\Local\Python\pythoncore-3.14-64\python.exe" watch_excel.py %*
echo.
echo Watcher stopped. Press any key to close.
pause >nul
