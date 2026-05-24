param(
  [switch]$KeepBackend
)

$ErrorActionPreference = "Stop"

$racine = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $racine

function Executer-Controle {
  param(
    [string]$Titre,
    [scriptblock]$Commande
  )

  Write-Host ""
  Write-Host "== $Titre ==" -ForegroundColor Yellow

  & $Commande

  if ($LASTEXITCODE -ne 0) {
    throw "$Titre failed with exit code $LASTEXITCODE"
  }
}

Write-Host "Forge Souveraine smoke test" -ForegroundColor Green

Executer-Controle "Python compile" {
  .\.venv\Scripts\python.exe -m py_compile .\serveur.py .\noyau\transcription.py .\noyau\sous_titres.py .\noyau\rendu.py
}

Push-Location .\interface
Executer-Controle "Frontend build" {
  npm.cmd run build
}
Pop-Location

try {
  $anciensPids = Get-NetTCPConnection -LocalPort 8787 -State Listen -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty OwningProcess -Unique

  foreach ($pidItem in $anciensPids) {
    Write-Host "Stopping old backend PID $pidItem" -ForegroundColor DarkYellow
    Stop-Process -Id $pidItem -Force -ErrorAction SilentlyContinue
  }
} catch {}

Start-Sleep -Seconds 1

Remove-Item .\donnees\uvicorn.out.log -Force -ErrorAction SilentlyContinue
Remove-Item .\donnees\uvicorn.err.log -Force -ErrorAction SilentlyContinue

$backend = Start-Process `
  -FilePath ".\.venv\Scripts\python.exe" `
  -ArgumentList @("-m", "uvicorn", "serveur:application", "--host", "127.0.0.1", "--port", "8787") `
  -WindowStyle Hidden `
  -RedirectStandardOutput ".\donnees\uvicorn.out.log" `
  -RedirectStandardError ".\donnees\uvicorn.err.log" `
  -PassThru

try {
  $ok = $false

  foreach ($i in 1..40) {
    Start-Sleep -Seconds 1

    try {
      Invoke-RestMethod http://127.0.0.1:8787/api/sante | Out-Null
      $ok = $true
      break
    } catch {}
  }

  if (-not $ok) {
    Get-Content .\donnees\uvicorn.err.log -Tail 160 -ErrorAction SilentlyContinue
    throw "Backend did not start"
  }

  Write-Host "Backend alive" -ForegroundColor Green

  $testDir = "D:\PYTHON\forge-souveraine\donnees\test"
  New-Item -ItemType Directory -Force $testDir | Out-Null

  $wav = Join-Path $testDir "forge_souveraine_test.wav"
  $mp4 = Join-Path $testDir "forge_souveraine_test.mp4"

  Add-Type -AssemblyName System.Speech
  $voice = New-Object System.Speech.Synthesis.SpeechSynthesizer
  $voice.SetOutputToWaveFile($wav)
  $voice.Speak("Forge Souveraine test. Imperial subtitles are ready.")
  $voice.Dispose()

  if (!(Test-Path $wav)) {
    throw "Test WAV was not created"
  }

  $makeVideo = @"
from pathlib import Path
import subprocess
from imageio_ffmpeg import get_ffmpeg_exe

racine = Path("donnees/test")
wav = racine / "forge_souveraine_test.wav"
mp4 = racine / "forge_souveraine_test.mp4"
ffmpeg = get_ffmpeg_exe()

cmd = [
    ffmpeg,
    "-y",
    "-f", "lavfi",
    "-i", "color=c=black:s=1080x1920:r=30:d=6",
    "-i", str(wav),
    "-shortest",
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac",
    "-b:a", "160k",
    str(mp4),
]

result = subprocess.run(cmd, capture_output=True, text=True)

if result.returncode != 0:
    raise SystemExit(result.stderr[-4000:])

print(mp4)
"@

  $makeVideoPath = Join-Path $testDir "_make_test_video.py"
  Set-Content -Encoding UTF8 $makeVideoPath $makeVideo

  Executer-Controle "Create test vertical MP4" {
    .\.venv\Scripts\python.exe $makeVideoPath
  }

  Remove-Item $makeVideoPath -Force -ErrorAction SilentlyContinue

  if (!(Test-Path $mp4)) {
    throw "Test MP4 was not created"
  }

  Write-Host "Test MP4 created: $mp4" -ForegroundColor Green

  $uploadJson = & curl.exe -s -F "fichier=@$mp4" http://127.0.0.1:8787/api/televerser

  if ($LASTEXITCODE -ne 0) {
    throw "Upload curl failed"
  }

  $upload = $uploadJson | ConvertFrom-Json

  if (-not $upload.nom_stocke) {
    Write-Host $uploadJson
    throw "Upload failed"
  }

  Write-Host "Uploaded: $($upload.nom_stocke)" -ForegroundColor Green

  $body = @{
    nom_stocke = $upload.nom_stocke
    langue = "en"
    modele = "tiny"
    style = "imperial"
  } | ConvertTo-Json

  $tache = Invoke-RestMethod `
    -Method Post `
    -Uri "http://127.0.0.1:8787/api/taches/creer" `
    -ContentType "application/json" `
    -Body $body

  if (-not $tache.identifiant_tache) {
    throw "Task was not created"
  }

  Write-Host "Task created: $($tache.identifiant_tache)" -ForegroundColor Green

  $execution = Invoke-RestMethod `
    -Method Post `
    -Uri "http://127.0.0.1:8787/api/taches/$($tache.identifiant_tache)/executer"

  if ($execution.etat -ne "terminee") {
    $execution | ConvertTo-Json -Depth 10
    throw "Transcription failed"
  }

  Write-Host "Transcription OK. Segments: $($execution.segments)" -ForegroundColor Green

  $rendu = Invoke-RestMethod `
    -Method Post `
    -Uri "http://127.0.0.1:8787/api/taches/$($tache.identifiant_tache)/rendre"

  if ($rendu.etat -ne "terminee" -or -not $rendu.sorties.mp4) {
    $rendu | ConvertTo-Json -Depth 10
    throw "MP4 render failed"
  }

  Write-Host "Render OK: $($rendu.sorties.mp4)" -ForegroundColor Green

  foreach ($cle in @("srt", "ass", "json", "mp4")) {
    $nom = $rendu.sorties.PSObject.Properties[$cle].Value

    if (-not $nom) {
      throw "Missing output: $cle"
    }

    $destination = Join-Path $testDir ("downloaded." + $cle)
    $url = "http://127.0.0.1:8787/api/sorties/$([Uri]::EscapeDataString($nom))"

    Invoke-WebRequest -Uri $url -OutFile $destination | Out-Null

    if (!(Test-Path $destination)) {
      throw "Download failed: $cle"
    }

    if ((Get-Item $destination).Length -le 0) {
      throw "Downloaded file is empty: $cle"
    }

    Write-Host "Download OK: $cle" -ForegroundColor Green
  }

  Write-Host ""
  Write-Host "AUTOTEST OK: upload -> task -> whisper -> SRT/ASS/JSON -> MP4 -> downloads" -ForegroundColor Green
}
finally {
  if (-not $KeepBackend -and $backend -and -not $backend.HasExited) {
    Stop-Process -Id $backend.Id -Force -ErrorAction SilentlyContinue
    Write-Host "Backend stopped" -ForegroundColor DarkYellow
  }
}
