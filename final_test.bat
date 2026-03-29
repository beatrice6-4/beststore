@echo off
echo Testing IIS Site...
echo.

echo Checking if port 20306 is listening...
netstat -ano | findstr "20306" >nul
if %errorlevel% neq 0 (
    echo ERROR: IIS is not listening on port 20306
    goto end
)
echo ✓ IIS is listening on port 20306

echo.
echo Testing HTTP connection...
powershell -Command "$ProgressPreference = 'SilentlyContinue'; try { Invoke-WebRequest -Uri 'http://localhost:20306/' -TimeoutSec 5 -UseBasicParsing | Out-Null; Write-Host 'SUCCESS: Site is responding!' } catch { Write-Host 'ERROR:' $_.Exception.Message }"

echo.
echo If you see SUCCESS above, the 500.19 error is fixed!
echo Open your browser to: http://localhost:20306

:end
echo.
pause