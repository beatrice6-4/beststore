# PowerShell Script to Configure IIS for Django BestStore Application on Port 20306
# Run this script as Administrator in PowerShell

# Configuration variables
$AppName = "BestStore"
$AppPoolName = "BestStorePool"
$SiteName = "BestStore"
$Port = 20306
$AppPath = "C:\Users\BRAMWEL\OneDrive\Desktop\BESTSTORE"
$PhysicalPath = $AppPath
$HostHeader = "localhost:$Port"

Write-Host "========================================" -ForegroundColor Green
Write-Host "Django BestStore IIS Configuration"
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    exit 1
}

# Enable IIS Features if needed
Write-Host "1. Checking IIS Features..." -ForegroundColor Yellow
$features = @(
    "IIS-WebServer",
    "IIS-WebServerRole",
    "IIS-WebServerManagementTools",
    "IIS-CGI",
    "IIS-RequestFiltering",
    "IIS-URLRewrite"
)

foreach ($feature in $features) {
    $state = Get-WindowsOptionalFeature -FeatureName $feature -Online -ErrorAction SilentlyContinue
    if ($state -and $state.State -ne "Enabled") {
        Write-Host "  Enabling feature: $feature" -ForegroundColor Cyan
        Enable-WindowsOptionalFeature -FeatureName $feature -Online -NoRestart -ErrorAction SilentlyContinue
    }
}

# Import IIS module
Import-Module WebAdministration -ErrorAction SilentlyContinue
if (-not (Get-Module WebAdministration)) {
    Write-Host "ERROR: Could not load WebAdministration module" -ForegroundColor Red
    exit 1
}

# Create App Pool if it doesn't exist
Write-Host ""
Write-Host "2. Creating/Updating Application Pool: $AppPoolName" -ForegroundColor Yellow
$appPool = Get-IISAppPool -Name $AppPoolName -ErrorAction SilentlyContinue

if ($appPool) {
    Write-Host "  App Pool exists, updating configuration..." -ForegroundColor Cyan
    Stop-WebAppPool -Name $AppPoolName -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
} else {
    Write-Host "  Creating new App Pool..." -ForegroundColor Cyan
    New-WebAppPool -Name $AppPoolName
    $appPool = Get-IISAppPool -Name $AppPoolName
}

# Configure App Pool
$appPoolConfig = $appPool.processModel
$appPoolConfig.identityType = "ApplicationPoolIdentity"
$appPool | Set-ItemProperty -Name "processModel.identityType" -Value "ApplicationPoolIdentity"
$appPool | Set-ItemProperty -Name "processModel.loadUserProfile" -Value $true
$appPool.Recycle.periodicRestart.time = 0  # Disable periodic restart

# Set App Pool to start automatically
$appPool | Set-ItemProperty -Name "autoStart" -Value $true

# Save changes
$appPool | Set-Item

Write-Host "  App Pool configured successfully" -ForegroundColor Green

# Remove existing site/app if it exists
Write-Host ""
Write-Host "3. Checking for existing Website/Application..." -ForegroundColor Yellow
$site = Get-IISSite -Name $SiteName -ErrorAction SilentlyContinue

if ($site) {
    Write-Host "  Found existing site, removing..." -ForegroundColor Cyan
    
    # Stop the site if it's running
    $siteState = Get-WebSite -Name $SiteName | Select-Object -ExpandProperty State
    if ($siteState -eq "Started") {
        Stop-WebSite -Name $SiteName -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }
    
    # Remove the site
    Remove-WebSite -Name $SiteName -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
}

# Create new website
Write-Host "4. Creating Website: $SiteName on port $Port" -ForegroundColor Yellow
New-WebSite `
    -Name $SiteName `
    -ApplicationPool $AppPoolName `
    -PhysicalPath $PhysicalPath `
    -Port $Port `
    -HostHeader $HostHeader `
    -ErrorAction Stop | Out-Null

Write-Host "  Website '$SiteName' created successfully on http://localhost:$Port" -ForegroundColor Green

# Configure Application
Write-Host ""
Write-Host "5. Configuring Application Settings..." -ForegroundColor Yellow
$site = Get-IISSite -Name $SiteName
$app = $site.Applications[0]

# Set application pool
$app.ApplicationPool = $AppPoolName

Write-Host "  Application pool assigned: $AppPoolName" -ForegroundColor Green

# Set NTFS Permissions
Write-Host ""
Write-Host "6. Setting NTFS Permissions..." -ForegroundColor Yellow
try {
    $acl = Get-Acl $PhysicalPath
    $iisAppPoolSid = New-Object System.Security.Principal.NTAccount("IIS AppPool\$AppPoolName")
    
    # Check if permission already exists
    $ruleExists = $acl.Access | Where-Object { $_.IdentityReference -eq $iisAppPoolSid }
    
    if (-not $ruleExists) {
        $rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
            $iisAppPoolSid,
            "Modify",
            "ContainerInherit, ObjectInherit",
            "None",
            "Allow"
        )
        $acl.AddAccessRule($rule)
        Set-Acl $PhysicalPath $acl
        Write-Host "  Permissions set for IIS App Pool" -ForegroundColor Green
    } else {
        Write-Host "  Permissions already configured" -ForegroundColor Green
    }
} catch {
    Write-Host "  Warning: Could not set permissions automatically. Please set manually." -ForegroundColor Yellow
    Write-Host "  Run as Admin: icacls '$PhysicalPath' /grant 'IIS AppPool\$AppPoolName:(OI)(CI)M'" -ForegroundColor Yellow
}

# Reset IIS
Write-Host ""
Write-Host "7. Resetting IIS..." -ForegroundColor Yellow
try {
    iisreset /noforce | Out-Null
    Write-Host "  IIS reset successfully" -ForegroundColor Green
} catch {
    Write-Host "  Warning: Could not reset IIS automatically" -ForegroundColor Yellow
}

# Start the website
Write-Host ""
Write-Host "8. Starting Website..." -ForegroundColor Yellow
Start-WebSite -Name $SiteName -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

$siteState = Get-WebSite -Name $SiteName | Select-Object -ExpandProperty State
if ($siteState -eq "Started") {
    Write-Host "  Website started successfully" -ForegroundColor Green
} else {
    Write-Host "  Warning: Website may not have started" -ForegroundColor Yellow
}

# Display final information
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Configuration Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access your application at:" -ForegroundColor Yellow
Write-Host "  http://localhost:$Port" -ForegroundColor Cyan
Write-Host ""
Write-Host "Application Details:" -ForegroundColor Yellow
Write-Host "  Site Name: $SiteName" -ForegroundColor Cyan
Write-Host "  App Pool: $AppPoolName" -ForegroundColor Cyan
Write-Host "  Physical Path: $PhysicalPath" -ForegroundColor Cyan
Write-Host "  Port: $Port" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Ensure virtual environment is activated" -ForegroundColor White
Write-Host "  2. Install Python dependencies: pip install -r requirements.txt" -ForegroundColor White
Write-Host "  3. Collect static files: python manage.py collectstatic" -ForegroundColor White
Write-Host "  4. Check IIS Event Viewer for any errors" -ForegroundColor White
Write-Host ""
Write-Host "To view IIS logs:" -ForegroundColor Yellow
Write-Host "  C:\inetpub\logs\LogFiles\W3SVC$((Get-WebSite -Name $SiteName).id)\" -ForegroundColor Cyan
Write-Host ""

Write-Host "Press any key to continue..." -ForegroundColor Gray
[Console]::ReadKey() | Out-Null
