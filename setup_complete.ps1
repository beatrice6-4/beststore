# Comprehensive Setup and Diagnostic Script for BestStore on IIS Port 20306
# Run as Administrator

param (
    [string]$Action = "setup"
)

$AppPath = "C:\Users\BRAMWEL\OneDrive\Desktop\BESTSTORE"
$VenvPath = "$AppPath\venv"
$Port = 20306
$AppPort = 8000

Write-Host "==========================================" -ForegroundColor Green
Write-Host "BestStore IIS Setup & Diagnosis Tool"
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

function Check-Admin {
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
    if (-not $isAdmin) {
        Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
        exit 1
    }
}

function Diagnose-System {
    Write-Host "System Diagnostic Report" -ForegroundColor Yellow
    Write-Host "=========================" -ForegroundColor Yellow
    Write-Host ""

    Write-Host "1. Python Environment" -ForegroundColor Cyan
    if (Test-Path "$VenvPath\Scripts\python.exe") {
        $pythonVersion = & "$VenvPath\Scripts\python.exe" --version 2>&1
        Write-Host "   ✓ Python: $pythonVersion" -ForegroundColor Green
        Write-Host "     Path: $VenvPath\Scripts\python.exe" -ForegroundColor Gray
    } else {
        Write-Host "   ✗ Python venv not found at $VenvPath" -ForegroundColor Red
    }

    Write-Host ""
    Write-Host "2. Required Files" -ForegroundColor Cyan
    $files = @(
        "manage.py",
        "beststore\settings.py",
        "beststore\wsgi.py",
        "web.config",
        "db.sqlite3",
        "requirements.txt"
    )
    
    foreach ($file in $files) {
        $fullPath = Join-Path $AppPath $file
        if (Test-Path $fullPath) {
            Write-Host "   ✓ $file" -ForegroundColor Green
        } else {
            Write-Host "   ✗ $file (MISSING)" -ForegroundColor Yellow
        }
    }

    Write-Host ""
    Write-Host "3. Django Packages" -ForegroundColor Cyan
    & "$VenvPath\Scripts\pip.exe" show gunicorn django | Out-Null
    if ($?) {
        Write-Host "   ✓ Django and Gunicorn installed" -ForegroundColor Green
        $gunicornVer = & "$VenvPath\Scripts\pip.exe" show gunicorn | Select-String "Version:" | ForEach-Object { $_ -replace "Version: ", "" }
        Write-Host "     Gunicorn version: $gunicornVer" -ForegroundColor Gray
    } else {
        Write-Host "   ✗ Missing Django or Gunicorn" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "4. IIS Configuration" -ForegroundColor Cyan
    
    # Check IIS module
    Import-Module WebAdministration -ErrorAction SilentlyContinue
    
    # Check for site
    $site = Get-IISSite -Name "BestStore" -ErrorAction SilentlyContinue
    if ($site) {
        Write-Host "   ✓ IIS Site 'BestStore' exists" -ForegroundColor Green
        $siteState = Get-WebSite -Name "BestStore" | Select-Object -ExpandProperty State
        Write-Host "     Status: $siteState" -ForegroundColor Gray
    } else {
        Write-Host "   ✗ IIS Site 'BestStore' not found" -ForegroundColor Yellow
    }

    # Check for app pool
    $appPool = Get-IISAppPool -Name "BestStorePool" -ErrorAction SilentlyContinue
    if ($appPool) {
        Write-Host "   ✓ IIS App Pool 'BestStorePool' exists" -ForegroundColor Green
        $poolState = Get-IISAppPool -Name "BestStorePool" | Select-Object -ExpandProperty State
        Write-Host "     Status: $poolState" -ForegroundColor Gray
    } else {
        Write-Host "   ✗ IIS App Pool 'BestStorePool' not found" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "5. Port Status" -ForegroundColor Cyan
    
    $port20306 = netstat -ano 2>/dev/null | Select-String ":$Port " | Select-String "LISTENING"
    $port8000 = netstat -ano 2>/dev/null | Select-String ":$AppPort " | Select-String "LISTENING"
    
    if ($port20306) {
        Write-Host "   ✓ Port $Port is in use (IIS listening)" -ForegroundColor Green
    } else {
        Write-Host "   ⚠ Port $Port not in use - IIS may not be listening" -ForegroundColor Yellow
    }
    
    if ($port8000) {
        Write-Host "   ✓ Port $AppPort is in use (Django app running)" -ForegroundColor Green
    } else {
        Write-Host "   ⚠ Port $AppPort not in use - Django app not running" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "6. URL Rewrite Module" -ForegroundColor Cyan
    
    try {
        $rewriteModule = Get-WebServer | Get-WebGlobalModule | Where-Object { $_.Name -eq "RewriteModule" }
        if ($rewriteModule) {
            Write-Host "   ✓ URL Rewrite module installed" -ForegroundColor Green
        } else {
            Write-Host "   ⚠ URL Rewrite module NOT installed" -ForegroundColor Yellow
            Write-Host "     Download: https://www.iis.net/downloads/microsoft/url-rewrite" -ForegroundColor Gray
        }
    } catch {
        Write-Host "   ⚠ Could not verify URL Rewrite module" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "7. web.config Status" -ForegroundColor Cyan
    
    $webConfigPath = "$AppPath\web.config"
    if (Test-Path $webConfigPath) {
        Write-Host "   ✓ web.config exists" -ForegroundColor Green
        
        try {
            [xml]$webConfig = Get-Content $webConfigPath
            Write-Host "   ✓ web.config is valid XML" -ForegroundColor Green
            
            # Check for rewrite rules
            if ($webConfig.configuration.'system.webServer'.rewrite.rules) {
                Write-Host "   ✓ Contains URL rewrite rules" -ForegroundColor Green
            } else {
                Write-Host "   ⚠ No rewrite rules found in web.config" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "   ✗ web.config has XML errors:" -ForegroundColor Red
            Write-Host "     $_" -ForegroundColor Red
        }
    } else {
        Write-Host "   ✗ web.config not found" -ForegroundColor Red
    }

    Write-Host ""
    Write-Host "8. Static Files" -ForegroundColor Cyan
    
    $staticPath = "$AppPath\staticfiles"
    if (Test-Path $staticPath) {
        $count = (Get-ChildItem $staticPath -Recurse -File 2>/dev/null | Measure-Object).Count
        Write-Host "   ✓ Staticfiles directory exists ($count files)" -ForegroundColor Green
    } else {
        Write-Host "   ⚠ Staticfiles directory not found" -ForegroundColor Yellow
        Write-Host "     Run: python manage.py collectstatic --noinput" -ForegroundColor Gray
    }

    Write-Host ""
    Write-Host "Diagnosis Complete" -ForegroundColor Green
}

function Install-GunicornService {
    Write-Host "Installing Gunicorn as Windows Service..." -ForegroundColor Yellow
    Write-Host ""
    
    # Check for NSSM
    $nssmPath = "C:\nssm\win64\nssm.exe"
    if (-not (Test-Path $nssmPath)) {
        Write-Host "NSSM not found. Please:"
        Write-Host "1. Download from: https://nssm.cc/download" -ForegroundColor Yellow
        Write-Host "2. Extract to: C:\nssm" -ForegroundColor Yellow
        Write-Host "3. Run this script again" -ForegroundColor Yellow
        return
    }

    Write-Host "Found NSSM at: $nssmPath" -ForegroundColor Green
    
    $pythonExe = "$VenvPath\Scripts\python.exe"
    
    # Install service
    & $nssmPath install BestStoreApp $pythonExe "-m gunicorn --bind 127.0.0.1:8000 --workers 4 beststore.wsgi:application"
    & $nssmPath set BestStoreApp AppDirectory $AppPath
    
    Write-Host "Service installed. Starting..." -ForegroundColor Green
    & $nssmPath start BestStoreApp
    
    Start-Sleep 2
    
    $status = & $nssmPath status BestStoreApp
    Write-Host "Service status: $status" -ForegroundColor Cyan
}

function Quick-Setup {
    Write-Host "Quick Setup Mode" -ForegroundColor Yellow
    Check-Admin
    
    Write-Host ""
    Write-Host "Steps:" -ForegroundColor Cyan
    Write-Host "1. Checking Python environment..." -ForegroundColor White
    
    if (-not (Test-Path "$VenvPath\Scripts\python.exe")) {
        Write-Host "   ERROR: Virtual environment not found" -ForegroundColor Red
        return
    }
    Write-Host "   ✓ Found" -ForegroundColor Green
    
    Write-Host "2. Installing Gunicorn..." -ForegroundColor White
    & "$VenvPath\Scripts\pip.exe" install gunicorn -q
    Write-Host "   ✓ Done" -ForegroundColor Green
    
    Write-Host "3. Collecting static files..." -ForegroundColor White
    Push-Location $AppPath
    & "$VenvPath\Scripts\python.exe" manage.py collectstatic --noinput
    Write-Host "   ✓ Done" -ForegroundColor Green
    
    Write-Host "4. Running migrations..." -ForegroundColor White
    & "$VenvPath\Scripts\python.exe" manage.py migrate
    Write-Host "   ✓ Done" -ForegroundColor Green
    
    Pop-Location
    
    Write-Host ""
    Write-Host "Setup Complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next: Open new PowerShell AND run:" -ForegroundColor Yellow
    Write-Host "  $AppPath\start_django.ps1" -ForegroundColor Cyan
}

# Main logic
Check-Admin

if ($Action -eq "diagnose" -or $Action -eq "diag") {
    Diagnose-System
} elseif ($Action -eq "install-service") {
    Install-GunicornService
} else {
    Diagnose-System
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor Yellow
    Write-Host "  .\setup_complete.ps1 diagnose     - Run diagnostic report" -ForegroundColor Cyan
    Write-Host "  .\setup_complete.ps1 install-service - Install as Windows Service (requires NSSM)" -ForegroundColor Cyan
}
