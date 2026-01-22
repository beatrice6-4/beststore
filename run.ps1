# Run Django management commands with venv Python
# Usage: .\run.ps1 runserver
#        .\run.ps1 migrate
#        .\run.ps1 makemigrations

$venvPython = ".\venv\Scripts\python.exe"
$command = $args -join " "

if ($command -eq "") {
    Write-Host "Usage: .\run.ps1 <django-command>"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\run.ps1 runserver"
    Write-Host "  .\run.ps1 migrate"
    Write-Host "  .\run.ps1 makemigrations"
    exit 1
}

Write-Host "Running: $venvPython manage.py $command" -ForegroundColor Green
& $venvPython manage.py $command
