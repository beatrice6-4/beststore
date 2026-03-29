@echo off
echo ================================================
echo Namecheap DNS Configuration Test
echo Domain: mamamaasaibakers.com
echo Public IP: 105.164.7.132
echo ================================================
echo.

echo 1. Testing DNS Resolution:
echo --------------------------
nslookup mamamaasaibakers.com 8.8.8.8
echo.

echo 2. Testing Website Access:
echo --------------------------
curl -s -o /dev/null -w "HTTP Status: %%{http_code}\nResponse Time: %%{time_total}s\n" --max-time 10 http://mamamaasaibakers.com
if %errorlevel% neq 0 (
    echo ❌ Cannot connect to website
    echo   - Check if DNS has propagated
    echo   - Verify Apache is running
    echo   - Check firewall settings
) else (
    echo ✅ Website is accessible!
)
echo.

echo 3. Local Server Verification:
echo ----------------------------
sc query Apache2.4 | findstr STATE
netstat -ano | findstr :80 | findstr LISTENING >nul
if %errorlevel% equ 0 (
    echo ✅ Apache listening on port 80
) else (
    echo ❌ Apache not listening on port 80
)
echo.

echo 4. Django Application Check:
echo ---------------------------
netstat -ano | findstr :8001 | findstr LISTENING >nul
if %errorlevel% equ 0 (
    echo ✅ Django server running on port 8001
) else (
    echo ❌ Django server not running on port 8001
)
echo.

echo ================================================
echo NEXT STEPS:
echo 1. Add DNS records in Namecheap (see NAMECHEAP_DNS_SETUP.md)
echo 2. Wait 5-60 minutes for DNS propagation
echo 3. Run this test again
echo 4. Access: http://mamamaasaibakers.com
echo ================================================
echo.
pause