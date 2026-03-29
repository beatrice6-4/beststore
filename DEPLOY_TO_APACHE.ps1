# BestStore Apache Deployment Script for Windows PowerShell
# This script automates the complete deployment process

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   BestStore Django - Apache Automated Deployment (Windows)  " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$ServerIP = "10.190.143.234"
$SSHUser = "ubuntu"
$LocalProjectPath = "C:\Users\BRAMWEL\OneDrive\Desktop\BESTSTORE"
$RemoteProjectPath = "/var/www/mamamaasaibakers"
$Domain = "mamamaasaibakers.com"

Write-Host "Your Deployment Configuration:" -ForegroundColor Yellow
Write-Host "  Server IP: $ServerIP" -ForegroundColor Gray
Write-Host "  SSH User: $SSHUser" -ForegroundColor Gray
Write-Host "  Local Project: $LocalProjectPath" -ForegroundColor Gray
Write-Host "  Remote Project: $RemoteProjectPath" -ForegroundColor Gray
Write-Host ""

# Step 1: Check if project directory exists
Write-Host "[Step 1/5] Checking local project directory..." -ForegroundColor Cyan
if (-not (Test-Path "$LocalProjectPath\apache")) {
    Write-Host "[ERROR] Project directory not found at $LocalProjectPath\apache" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Project directory found" -ForegroundColor Green
Write-Host ""

# Step 2: Check SSH connectivity
Write-Host "[Step 2/5] Testing SSH connection..." -ForegroundColor Cyan
Write-Host "Please note: You'll need to authenticate with your server credentials" -ForegroundColor Yellow

try {
    # Test SSH connection by running a simple command
    $sshTest = ssh -o ConnectTimeout=5 "$SSHUser@$ServerIP" "whoami" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] SSH connection successful" -ForegroundColor Green
        Write-Host "  Connected as: $sshTest" -ForegroundColor Gray
    } else {
        Write-Host "[ERROR] SSH connection failed" -ForegroundColor Red
        Write-Host "Please verify:" -ForegroundColor Yellow
        Write-Host "  1. Server IP is correct: $ServerIP" -ForegroundColor Gray
        Write-Host "  2. SSH user is correct: $SSHUser" -ForegroundColor Gray
        Write-Host "  3. You have network connectivity to the server" -ForegroundColor Gray
        Write-Host "  4. SSH service is running on the server" -ForegroundColor Gray
        exit 1
    }
} catch {
    Write-Host "[ERROR] SSH not available or connection error: $_" -ForegroundColor Red
    Write-Host "Make sure SSH is installed on Windows 10+ or install Git Bash" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Step 3: Transfer Apache deployment files
Write-Host "[Step 3/5] Transferring deployment files to server..." -ForegroundColor Cyan
Write-Host "This may take a few seconds..." -ForegroundColor Gray

try {
    # Transfer the entire project
    Write-Host "  Uploading project files..." -ForegroundColor Gray
    scp -r "$LocalProjectPath\*" "${SSHUser}@${ServerIP}:${RemoteProjectPath}\" | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Files transferred successfully" -ForegroundColor Green
    } else {
        Write-Host "[WARNING] Some files may not have transferred" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[ERROR] Transfer failed: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 4: Prepare and run deployment script
Write-Host "[Step 4/5] Preparing deployment script on server..." -ForegroundColor Cyan
Write-Host "This will run the automated Apache deployment" -ForegroundColor Gray
Write-Host ""

$deployCommand = @"
cd $RemoteProjectPath/apache
chmod +x deploy.sh
echo '========================================'
echo 'Starting BestStore Apache Deployment'
echo 'Deployment will take 10-15 minutes'
echo '========================================'
echo ''
sudo bash deploy.sh
"@

# Run the deployment script via SSH
Write-Host "[OK] Deployment starting on remote server..." -ForegroundColor Green
Write-Host ""

ssh "$SSHUser@$ServerIP" $deployCommand

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[WARNING] Deployment script returned with exit code: $LASTEXITCODE" -ForegroundColor Yellow
    Write-Host "This may or may not indicate an error - check the server logs" -ForegroundColor Yellow
}

Write-Host ""

# Step 5: Verification
Write-Host "[Step 5/5] Verifying deployment..." -ForegroundColor Cyan

$verifyCommand = @"
echo 'Checking Apache status...'
sudo systemctl status apache2 --no-pager | head -5
echo ''
echo 'Checking database connection...'
cd $RemoteProjectPath
source venv/bin/activate
python manage.py check 2>&1 | grep -E '(System check|OK|ERROR)' | head -3
echo ''
echo 'Checking SSL certificate...'
sudo certbot certificates 2>&1 | grep -E '(Certificate|Expiry|Domain)' | head -5
"@

Write-Host ""
Write-Host "Deployment Verification:" -ForegroundColor Yellow
Write-Host ""

ssh "$SSHUser@$ServerIP" $verifyCommand

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "              Deployment Process Complete!                   " -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""

Write-Host "NEXT STEPS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Update environment variables on server:" -ForegroundColor Yellow
Write-Host "   ssh ubuntu@10.190.143.234" -ForegroundColor Gray
Write-Host "   sudo nano $RemoteProjectPath/.env" -ForegroundColor Gray
Write-Host ""
Write-Host "   Update these values:" -ForegroundColor Gray
Write-Host "   - DJANGO_SECRET_KEY=your-secure-key" -ForegroundColor Gray
Write-Host "   - EMAIL_HOST_USER=your-email" -ForegroundColor Gray
Write-Host "   - EMAIL_HOST_PASSWORD=your-app-password" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Create Django superuser:" -ForegroundColor Yellow
Write-Host "   ssh ubuntu@10.190.143.234" -ForegroundColor Gray
Write-Host "   cd $RemoteProjectPath" -ForegroundColor Gray
Write-Host "   source venv/bin/activate" -ForegroundColor Gray
Write-Host "   python manage.py createsuperuser" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Test your site:" -ForegroundColor Yellow
Write-Host "   Open browser: https://$Domain" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Access admin panel:" -ForegroundColor Yellow
Write-Host "   https://$Domain/admin/" -ForegroundColor Gray
Write-Host ""

Write-Host "SERVER DETAILS:" -ForegroundColor Cyan
Write-Host "   IP Address: $ServerIP" -ForegroundColor Gray
Write-Host "   Domain: $Domain" -ForegroundColor Gray
Write-Host "   Project Path: $RemoteProjectPath" -ForegroundColor Gray
Write-Host "   SSH User: $SSHUser" -ForegroundColor Gray
Write-Host ""

Write-Host "USEFUL COMMANDS FOR FUTURE:" -ForegroundColor Cyan
Write-Host ""
Write-Host "View logs:" -ForegroundColor Yellow
Write-Host "    ssh ubuntu@10.190.143.234 sudo tail -f /var/log/apache2/beststore_error.log" -ForegroundColor Gray
Write-Host ""
Write-Host "Check status:" -ForegroundColor Yellow
Write-Host "    ssh ubuntu@10.190.143.234 sudo systemctl status apache2" -ForegroundColor Gray
Write-Host ""
Write-Host "Restart services:" -ForegroundColor Yellow
Write-Host "    ssh ubuntu@10.190.143.234 sudo systemctl restart apache2" -ForegroundColor Gray
Write-Host ""
Write-Host "Database backup:" -ForegroundColor Yellow
Write-Host "    ssh ubuntu@10.190.143.234 sudo -u postgres pg_dump beststore_db > backup.sql" -ForegroundColor Gray
Write-Host ""

Write-Host "DEPLOYMENT COMPLETE - Configuration complete!" -ForegroundColor Green
Write-Host ""
