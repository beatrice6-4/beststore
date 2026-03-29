@echo off
echo ==========================================
echo BestStore IIS Diagnostic Tool
echo ==========================================
echo.

cd /d "C:\Users\BRAMWEL\OneDrive\Desktop\BESTSTORE"

echo 1. Checking Python virtual environment...
if exist "venv\Scripts\python.exe" (
    echo    ✓ Virtual environment found
    venv\Scripts\python.exe --version
) else (
    echo    ✗ Virtual environment NOT found
    echo    Please create it with: python -m venv venv
    goto :error
)

echo.
echo 2. Checking required files...
set "files=manage.py beststore\settings.py beststore\wsgi.py web.config db.sqlite3 requirements.txt"
for %%f in (%files%) do (
    if exist "%%f" (
        echo    ✓ %%f
    ) else (
        echo    ✗ %%f (MISSING)
    )
)

echo.
echo 3. Checking Django packages...
venv\Scripts\pip.exe show gunicorn django >nul 2>&1
if %errorlevel% equ 0 (
    echo    ✓ Django and Gunicorn installed
) else (
    echo    ✗ Django or Gunicorn not installed
    echo    Run: pip install -r requirements.txt
)

echo.
echo 4. Checking IIS status...
netstat -ano | findstr ":20306" >nul 2>&1
if %errorlevel% equ 0 (
    echo    ✓ Port 20306 is in use (IIS listening)
) else (
    echo    ⚠ Port 20306 not in use - IIS may not be running
)

netstat -ano | findstr ":8000" >nul 2>&1
if %errorlevel% equ 0 (
    echo    ✓ Port 8000 is in use (Django app running)
) else (
    echo    ⚠ Port 8000 not in use - Django app not running
)

echo.
echo 5. Checking static files...
if exist "staticfiles\" (
    for /f %%c in ('dir /b /s staticfiles\ ^| find /c "::"') do set count=%%c
    echo    ✓ Static files directory exists (%count% files)
) else (
    echo    ⚠ Static files not collected
    echo    Run: python manage.py collectstatic --noinput
)

echo.
echo ==========================================
echo Diagnostic Complete
echo ==========================================
echo.
echo If you see errors above, fix them first.
echo.
echo To start the application:
echo 1. Run: start_beststore.bat (keep it running)
echo 2. Open: http://localhost:20306
echo.
echo Press any key to exit...
pause >nul
goto :eof

:error
echo.
echo Errors found. Please fix them before continuing.
echo.
pause
exit /b 1