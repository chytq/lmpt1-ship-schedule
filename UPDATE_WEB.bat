@echo off
REM ─────────────────────────────────────────────────────────────
REM  อัปเดตเว็บบน GitHub Pages — ใช้หลังแก้ไฟล์ Excel เสร็จ
REM  ดับเบิลคลิกไฟล์นี้ได้เลย
REM ─────────────────────────────────────────────────────────────
title อัปเดตเว็บตารางเรือ
cd /d "%~dp0"

set PY="C:\Users\lng660008\AppData\Local\Python\pythoncore-3.14-64\python.exe"

echo.
echo  [1/3] สร้างหน้าเว็บใหม่จากไฟล์ Excel ...
%PY% build_static.py %*
if %errorLevel% neq 0 goto :fail

echo.
echo  [2/3] บันทึกการเปลี่ยนแปลง ...
git add -A
git diff --cached --quiet
if %errorLevel% equ 0 (
    echo        ไม่มีอะไรเปลี่ยน - ข้อมูลบนเว็บตรงกับ Excel อยู่แล้ว
    goto :done
)
for /f "tokens=1-3 delims=/ " %%a in ('date /t') do set TODAY=%%a-%%b-%%c
git commit -q -m "update schedule %TODAY%"
if %errorLevel% neq 0 goto :fail

echo.
echo  [3/3] ส่งขึ้น GitHub ...
git push
if %errorLevel% neq 0 goto :fail

echo.
echo  ─────────────────────────────────────────────
echo   เสร็จแล้ว! เว็บจะอัปเดตภายใน 1-2 นาที
echo  ─────────────────────────────────────────────
goto :done

:fail
echo.
echo  [X] มีข้อผิดพลาด - อ่านข้อความด้านบน
echo.

:done
echo.
pause
