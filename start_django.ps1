# PowerShell Script to Run BestStore with Gunicorn on Port 20306
# This script starts the Django application server on a local port and proxies through IIS

$AppPath = "C:\Users\BRAMWEL\OneDrive\Desktop\BESTSTORE"
$VenvPath = "$AppPath\venv"
$InternalPort = 8000  # Django app server port
$IISPort = 20306      # IIS exposed port

Write-Host "==========================================" -ForegroundColor Green
Write-Host "Starting BestStore Django Application"
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

# Check if venv exists
if (-not (Test-Path "$VenvPath\Scripts\Activate.ps1")) {
    Write-Host "ERROR: Virtual environment not found at $VenvPath" -ForegroundColor Red
    exit 1
}

# Activate virtual environment
Write-Host "1. Activating virtual environment..." -ForegroundColor Yellow
& "$VenvPath\Scripts\Activate.ps1"

if (-not $?) {
    Write-Host "ERROR: Could not activate virtual environment" -ForegroundColor Red
    exit 1
}

Write-Host "   ✓ Virtual environment activated" -ForegroundColor Green

# Install Gunicorn if not already installed
Write-Host ""
Write-Host "2. Checking for Gunicorn..." -ForegroundColor Yellow
$gunicornCheck = python -m pip show gunicorn 2>&1
if (-not $gunicornCheck -or $gunicornCheck -like "*WARNING*") {
    Write-Host "   Installing Gunicorn..." -ForegroundColor Cyan
    python -m pip install gunicorn --quiet
    Write-Host "   ✓ Gunicorn installed" -ForegroundColor Green
} else {
    Write-Host "   ✓ Gunicorn is already installed" -ForegroundColor Green
}

# Run migrations
Write-Host ""
Write-Host "3. Running database migrations..." -ForegroundColor Yellow
python manage.py migrate
Write-Host "   ✓ Migrations complete" -ForegroundColor Green

# Collect static files
Write-Host ""
Write-Host "4. Collecting static files..." -ForegroundColor Yellow
python manage.py collectstatic --noinput
Write-Host "   ✓ Static files collected" -ForegroundColor Green

# Start Gunicorn
Write-Host ""
Write-Host "5. Starting Django application server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "   Starting Gunicorn on http://localhost:$InternalPort" -ForegroundColor Cyan
Write-Host "   Application will be accessible at http://localhost:$IISPort" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

gunicorn --bind 127.0.0.1:$InternalPort `
         --workers 4 `
         --worker-class sync `
         --timeout 120 `
         --access-logfile - `
         --error-logfile - `
         beststore.wsgi:application
