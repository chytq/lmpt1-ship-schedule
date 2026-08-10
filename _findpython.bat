@echo off
REM Locate a usable Python and set %PY%. Called by the other .bat files.
REM Kept ASCII-only: non-ASCII text breaks cmd.exe parsing.

set PY=

REM 1) Windows Python launcher (most reliable)
where py >nul 2>&1
if not errorlevel 1 (
    py -3 -c "import sys" >nul 2>&1
    if not errorlevel 1 set PY=py -3
)

REM 2) python on PATH
if not defined PY (
    where python >nul 2>&1
    if not errorlevel 1 (
        python -c "import sys" >nul 2>&1
        if not errorlevel 1 set PY=python
    )
)

if not defined PY (
    echo.
    echo   [!] Python not found.
    echo       Install Python 3.10+ from https://www.python.org/downloads/
    echo       and tick "Add python.exe to PATH" during setup.
    echo.
    pause
    exit /b 1
)

exit /b 0
