@echo off
chcp 65001 >nul
REM ============================================================
REM  DEV MODE - runs the site on FAKE sample data.
REM  Never used for publishing: build_static.py refuses to run
REM  while USE_SAMPLE is set.
REM ============================================================
title DEV MODE (sample data) - LNG Vessel Schedule
cd /d "%~dp0"
call "%~dp0_findpython.bat" || exit /b 1

if not exist "sample\sample_work_plan.xlsx" (
    echo.
    echo   Sample data not found - generating it now ...
    %PY% sample\make_sample_excel.py
    echo.
)

set USE_SAMPLE=1
echo.
echo  ============================================================
echo   DEV MODE - FAKE DATA. Do not share this output.
echo   Open http://localhost:5000
echo  ============================================================
echo.
%PY% app.py
echo.
pause
