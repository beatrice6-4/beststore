@echo off
echo Testing BestStore Production Configuration...
echo.

echo 1. Testing localhost access:
curl -s -o /dev/null -w "Status: %%{http_code}\n" http://localhost
echo.

echo 2. Testing Django server directly:
curl -s -o /dev/null -w "Status: %%{http_code}\n" http://127.0.0.1:8001
echo.

echo 3. Checking services status:
sc query Apache2.4 | findstr STATE
echo.

echo 4. Checking if Waitress is running:
netstat -ano | findstr :8001
echo.

echo Configuration test complete!
echo If all tests show Status: 200, your production setup is working.
echo.
echo For domain access (mamamaasaibakers.com), ensure DNS is configured.
echo.
pause