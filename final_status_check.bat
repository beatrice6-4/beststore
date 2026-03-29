@echo off
echo ================================================
echo BESTSTORE DEPLOYMENT STATUS CHECK
echo ================================================
echo.

echo 🔍 CHECKING COMPONENTS:
echo -----------------------

REM Check Apache
sc query Apache2.4 | findstr STATE >nul
if %errorlevel% equ 0 (
    echo ✅ Apache Service: Running
) else (
    echo ❌ Apache Service: Stopped
)

REM Check port 80
netstat -ano | findstr :80 | findstr LISTENING >nul
if %errorlevel% equ 0 (
    echo ✅ Port 80: Listening
) else (
    echo ❌ Port 80: Not listening
)

REM Check DNS
nslookup mamamaasaibakers.com >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ DNS Resolution: Working
) else (
    echo ❌ DNS Resolution: Failed
)

echo.
echo 🏠 LOCAL ACCESS TEST:
echo -------------------
curl -s -o /dev/null -w "Status Code: %%{http_code}\n" http://localhost
echo.

echo 🌐 EXTERNAL ACCESS TEST:
echo ----------------------
echo Testing mamamaasaibakers.com...
curl -s -o /dev/null -w "Status Code: %%{http_code}\n" --max-time 15 http://mamamaasaibakers.com
if %errorlevel% neq 0 (
    echo ❌ EXTERNAL ACCESS: FAILED (Port forwarding needed)
    echo.
    echo 🚨 SOLUTION REQUIRED:
    echo Configure port forwarding on your router
    echo Forward external port 80 to internal IP 10.190.143.234
) else (
    echo ✅ EXTERNAL ACCESS: WORKING!
    echo 🎉 Your website is live at http://mamamaasaibakers.com
)

echo.
echo 📋 NETWORK INFO:
echo ---------------
echo Internal IP: 10.190.143.234
echo External IP: 105.164.7.132
echo Router IP (Default Gateway):
ipconfig | findstr "Default Gateway" | findstr [0-9]

echo.
echo 🔧 QUICK FIX:
echo -----------
echo 1. Open browser and go to your router IP (see above)
echo 2. Login (usually admin/admin)
echo 3. Find 'Port Forwarding' section
echo 4. Add rule: External Port 80 → Internal IP 10.190.143.234
echo 5. Save and run this test again

echo.
echo 📁 HELP FILES:
echo -------------
echo FINAL_PORT_FORWARDING_GUIDE.md - Complete setup guide
echo CONNECTIVITY_FIX.md - Detailed troubleshooting
echo test_connectivity.bat - This test script

echo.
pause