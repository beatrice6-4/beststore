@echo off
echo DNS Configuration Test for mamamaasaibakers.com
echo ================================================
echo.

echo 1. Testing DNS Resolution:
echo --------------------------
nslookup mamamaasaibakers.com 2>nul
if %errorlevel% neq 0 (
    echo ❌ DNS lookup failed - domain not configured yet
) else (
    echo ✅ DNS lookup successful
)
echo.

echo 2. Testing Website Access:
echo --------------------------
curl -s -o /dev/null -w "HTTP Status: %%{http_code}\n" http://mamamaasaibakers.com
echo.

echo 3. Local Server Status:
echo ----------------------
sc query Apache2.4 | findstr STATE
netstat -ano | findstr :80 | findstr LISTENING >nul
if %errorlevel% equ 0 (
    echo ✅ Apache listening on port 80
) else (
    echo ❌ Apache not listening on port 80
)
echo.

echo 4. Django Application Status:
echo ----------------------------
netstat -ano | findstr :8001 | findstr LISTENING >nul
if %errorlevel% equ 0 (
    echo ✅ Django server running on port 8001
) else (
    echo ❌ Django server not running on port 8001
)
echo.

echo ================================================
echo DNS Setup Summary:
echo - Domain: mamamaasaibakers.com
echo - Required: A record pointing to your PUBLIC IP
echo - Test again after DNS propagation (24-48 hours)
echo ================================================
echo.
pause