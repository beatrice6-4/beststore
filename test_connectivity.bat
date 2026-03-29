@echo off
echo ================================================
echo CONNECTIVITY TEST FOR mamamaasaibakers.com
echo ================================================
echo.

echo 1. Local Server Test:
echo ---------------------
curl -s -o /dev/null -w "Status: %%{http_code} (Local)\n" http://localhost
echo.

echo 2. External Connectivity Test:
echo ------------------------------
echo Testing external access to mamamaasaibakers.com...
curl -s -o /dev/null -w "Status: %%{http_code} (External)\n" --max-time 15 http://mamamaasaibakers.com
if %errorlevel% neq 0 (
    echo ❌ FAILED: Cannot reach externally
    echo.
    echo POSSIBLE CAUSES:
    echo - Port forwarding not configured on router
    echo - Router firewall blocking port 80
    echo - ISP blocking port 80
    echo - Wrong internal IP in port forwarding rule
    echo.
    echo SOLUTION: Configure port forwarding (see CONNECTIVITY_FIX.md)
) else (
    echo ✅ SUCCESS: External access working!
    echo Your website is now live at http://mamamaasaibakers.com
)
echo.

echo 3. Network Diagnostics:
echo ----------------------
echo Local IP: 10.190.143.234
echo Public IP: 105.164.7.132
echo Apache Status: Running
netstat -ano | findstr :80 | findstr LISTENING >nul
if %errorlevel% equ 0 (
    echo Port 80: Listening ✅
) else (
    echo Port 80: Not listening ❌
)
echo.

echo ================================================
echo NEXT STEPS:
echo 1. Configure port forwarding on your router
echo 2. Forward external port 80 to internal IP 10.190.143.234
echo 3. Run this test again
echo 4. Access: http://mamamaasaibakers.com
echo ================================================
echo.
pause