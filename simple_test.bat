@echo off
echo Simple IIS Test...
powershell -Command "try { $req = [System.Net.WebRequest]::Create('http://localhost:20306/'); $req.Timeout = 5000; $resp = $req.GetResponse(); Write-Host 'SUCCESS: HTTP' $resp.StatusCode; $resp.Close() } catch { Write-Host 'ERROR:' $_.Exception.Message }"
echo.
pause