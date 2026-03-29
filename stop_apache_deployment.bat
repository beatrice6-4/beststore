@echo off
echo Stopping BestStore Django Application...

REM Stop Apache
net stop Apache2.4

REM Kill any remaining waitress processes
taskkill /f /im python.exe /fi "WINDOWTITLE eq Django Server*" 2>nul

echo.
echo Services stopped.
echo.
pause