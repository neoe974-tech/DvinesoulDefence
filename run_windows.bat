@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher not found. Install Python 3.12 or 3.13 from https://www.python.org/downloads/windows/
  echo During setup, enable the option to install the Python launcher.
  pause
  exit /b 1
)
py -3.12 -c "import tkinter" >nul 2>nul
if errorlevel 1 (
  py -3.13 -c "import tkinter" >nul 2>nul
  if errorlevel 1 (
    echo Python with Tkinter was not found. Re-run the official Python installer and enable Tcl/Tk and IDLE.
    pause
    exit /b 1
  )
  set PYTHON=py -3.13
) else (
  set PYTHON=py -3.12
)
%PYTHON% -m pip install --upgrade pip
if errorlevel 1 goto failed
%PYTHON% -m pip install -r requirements-windows.txt
if errorlevel 1 goto failed
%PYTHON% app\main.py
if errorlevel 1 goto failed
exit /b 0
:failed
echo.
echo Startup failed. Read the error above; check Python/Tkinter and network access for package installation.
pause
exit /b 1
