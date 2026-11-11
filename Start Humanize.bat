@echo off
rem Double-click to open the Humanize kit in your browser. Keep this window open while you use it.
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 tools\app.py
  goto end
)
where python >nul 2>nul
if %errorlevel%==0 (
  python tools\app.py
  goto end
)
echo.
echo Python is not installed on this computer.
echo Get it free from https://www.python.org/downloads/
echo During setup, tick "Add python.exe to PATH". Then double-click this file again.
echo.
:end
pause
