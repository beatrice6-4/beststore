@echo off
REM BestStore Apache Diagnostic Script
REM This will help diagnose why Apache returns 503 Service Unavailable

echo ============================================================
echo   BestStore Apache - Diagnostic Report
echo ============================================================
echo.

echo [1] Testing SSH connection to server...
ssh -o ConnectTimeout=5 ubuntu@10.190.143.234 "echo 'SSH Connection OK'"
if errorlevel 1 (
    echo SSH Connection FAILED
    echo.
) else (
    echo SSH Connection OK
    echo.
    
    echo [2] Checking Apache Status...
    ssh ubuntu@10.190.143.234 "sudo systemctl status apache2 | head -10"
    echo.
    
    echo [3] Checking for WSGI daemon errors...
    ssh ubuntu@10.190.143.234 "sudo tail -50 /var/log/apache2/beststore_error.log"
    echo.
    
    echo [4] Checking Django health...
    ssh ubuntu@10.190.143.234 "cd /var/www/mamamaasaibakers && source venv/bin/activate && python manage.py check"
    echo.
    
    echo [5] Checking PostgreSQL connection...
    ssh ubuntu@10.190.143.234 "sudo -u postgres psql -d beststore_db -c 'SELECT version();'"
    echo.
    
    echo [6] Checking WSGI processes...
    ssh ubuntu@10.190.143.234 "ps aux | grep -i wsgi"
    echo.
    
    echo [7] Checking file permissions...
    ssh ubuntu@10.190.143.234 "ls -la /var/www/mamamaasaibakers/beststore/wsgi.py"
    echo.
    
    echo [8] Checking .env file...
    ssh ubuntu@10.190.143.234 "ls -la /var/www/mamamaasaibakers/.env && echo '.env file exists'"
    echo.
)

echo ============================================================
echo Diagnostic Complete!
echo ============================================================
pause
