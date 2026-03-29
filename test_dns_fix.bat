@echo off
echo ================================================
echo DNS FIX VERIFICATION
echo Domain: mamamaasaibakers.com
echo Expected IP: 105.164.7.132
echo ================================================
echo.

echo 1. Testing IPv4 A Record:
echo -------------------------
nslookup -type=A mamamaasaibakers.com 8.8.8.8
echo.

echo 2. Testing IPv6 AAAA Record (should be minimal):
echo ------------------------------------------------
nslookup -type=AAAA mamamaasaibakers.com 8.8.8.8
echo.

echo 3. Testing Website Access:
echo --------------------------
curl -s -o /dev/null -w "HTTP Status: %%{http_code}\n" --max-time 10 http://mamamaasaibakers.com
if %errorlevel% equ 0 (
    echo ✅ SUCCESS: Website is accessible!
) else (
    echo ❌ FAILED: Cannot access website
    echo    - DNS may still be propagating (wait 5-10 minutes)
    echo    - Check if A record is correctly set in Namecheap
)
echo.

echo 4. Local Server Check:
echo ----------------------
sc query Apache2.4 | findstr STATE
netstat -ano | findstr :80 | findstr LISTENING >nul
if %errorlevel% equ 0 (
    echo ✅ Apache is running and listening
) else (
    echo ❌ Apache is not running properly
)
echo.

echo ================================================
echo SUMMARY:
echo - A record should point @ to 105.164.7.132
echo - Test again in 5-10 minutes after DNS changes
echo - Use https://dnschecker.org/ to verify globally
echo ================================================
echo.
pause