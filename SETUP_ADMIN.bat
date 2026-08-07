@echo off
REM ============================================================
REM  Setup once - right-click this file > "Run as administrator"
REM  ASCII only on purpose: non-ASCII text breaks cmd.exe parsing
REM    1) open firewall port 5000 for colleagues on the LAN
REM    2) auto-start the local server at logon
REM  Not needed if you publish via GitHub Pages.
REM ============================================================
title Setup - LNG Vessel Schedule
cd /d "%~dp0"

net session >nul 2>&1
if errorlevel 1 (
    echo.
    echo   [!] Please run as Administrator
    echo       Right-click this file ^> "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo.
echo  [1/2] Opening firewall port 5000 ...
netsh advfirewall firewall delete rule name="LNG Vessel Schedule" >nul 2>&1
netsh advfirewall firewall add rule name="LNG Vessel Schedule" dir=in action=allow protocol=TCP localport=5000 profile=domain >nul
if errorlevel 1 (echo        FAILED) else (echo        OK)

echo.
echo  [2/2] Enabling auto-start at logon ...
schtasks /delete /tn "LNG Vessel Schedule" /f >nul 2>&1
schtasks /create /tn "LNG Vessel Schedule" /tr "\"%~dp0START_SERVER.bat\"" /sc onlogon /rl highest /f >nul
if errorlevel 1 (echo        FAILED) else (echo        OK)

echo.
echo  ------------------------------------------------
echo   Done. Share this link with colleagues:
echo.
echo       http://%COMPUTERNAME%:5000
echo.
echo   This PC must stay on and connected to the
echo   corporate network for the link to work.
echo  ------------------------------------------------
echo.
pause
