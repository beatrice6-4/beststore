@echo off
echo ================================================
echo Starting BestStore Production Deployment
echo ================================================
echo Domain: mamamaasaibakers.com
echo Public IP: 105.164.7.132
echo Local Access: http://localhost
echo Production Access: http://mamamaasaibakers.com
echo ================================================
echo.

REM Start Waitress (Django application server)
start "Django Server - mamamaasaibakers.com" cmd /c "cd C:\Users\BRAMWEL\OneDrive\Desktop\BESTSTORE && C:\Users\BRAMWEL\OneDrive\Desktop\BESTSTORE\venv\Scripts\python.exe -m waitress --host=127.0.0.1 --port=8001 beststore.wsgi:application"

REM Wait a moment for Django to start
timeout /t 5 /nobreak > nul

REM Start Apache
net start Apache2.4

echo.
echo ✅ Services Started Successfully!
echo.
echo 🌐 PRODUCTION ACCESS:
echo    http://mamamaasaibakers.com
echo    http://www.mamamaasaibakers.com
echo.
echo 🏠 LOCAL TESTING:
echo    http://localhost
echo    http://127.0.0.1
echo.
echo 🔧 MANAGEMENT:
echo    Admin Panel: http://mamamaasaibakers.com/admin
echo    Stop Services: stop_apache_deployment.bat
echo    Test DNS: verify_namecheap_setup.bat
echo.
echo ⚠️  IMPORTANT:
echo    DNS must be configured in Namecheap for public access
echo    See: NAMECHEAP_DNS_SETUP.md
echo.
pause