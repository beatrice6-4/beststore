@echo off
echo ==========================================
echo Starting BestStore Django Application
echo ==========================================
echo.

cd /d "C:\Users\BRAMWEL\OneDrive\Desktop\BESTSTORE"

echo 1. Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Could not activate virtual environment
    pause
    exit /b 1
)
echo    ✓ Virtual environment activated

echo.
echo 2. Installing Gunicorn (if needed)...
pip install gunicorn --quiet
if errorlevel 1 (
    echo ERROR: Could not install Gunicorn
    pause
    exit /b 1
)
echo    ✓ Gunicorn ready

echo.
echo 3. Collecting static files...
python manage.py collectstatic --noinput
if errorlevel 1 (
    echo ERROR: Could not collect static files
    pause
    exit /b 1
)
echo    ✓ Static files collected

echo.
echo 4. Running database migrations...
python manage.py migrate
if errorlevel 1 (
    echo ERROR: Could not run migrations
    pause
    exit /b 1
)
echo    ✓ Database migrations complete

echo.
echo ==========================================
echo Starting Gunicorn server on localhost:8000
echo ==========================================
echo.
echo Application will be accessible at: http://localhost:20306
echo.
echo Press Ctrl+C to stop the server
echo.
echo ==========================================

gunicorn --bind 127.0.0.1:8000 --workers 4 --worker-class sync --timeout 120 --access-logfile - --error-logfile - beststore.wsgi:application

echo.
echo Server stopped. Press any key to exit...
pause >nul