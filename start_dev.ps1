$ErrorActionPreference = "Stop"

$racine = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $racine

Write-Host "Forge Souveraine dev launcher" -ForegroundColor Green

$python = Join-Path $racine ".venv\Scripts\python.exe"
$interface = Join-Path $racine "interface"

if (!(Test-Path $python)) {
  Write-Host "Venv introuvable. Lance d'abord l'installation Python." -ForegroundColor Red
  exit 1
}

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-ExecutionPolicy", "Bypass",
  "-Command",
  "Set-Location '$racine'; .\.venv\Scripts\python.exe -m uvicorn serveur:application --host 127.0.0.1 --port 8787 --reload"
)

Start-Sleep -Seconds 2

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-ExecutionPolicy", "Bypass",
  "-Command",
  "Set-Location '$interface'; npm.cmd run dev -- --host 127.0.0.1 --port 5173"
)

Start-Sleep -Seconds 3
Start-Process "http://127.0.0.1:5173/"

Write-Host "Backend:  http://127.0.0.1:8787/api/sante" -ForegroundColor Yellow
Write-Host "Frontend: http://127.0.0.1:5173/" -ForegroundColor Yellow
