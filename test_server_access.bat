@echo off
echo ================================================
echo SERVER ACCESS DIAGNOSTIC TEST
echo ================================================
echo.

echo 🔍 CHECKING SERVER COMPONENTS:
echo ------------------------------

REM Check Apache service
sc query Apache2.4 | findstr STATE >nul
if %errorlevel% equ 0 (
    echo ✅ Apache Service: RUNNING
) else (
    echo ❌ Apache Service: STOPPED
    echo    Solution: Run start_apache_deployment.bat
)

REM Check port 80
netstat -ano | findstr :80 | findstr LISTENING >nul
if %errorlevel% equ 0 (
    echo ✅ Port 80: LISTENING
) else (
    echo ❌ Port 80: NOT LISTENING
)

echo.
echo 🏠 TESTING LOCAL ACCESS:
echo -----------------------
curl -s -o /dev/null -w "Status: %%{http_code}\n" http://localhost
if %errorlevel% neq 0 (
    echo ❌ Local access failed
) else (
    echo ✅ Local access working
)

echo.
echo 🌐 TESTING NETWORK ACCESS:
echo -------------------------
echo Server IP: 10.190.143.234
ping -n 1 10.190.143.234 >nul
if %errorlevel% equ 0 (
    echo ✅ Server reachable via ping
) else (
    echo ❌ Server not reachable via ping
)

curl -s -o /dev/null -w "Status: %%{http_code}\n" --max-time 5 http://10.190.143.234
if %errorlevel% neq 0 (
    echo ❌ Network access failed (firewall/network issue)
    echo.
    echo TROUBLESHOOTING:
    echo - Check Windows Firewall settings
    echo - Ensure both devices on same network
    echo - Try from different device
    echo - Check antivirus/firewall software
) else (
    echo ✅ Network access working!
)

echo.
echo 📋 HOW TO ACCESS YOUR SERVER:
echo ----------------------------
echo 1. From this computer (localhost):
echo    http://localhost
echo    http://127.0.0.1
echo.
echo 2. From other devices on same network:
echo    http://10.190.143.234
echo.
echo 3. From anywhere (after port forwarding):
echo    http://mamamaasaibakers.com

echo.
echo 📁 HELP FILES:
echo -------------
echo SERVER_ACCESS_GUIDE.md - Complete troubleshooting guide
echo FINAL_PORT_FORWARDING_GUIDE.md - For external access

echo.
pause