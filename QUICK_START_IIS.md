# Quick Start: Get BestStore Running on IIS Port 20306 (Next 5 Minutes)

## Prerequisites Check

- Windows PowerShell open as Administrator
- In folder: `C:\Users\BRAMWEL\OneDrive\Desktop\BESTSTORE`

## Quick Steps

### Step 1: Open PowerShell as Administrator

Click Windows → type `PowerShell` → Right-click → `Run as Administrator`

### Step 2: Navigate to Project

```powershell
cd "C:\Users\BRAMWEL\OneDrive\Desktop\BESTSTORE"
```

### Step 3: Test IIS is Working

```powershell
iisreset
```

Wait for the message: "Internet services successfully restarted"

### Step 4: Activate Virtual Environment

```powershell
venv\Scripts\Activate.ps1
```

You should see `(venv)` at the start of the prompt.

### Step 5: Install Gunicorn (if not already installed)

```powershell
pip install gunicorn
```

### Step 6: Prepare Django

```powershell
# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate
```

### Step 7: Start Django Server

```powershell
gunicorn --bind 127.0.0.1:8000 --workers 4 beststore.wsgi:application
```

**Keep this PowerShell window open!** You should see output like:
```
[2026-03-21 14:30:00 +0000] [12345] [INFO] Starting gunicorn 21.0.0
[2026-03-21 14:30:00 +0000] [12345] [INFO] Listening at: http://127.0.0.1:8000
```

### Step 8: Open Second PowerShell Window (as Administrator)

Open a new PowerShell window again (don't close the Gunicorn one!)

```powershell
cd "C:\Users\BRAMWEL\OneDrive\Desktop\BESTSTORE"
iisreset
```

### Step 9: Test It!

Open your web browser and go to:

**`http://localhost:20306`**

You should see your BestStore application!

## What if it doesn't work?

### IIS Shows Error

**Check**: Is the URL Rewrite module installed?

Install it:
1. Download: https://www.iis.net/downloads/microsoft/url-rewrite
2. Run installer
3. Restart IIS: `iisreset`
4. Try again

### Still Getting 500.19 Error

The web.config has invalid XML. Try the simplest possible version:

```powershell
# Backup current:
Copy-Item web.config web.config.backup

# Create new simple one:
@'
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <rewrite>
      <rules>
        <rule name="Static Files" stopProcessing="true">
          <match url="^(static|media)/" />
          <action type="None" />
        </rule>
        <rule name="DjangoProxy" stopProcessing="true">
          <match url=".*" />
          <action type="Rewrite" url="http://localhost:8000/{R:0}" />
        </rule>
      </rules>
    </rewrite>
    <staticContent>
      <mimeMap fileExtension=".json" mimeType="application/json" />
      <mimeMap fileExtension=".woff2" mimeType="application/font-woff2" />
    </staticContent>
  </system.webServer>
</configuration>
'@ | Out-File -Encoding UTF8 web.config

iisreset
```

### Can't find localhost:8000

The Gunicorn server isn't running or crashed.

**Check the PowerShell window where you started Gunicorn** - there should be error messages.

If you see issues like:
- "ModuleNotFoundError" → Run: `pip install -r requirements.txt`
- "Database error" → Run: `python manage.py migrate`
- "Static files error" → Run: `python manage.py collectstatic --noinput`

### Connection Refused on Port 20306

IIS isn't running or the binding isn't correct.

```powershell
# Check IIS status
Get-IISSite -Name "BestStore"

# Should show: Name, Status, Bindings

# If not found, run setup:
.\setup_iis.ps1
```

## Keep It Running (Windows Startup)

To automatically start Gunicorn when Windows starts:

### Create a batch file `start_beststore.bat`:

```batch
@echo off
cd /d "C:\Users\BRAMWEL\OneDrive\Desktop\BESTSTORE"
call venv\Scripts\activate.bat
gunicorn --bind 127.0.0.1:8000 --workers 4 beststore.wsgi:application
pause
```

Save this file in the BESTSTORE folder.

### Then run at startup:

1. Create a shortcut to the batch file
2. Right-click shortcut → Properties → Advanced → Check "Run as administrator"
3. Copy to: `C:\Users\BRAMWEL\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup`

## Validation Checklist

- ✓ Python virtual environment activated
- ✓ Gunicorn installed: `pip show gunicorn`
- ✓ Static files collected: `dir staticfiles` (should show files)
- ✓ Database exists: `dir db.sqlite3`
- ✓ web.config is valid XML
- ✓ IIS URL Rewrite module installed
- ✓ Gunicorn running on localhost:8000
- ✓ IIS reset recently: `iisreset`
- ✓ Browser can reach: `http://localhost:20306`

## Access Your Application

Once working, you can access:

| Component | URL |
|-----------|-----|
| Home Page | http://localhost:20306/ |
| Admin Panel | http://localhost:20306/admin/ |
| API (if enabled) | http://localhost:20306/api/ |

## Default Admin Login

Before first login, create an admin user:

```powershell
# While Gunicorn is running, in a new PowerShell window:
python manage.py createsuperuser
```

Follow the prompts to create username/password.

Then login at: `http://localhost:20306/admin/`

## Next: Make It Permanent

Once you verify everything works, set up automatic startup:

1. Create the batch file (see above)
2. Test that batch file works
3. Schedule it to run on Windows startup
4. Or install as Windows service using NSSM

## Still Need Help?

Check the logs:
```powershell
# See Gunicorn errors in the PowerShell window
# See IIS errors:
Get-ChildItem "C:\inetpub\logs\LogFiles\W3SVC*\" -Recurse -Name | Select-Object -Last 5
```

Or review: `IIS_SETUP_FIXED.md` for detailed troubleshooting.

---

Keep the Gunicorn PowerShell window open while testing!
