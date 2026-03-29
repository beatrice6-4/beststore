# PowerShell Script to Verify IIS Configuration for BestStore
# Run this script to verify your IIS setup is correct on port 20306

$SiteName = "BestStore"
$AppPoolName = "BestStorePool"
$Port = 20306
$Url = "http://localhost:$Port"

Write-Host "==========================================" -ForegroundColor Green
Write-Host "BestStore IIS Configuration Verification"
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

# Check if running as Administrator (optional for read-only checks)
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "Note: Some checks require Administrator privileges" -ForegroundColor Yellow
}

# Import IIS module
Write-Host "1. Loading IIS Module..." -ForegroundColor Yellow
try {
    Import-Module WebAdministration -ErrorAction Stop
    Write-Host "   ✓ IIS Module loaded successfully" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Failed to load IIS Module" -ForegroundColor Red
    Write-Host "   Please ensure IIS is installed" -ForegroundColor Red
    exit 1
}

# Check Application Pool
Write-Host ""
Write-Host "2. Checking Application Pool: $AppPoolName" -ForegroundColor Yellow
$appPool = Get-IISAppPool -Name $AppPoolName -ErrorAction SilentlyContinue
if ($appPool) {
    Write-Host "   ✓ Application Pool found" -ForegroundColor Green
    $state = Get-IISAppPool -Name $AppPoolName | Select-Object -ExpandProperty State
    Write-Host "     Status: $state" -ForegroundColor Cyan
    if ($state -eq "Started") {
        Write-Host "   ✓ Application Pool is running" -ForegroundColor Green
    } else {
        Write-Host "   ⚠ Application Pool is NOT running" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ✗ Application Pool NOT found" -ForegroundColor Red
    Write-Host "   Run: .\setup_iis.ps1" -ForegroundColor Yellow
}

# Check Website
Write-Host ""
Write-Host "3. Checking Website: $SiteName" -ForegroundColor Yellow
$site = Get-IISSite -Name $SiteName -ErrorAction SilentlyContinue
if ($site) {
    Write-Host "   ✓ Website found" -ForegroundColor Green
    $siteState = Get-WebSite -Name $SiteName | Select-Object -ExpandProperty State
    Write-Host "     Status: $siteState" -ForegroundColor Cyan
    if ($siteState -eq "Started") {
        Write-Host "   ✓ Website is running" -ForegroundColor Green
    } else {
        Write-Host "   ⚠ Website is NOT running" -ForegroundColor Yellow
    }
    
    # Check bindings
    Write-Host ""
    Write-Host "   Bindings:" -ForegroundColor Cyan
    $bindings = Get-IISSiteBinding -Name $SiteName
    foreach ($binding in $bindings) {
        if ($binding.bindingInformation -like "*$Port*") {
            Write-Host "     ✓ Port $Port binding found" -ForegroundColor Green
        }
    }
} else {
    Write-Host "   ✗ Website NOT found" -ForegroundColor Red
    Write-Host "   Run: .\setup_iis.ps1" -ForegroundColor Yellow
}

# Check Django Application Files
Write-Host ""
Write-Host "4. Checking Django Application Files" -ForegroundColor Yellow
$appPath = "C:\Users\BRAMWEL\OneDrive\Desktop\BESTSTORE"
$requiredFiles = @(
    "manage.py",
    "beststore\settings.py",
    "beststore\wsgi.py",
    "web.config",
    "requirements.txt"
)

foreach ($file in $requiredFiles) {
    $fullPath = Join-Path $appPath $file
    if (Test-Path $fullPath) {
        Write-Host "   ✓ $file exists" -ForegroundColor Green
    } else {
        Write-Host "   ✗ $file NOT found" -ForegroundColor Red
    }
}

# Check Virtual Environment
Write-Host ""
Write-Host "5. Checking Python Virtual Environment" -ForegroundColor Yellow
$venvPath = "$appPath\venv"
if (Test-Path $venvPath) {
    Write-Host "   ✓ Virtual environment found" -ForegroundColor Green
    
    $pythonExe = "$venvPath\Scripts\python.exe"
    if (Test-Path $pythonExe) {
        Write-Host "   ✓ Python executable found" -ForegroundColor Green
        
        $pythonVersion = & $pythonExe --version 2>&1
        Write-Host "     $pythonVersion" -ForegroundColor Cyan
    } else {
        Write-Host "   ✗ Python executable NOT found" -ForegroundColor Red
    }
} else {
    Write-Host "   ✗ Virtual environment NOT found" -ForegroundColor Red
    Write-Host "   Please create and activate venv first" -ForegroundColor Yellow
}

# Check Static Files
Write-Host ""
Write-Host "6. Checking Static Files" -ForegroundColor Yellow
$staticPath = "$appPath\staticfiles"
if (Test-Path $staticPath) {
    $staticCount = (Get-ChildItem $staticPath -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count
    if ($staticCount -gt 0) {
        Write-Host "   ✓ Static files collected ($staticCount files)" -ForegroundColor Green
    } else {
        Write-Host "   ⚠ No static files found" -ForegroundColor Yellow
        Write-Host "     Run: python manage.py collectstatic --noinput" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ⚠ Staticfiles directory not created yet" -ForegroundColor Yellow
    Write-Host "     Run: python manage.py collectstatic --noinput" -ForegroundColor Yellow
}

# Check Database
Write-Host ""
Write-Host "7. Checking Database" -ForegroundColor Yellow
$dbPath = "$appPath\db.sqlite3"
if (Test-Path $dbPath) {
    Write-Host "   ✓ SQLite database found" -ForegroundColor Green
    $dbSize = (Get-Item $dbPath).Length
    $dbSizeMB = [math]::Round($dbSize / 1MB, 2)
    Write-Host "     Size: $($dbSizeMB) MB" -ForegroundColor Cyan
} else {
    Write-Host "   ⚠ Database not found - run migrations" -ForegroundColor Yellow
}

# Check Web.config
Write-Host ""
Write-Host "8. Checking web.config" -ForegroundColor Yellow
$webConfigPath = "$appPath\web.config"
if (Test-Path $webConfigPath) {
    Write-Host "   ✓ web.config found" -ForegroundColor Green
    
    [xml]$webConfig = Get-Content $webConfigPath
    if ($webConfig.configuration.'system.webServer'.handlers) {
        Write-Host "   ✓ Handlers configured" -ForegroundColor Green
    }
} else {
    Write-Host "   ✗ web.config NOT found" -ForegroundColor Red
}

# Test Network Connectivity
Write-Host ""
Write-Host "9. Testing Network Connectivity" -ForegroundColor Yellow
try {
    $testConnection = Test-Connection -ComputerName localhost -Count 1 -Quiet
    if ($testConnection) {
        Write-Host "   ✓ Localhost is accessible" -ForegroundColor Green
    } else {
        Write-Host "   ✗ Cannot reach localhost" -ForegroundColor Red
    }
} catch {
    Write-Host "   ⚠ Could not test connectivity" -ForegroundColor Yellow
}

# Check Log Files
Write-Host ""
Write-Host "10. Checking IIS Logs" -ForegroundColor Yellow
$logPath = "C:\inetpub\logs\LogFiles\"
if (Test-Path $logPath) {
    Write-Host "   ✓ Log directory found: $logPath" -ForegroundColor Green
    
    $logFiles = Get-ChildItem $logPath -Filter "*.log" -Recurse -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($logFiles) {
        Write-Host "   ✓ Log files present" -ForegroundColor Green
        Write-Host "     Latest: $($logFiles.FullName)" -ForegroundColor Cyan
    }
} else {
    Write-Host "   ✗ Log directory not found" -ForegroundColor Red
}

# Summary
Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Verification Summary" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Configuration Status:" -ForegroundColor Yellow
Write-Host "  Application URL: $Url" -ForegroundColor Cyan
Write-Host "  Site Name: $SiteName" -ForegroundColor Cyan
Write-Host "  App Pool: $AppPoolName" -ForegroundColor Cyan
Write-Host "  Port: $Port" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow

if (-not $site -or -not $appPool) {
    Write-Host "  1. Run .\setup_iis.ps1 as Administrator to configure IIS"
    Write-Host "  2. Ensure required IIS features are installed"
}

Write-Host "  1. Visit $Url in your browser"
Write-Host "  2. Check IIS logs if you encounter errors"
Write-Host "  3. Review IIS_SETUP_GUIDE.md for troubleshooting"
Write-Host ""
Write-Host "Common Troubleshooting:" -ForegroundColor Yellow
Write-Host "  - Error 500: Check Python dependencies with: pip list"
Write-Host "  - Error 404: Check Django URL configuration"
Write-Host "  - Error 403: Check NTFS permissions on the app folder"
Write-Host ""

Write-Host "Press any key to continue..." -ForegroundColor Gray
[Console]::ReadKey() | Out-Null
