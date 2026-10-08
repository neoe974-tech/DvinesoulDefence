@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul || (echo Python launcher missing. Install Python 3.12 or 3.13 from python.org.& pause & exit /b 1)
py -3.12 -c "import tkinter" >nul 2>nul
if errorlevel 1 (
  py -3.13 -c "import tkinter" >nul 2>nul
  if errorlevel 1 (echo Python with Tkinter is required. Enable Tcl/Tk in the official Python installer.& pause & exit /b 1)
  set PY=py -3.13
) else (
  set PY=py -3.12
)
%PY% -m pip install --upgrade pip
if errorlevel 1 goto failed
%PY% -m pip install -r requirements-windows.txt
if errorlevel 1 goto failed
%PY% -m unittest discover -s tests -v
if errorlevel 1 goto failed
%PY% -m PyInstaller --noconfirm --clean --windowed --name DvinesoulDefence --collect-all scapy app\main.py
if errorlevel 1 goto failed
echo.
echo Build complete: dist\DvinesoulDefence\DvinesoulDefence.exe
echo IMPORTANT: live packet capture still needs Npcap installed on the target Windows PC.
echo Package the entire dist\DvinesoulDefence folder, not only the EXE.
pause
exit /b 0
:failed
echo.
echo Build failed. Review the error above before distributing the application.
pause
exit /b 1
