@echo off
chcp 65001 >nul
title Update LNG Vessel Schedule Website
cd /d "%~dp0"
call "%~dp0_findpython.bat" || exit /b 1
%PY% update_web.py %*
echo.
pause
