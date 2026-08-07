@echo off
REM ─────────────────────────────────────────────────────────────
REM  ตั้งค่าครั้งเดียว — ต้องคลิกขวา > "Run as administrator"
REM  1) เปิด firewall port 5000 ให้เพื่อนในบริษัทเข้าเว็บได้
REM  2) ตั้งให้เว็บเปิดเองอัตโนมัติทุกครั้งที่ login เข้าเครื่อง
REM ─────────────────────────────────────────────────────────────
title Setup - LNG Vessel Schedule

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo   [!] ต้องรันแบบ Administrator
    echo       คลิกขวาที่ไฟล์นี้ ^> "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo.
echo  [1/2] เปิด firewall port 5000 ...
netsh advfirewall firewall delete rule name="LNG Vessel Schedule" >nul 2>&1
netsh advfirewall firewall add rule name="LNG Vessel Schedule" ^
    dir=in action=allow protocol=TCP localport=5000 profile=domain
if %errorLevel% equ 0 (echo        OK) else (echo        FAILED)

echo.
echo  [2/2] ตั้งให้เปิดเว็บอัตโนมัติตอน login ...
schtasks /delete /tn "LNG Vessel Schedule" /f >nul 2>&1
schtasks /create /tn "LNG Vessel Schedule" ^
    /tr "\"%~dp0START_SERVER.bat\"" ^
    /sc onlogon /rl highest /f
if %errorLevel% equ 0 (echo        OK) else (echo        FAILED)

echo.
echo  ─────────────────────────────────────────────
echo   เสร็จแล้ว! ส่งลิงก์นี้ให้เพื่อนร่วมงาน:
echo.
echo       http://%COMPUTERNAME%:5000
echo.
echo   หมายเหตุ: เครื่องนี้ต้องเปิดอยู่ตลอด เพื่อนถึงจะเข้าได้
echo  ─────────────────────────────────────────────
echo.
pause
