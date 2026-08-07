@echo off
REM ── เปิดเว็บตารางเรือ LNG (ดับเบิลคลิกไฟล์นี้ได้เลย) ──
title LNG Vessel Schedule Server
cd /d "%~dp0"
"C:\Users\lng660008\AppData\Local\Python\pythoncore-3.14-64\python.exe" serve.py
echo.
echo Server หยุดทำงานแล้ว — กดปุ่มใดก็ได้เพื่อปิดหน้าต่าง
pause >nul
