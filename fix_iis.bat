@echo off
echo ==========================================
echo IIS Configuration Fix Tool
echo ==========================================
echo.

cd /d "C:\Users\BRAMWEL\OneDrive\Desktop\BESTSTORE"

echo Current web.config status:
if exist "web.config" (
    echo ✓ web.config exists
    echo.
    echo First few lines of web.config:
    type web.config | findstr /n "<?xml" | head -1
    type web.config | findstr /n "<configuration>" | head -1
    echo.
) else (
    echo ✗ web.config not found
)

echo.
echo IIS Site Status:
powershell -Command "Import-Module WebAdministration; Get-IISSite -Name 'BestStore' -ErrorAction SilentlyContinue | Select-Object Name, State, Bindings"

echo.
echo Available options:
echo 1. Use minimal web.config (backup)
echo 2. Reset IIS completely
echo 3. Check IIS logs
echo 4. Exit
echo.

set /p choice="Choose option (1-4): "

if "%choice%"=="1" (
    echo.
    echo Switching to minimal web.config...
    copy web.config web.config.backup 2>nul
    copy web.config.minimal web.config
    echo ✓ Switched to minimal configuration
    echo Restarting IIS...
    iisreset
    echo ✓ IIS restarted
    echo.
    echo Test: http://localhost:20306
    echo.
    pause
) else if "%choice%"=="2" (
    echo.
    echo Resetting IIS completely...
    iisreset /stop
    timeout /t 2 /nobreak >nul
    iisreset /start
    echo ✓ IIS reset complete
    echo.
    echo Test: http://localhost:20306
    echo.
    pause
) else if "%choice%"=="3" (
    echo.
    echo IIS Log Location: C:\inetpub\logs\LogFiles\
    echo.
    echo Recent log files:
    dir "C:\inetpub\logs\LogFiles\" /b /o-d 2>nul | findstr W3SVC | head -3
    echo.
    echo Press any key to continue...
    pause >nul
) else (
    echo.
    echo Exiting...
    timeout /t 1 /nobreak >nul
)

echo.
echo Done.
pause