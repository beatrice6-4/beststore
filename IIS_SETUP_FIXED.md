# BestStore on IIS Port 20306 - Proper Setup Guide

## Issue Found: 500.19 Error

The previous web.config had invalid FastCGI syntax. The issue is that running Django directly on IIS is complex and requires multiple components.

## Correct Architecture

The proper way to run Django on Windows IIS is:

```
Client Browser (localhost:20306)
         ↓
    IIS (Port 20306) 
         ↓
  URL Rewrite Module
         ↓
Gunicorn App Server (localhost:8000)
         ↓
    Django App
         ↓
   SQLite DB
```

## Step 1: Install Required IIS Features

Open PowerShell as Administrator:

```powershell
# Install URL Rewrite module (required for reverse proxy)
# Download and install from: https://www.iis.net/downloads/microsoft/url-rewrite

# Then enable required Windows features:
Enable-WindowsOptionalFeature -Online -FeatureName IIS-URLRewrite -NoRestart
```

**Alternative**: Download and run the installer directly:
- Visit: https://www.iis.net/downloads/microsoft/url-rewrite
- Download "URL Rewrite Module 2.1"
- Run the installer as Administrator
- Restart IIS when prompted

## Step 2: Prepare Python Environment

Open PowerShell as Administrator and navigate to your BESTSTORE folder:

```powershell
cd "C:\Users\BRAMWEL\OneDrive\Desktop\BESTSTORE"

# Activate virtual environment
venv\Scripts\Activate.ps1

# Install Gunicorn (application server)
pip install gunicorn

# Verify installation
gunicorn --version
```

## Step 3: Configure Django Settings

Verify your `beststore/settings.py` has:

```python
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'localhost:20306',
    '127.0.0.1:20306',
]

# For production, set DEBUG = False
DEBUG = True
```

## Step 4: Prepare Static Files

While still in the activated venv:

```powershell
# Collect all static files
python manage.py collectstatic --noinput

# Run migrations if needed
python manage.py migrate
```

## Step 5: Test Django Application Locally

Before configuring IIS, test that Django works:

```powershell
# Start Django development server
python manage.py runserver 0.0.0.0:8000
```

Then open: `http://localhost:8000` in your browser

If it works, press Ctrl+C to stop, then continue to Step 6.

## Step 6: Test with Gunicorn

Test with Gunicorn (what IIS will use):

```powershell
# Still in activated venv
gunicorn --bind 127.0.0.1:8000 beststore.wsgi:application

# Should see output like:
# [2026-03-21 14:30:00 +0000] [12345] [INFO] Starting gunicorn 21.0.0
# [2026-03-21 14:30:00 +0000] [12345] [INFO] Listening at: http://127.0.0.1:8000
```

If successful, press Ctrl+C to stop.

## Step 7: Set Up IIS Website (If Not Already Done)

Run the setup PowerShell script as Administrator:

```powershell
cd "C:\Users\BRAMWEL\OneDrive\Desktop\BESTSTORE"
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\setup_iis.ps1
```

This creates:
- Application Pool: "BestStorePool"
- Website: "BestStore" on port 20306

## Step 8: Automate Django Server Startup

We need the Gunicorn server running while IIS is serving requests. Create a Windows Service or use a startup script.

### Option A: Using a Simple Batch File (Quickest)

Create `start_gunicorn.bat`:

```batch
@echo off
cd C:\Users\BRAMWEL\OneDrive\Desktop\BESTSTORE
call venv\Scripts\activate.bat
gunicorn --bind 127.0.0.1:8000 ^
         --workers 4 ^
         --worker-class sync ^
         --timeout 120 ^
         --log-level info ^
         beststore.wsgi:application
pause
```

Run this manually when you want to start the server, or set it as a Windows scheduled task to run on startup.

### Option B: Using Python Script Wrapper

Use the provided `start_django.ps1` script:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\start_django.ps1
```

### Option C: Windows Service (Advanced)

For production, install Gunicorn as a Windows service using NSSM:

```powershell
# Download NSSM from: https://nssm.cc/download
# Extract and:

cd C:\path\to\nssm\win64
.\nssm install BestStoreGunicorn `
  "C:\Users\BRAMWEL\OneDrive\Desktop\BESTSTORE\venv\Scripts\python.exe" `
  "-m gunicorn --bind 127.0.0.1:8000 --workers 4 beststore.wsgi:application"

.\nssm set BestStoreGunicorn AppDirectory "C:\Users\BRAMWEL\OneDrive\Desktop\BESTSTORE"

# Start the service
.\nssm start BestStoreGunicorn
```

## Step 9: Test IIS Access

1. **Ensure Gunicorn is running**: Start the `start_django.ps1` or batch file in a PowerShell window (keep it running)

2. **Open browser and test**: Go to `http://localhost:20306`

3. **You should see**: Your BestStore home page

4. **Test admin panel**: Go to `http://localhost:20306/admin/`

## Step 10: Troubleshooting

### Error: "Connection refused" or "502 Bad Gateway"

**Cause**: Gunicorn server isn't running

**Solution**:
```powershell
cd "C:\Users\BRAMWEL\OneDrive\Desktop\BESTSTORE"
venv\Scripts\Activate.ps1
gunicorn --bind 127.0.0.1:8000 beststore.wsgi:application
```

### Error: "Invalid web.config"

**Solution**:
- Ensure URL Rewrite module is installed
- Check web.config XML syntax is valid
- View IIS logs: `C:\inetpub\logs\LogFiles\`

### Static files not loading (images/CSS broken)

**Solution**:
1. Run: `python manage.py collectstatic --noinput`
2. Check folder: `C:\Users\BRAMWEL\OneDrive\Desktop\BESTSTORE\staticfiles\` has files
3. Verify web.config has static file rules

### Slow performance

**Cause**: Single worker process

**Solution**: Increase workers in Gunicorn:
```powershell
gunicorn --workers 8 --bind 127.0.0.1:8000 beststore.wsgi:application
```

## Architecture Diagram

```
┌─────────────────────────────────────┐
│    Web Browser at localhost:20306   │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│  IIS Server on Port 20306           │
│  (web.config with URL Rewrite)      │
│  - Serves static files directly     │
│  - Proxies dynamic requests         │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│  Gunicorn App Server (8000)         │
│  - Runs Django WSGI application     │
│  - 4 worker processes               │
│  - Memory: ~200MB per worker        │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│  Django Application                 │
│  - URL routing                      │
│  - Business logic                   │
│  - ORM/Database queries             │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│  SQLite Database (db.sqlite3)       │
│  - Product data                     │
│  - User accounts                    │
│  - Order information                │
└─────────────────────────────────────┘
```

## Next Steps

1. **Install URL Rewrite Module** (if not already done)
2. **Start Gunicorn server** using one of the methods above
3. **Reset IIS**: `iisreset` (in PowerShell as Admin)
4. **Test**: Open browser to `http://localhost:20306`
5. **Monitor**: Watch Gunicorn output for errors

## For Production Deployment

When deploying to production:

```python
# In settings.py:
DEBUG = False
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'your-domain.com']

# Enable security headers:
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# Use a real database (PostgreSQL):
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'beststore_db',
        'USER': 'postgres',
        'PASSWORD': 'your-password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Files Modified/Created

- ✓ `web.config` - Updated with reverse proxy rules
- ✓ `beststore/settings.py` - Added localhost:20306 to ALLOWED_HOSTS
- ✓ `start_django.ps1` - Script to start Gunicorn server
- ✓ `setup_iis.ps1` - IIS configuration script
- ✓ `verify_iis_config.ps1` - Verification script

## Getting Help

If you encounter issues:

1. Check IIS logs: `C:\inetpub\logs\LogFiles\`
2. Check Gunicorn console output
3. Verify ports: `netstat -ano | findstr :8000` (Gunicorn) and `:20306` (IIS)
4. Test Django directly: `python manage.py runserver 0.0.0.0:8000`

---

**Last Updated**: 2026-03-21
**Configuration**: IIS on port 20306 → Gunicorn on localhost:8000
