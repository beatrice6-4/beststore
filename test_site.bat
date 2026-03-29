@echo off
echo ==========================================
echo Testing IIS Site: http://localhost:20306
echo ==========================================
echo.

echo Checking if IIS is listening on port 20306...
netstat -ano | findstr ":20306" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ IIS is listening on port 20306
) else (
    echo ✗ IIS is NOT listening on port 20306
    echo.
    echo Please run: .\setup_iis.ps1
    goto :end
)

echo.
echo Testing site response...
powershell -Command "$ErrorActionPreference = 'SilentlyContinue'; try { $request = [System.Net.WebRequest]::Create('http://localhost:20306/'); $request.Timeout = 10000; $response = $request.GetResponse(); Write-Host '✓ SUCCESS: HTTP' $response.StatusCode; $response.Close() } catch { Write-Host '✗ ERROR:' $_.Exception.Message }"

echo.
echo If you see a SUCCESS message above, the 500.19 error is fixed!
echo.
echo Next steps:
echo 1. Open your browser to: http://localhost:20306
echo 2. Follow the setup instructions on the page
echo 3. Run start_beststore.bat to start Django
echo.

:end
echo Press any key to exit...
pause >nul