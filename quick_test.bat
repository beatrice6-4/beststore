@echo off
echo Testing IIS Site Accessibility...
echo.

powershell -Command "try { $web = New-Object System.Net.WebClient; $result = $web.DownloadString('http://localhost:20306/'); Write-Host 'SUCCESS: Site is working!'; Write-Host 'Content preview:'; Write-Host $result.Substring(0, [Math]::Min(100, $result.Length)) } catch { Write-Host 'ERROR:' $_.Exception.Message }"

echo.
echo If you see SUCCESS above, the 500.19 error is fixed!
echo.
pause