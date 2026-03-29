# BestStore Deployment on IIS (Port 20306) - Setup Guide

## Overview

This guide will help you deploy your Django BestStore application on IIS on port 20306.

## Prerequisites

- Windows Server or Windows 10/11 with IIS installed
- Python 3.8+ installed
- Administrator access to manage IIS

## Step-by-Step Setup Instructions

### Step 1: Install Required IIS Components

1. Open **Control Panel** → **Programs** → **Programs and Features**
2. Click **Turn Windows features on or off**
3. Ensure these are checked:
   - **Internet Information Services**
   - **Web Management Tools**
   - **CGI** (under Application Development Features)
4. Click **OK** and restart if prompted

### Step 2: Install Python Dependencies

1. Open PowerShell as Administrator
2. Navigate to the project directory:
   ```powershell
   cd "C:\Users\BRAMWEL\OneDrive\Desktop\BESTSTORE"
   ```

3. Activate the virtual environment:
   ```powershell
   venv\Scripts\Activate.ps1
   ```

4. Install required packages:
   ```powershell
   pip install -r requirements.txt
   ```

5. Install WinDjango FastCGI handler (for IIS FastCGI support):
   ```powershell
   pip install wfastcgi
   ```

6. Enable FastCGI in Python:
   ```powershell
   python -m wfastcgi
   ```

### Step 3: Prepare Django Application

Still in the venv-activated PowerShell:

1. Run migrations:
   ```powershell
   python manage.py migrate
   ```

2. Collect static files:
   ```powershell
   python manage.py collectstatic --noinput
   ```

3. Note the location of your Python executable (you'll need it):
   ```powershell
   python -c "import sys; print(sys.executable)"
   # Should output: C:\Users\BRAMWEL\OneDrive\Desktop\BESTSTORE\venv\Scripts\python.exe
   ```

### Step 4: Configure IIS

Run the provided PowerShell script as Administrator:

1. Open PowerShell as Administrator
2. Run:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   cd "C:\Users\BRAMWEL\OneDrive\Desktop\BESTSTORE"
   .\setup_iis.ps1
   ```

3. The script will:
   - Create an Application Pool named "BestStorePool"
   - Create a website named "BestStore" on port 20306
   - Configure FastCGI handlers
   - Set appropriate NTFS permissions
   - Reset IIS

### Step 5: Verify Configuration

#### Check Website Status in IIS Manager

1. Open **IIS Manager** (press Windows key, type "IIS", select "Internet Information Services (IIS) Manager")
2. Expand your server name in the left panel
3. Click on **Sites** → Verify "BestStore" is listed and shows a green checkmark
4. Click on **Application Pools** → Verify "BestStorePool" is listed and status shows "Started"

#### Access the Application

1. Open a web browser
2. Navigate to: `http://localhost:20306`
3. You should see your BestStore application home page

### Step 6: Troubleshooting

#### Application Returns 500 Error

1. Check IIS logs:
   ```powershell
   Get-ChildItem "C:\inetpub\logs\LogFiles\" -Recurse -File -Name
   ```

2. Check Python FastCGI logs:
   - Look in `C:\inetpub\logs\LogFiles\W3SVC[ID]\` for error details

3. Verify ALLOWED_HOSTS in settings.py includes:
   - `localhost`
   - `127.0.0.1`
   - `localhost:20306`
   - `127.0.0.1:20306`

#### Application Pool Keeps Stopping

1. Open IIS Manager
2. Right-click "BestStorePool" → **Advanced Settings**
3. Set:
   - **Recycling** → **Disable Recycling**: Set to False (allow recycling)
   - **Process Model** → **Idle Time-out**: Set to 0 or a large value

#### Static Files Not Loading

1. Verify static files were collected:
   ```powershell
   dir "C:\Users\BRAMWEL\OneDrive\Desktop\BESTSTORE\staticfiles\"
   ```

2. In IIS Manager, right-click the BestStore site → **Edit Web Config**
3. Verify the URL rewrite rules include exceptions for `/static/` and `/media/`

### Step 7: Performance Optimization (Optional)

#### Enable Compression

1. In IIS Manager, select your server
2. Double-click **Compression** under IIS section
3. Enable both "Static" and "Dynamic" compression for applicable MIME types

#### Configure Application Pool Recycling

1. Right-click **BestStorePool** → **Recycling Settings**
2. Set:
   - **Regular time interval (minutes)**: 360 (6 hours) or your preference
   - **Virtual Memory (MB)**: 512 or based on your server capacity

### Step 8: Enable HTTPS (Recommended for Production)

For production, you should enable HTTPS:

1. Obtain an SSL certificate
2. In IIS Manager, right-click "BestStore" site → **Edit Bindings**
3. Add binding:
   - Type: HTTPS
   - Port: 20443 (or your choice)
   - SSL Certificate: Select your certificate
4. Update ALLOWED_HOSTS in settings.py to include the SSL host

### Step 9: Production Settings

For production deployment, update your settings.py:

```python
DEBUG = False
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'localhost:20306', '127.0.0.1:20306', 'yourdomain.com']

# Add HTTPS redirect
SECURE_SSL_REDIRECT = True  # Only when HTTPS is set up
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
```

## Testing the Deployment

### Test Application Functionality

1. Navigate to `http://localhost:20306`
2. Test main features:
   - Admin panel: `http://localhost:20306/admin/`
   - Browse products (if applicable)
   - Test any other major functionality

### Check Application Health

Create a health check endpoint by creating a view in your main app:

```python
# In beststore/views.py
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({'status': 'ok', 'database': 'connected'})

# In beststore/urls.py
path('health/', health_check, name='health-check'),
```

Then test: `http://localhost:20306/health/`

## Common Issues and Solutions

### Issue: "Python path not found"
**Solution**: Ensure the Python path in web.config matches your venv location

### Issue: "Database locked"
**Solution**: SQLite doesn't work well with IIS. Configure PostgreSQL or MySQL for production

### Issue: "Media files not uploading"
**Solution**: Check folder permissions for the mediafiles directory

### Issue: "Admin styles not loading"
**Solution**: Run `python manage.py collectstatic --noinput` and verify web.config URL rewrite rules

## Next Steps

1. **Monitor logs**: Regularly check IIS logs for errors
2. **Set up backups**: Backup your database and media files
3. **Enable logging**: Configure Django logging in settings.py
4. **Setup monitoring**: Use Windows Event Viewer or third-party monitoring tools
5. **Plan scaling**: If load increases, consider load balancing

## Support Resources

- [Django IIS Deployment Guide](https://docs.djangoproject.com/en/stable/)
- [IIS FastCGI Documentation](https://www.iis.net/downloads/microsoft/fastcgi-for-iis)
- [Python wfastcgi Documentation](https://pypi.org/project/wfastcgi/)

## Rollback Instructions

If you need to remove the IIS site:

```powershell
# As Administrator
Remove-WebSite -Name "BestStore"
Remove-WebAppPool -Name "BestStorePool"
iisreset
```

---

**Setup Date**: 2026-03-21
**Application**: BestStore Django Application
**Port**: 20306
