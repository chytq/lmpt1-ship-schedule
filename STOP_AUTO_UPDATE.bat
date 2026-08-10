@echo off
chcp 65001 >nul
REM Turn OFF auto-update
title Stop Auto Update - LNG Vessel Schedule
cd /d "%~dp0"
call "%~dp0_findpython.bat" || exit /b 1
%PY% setup_auto.py off
echo.
pause
