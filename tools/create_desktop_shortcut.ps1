$ErrorActionPreference = "Stop"

$racine = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $racine

$ressources = Join-Path $racine "ressources"
New-Item -ItemType Directory -Force $ressources | Out-Null

$iconPath = Join-Path $ressources "forge_souveraine.ico"
$tempPng = Join-Path $env:TEMP "forge_souveraine_icon.png"

Add-Type -AssemblyName System.Drawing

$bitmap = New-Object System.Drawing.Bitmap 256, 256
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit

$rectangle = New-Object System.Drawing.Rectangle 0, 0, 256, 256
$fond = New-Object System.Drawing.Drawing2D.LinearGradientBrush `
  $rectangle,
  ([System.Drawing.Color]::FromArgb(255, 2, 12, 7)),
  ([System.Drawing.Color]::FromArgb(255, 18, 42, 18)),
  45

$graphics.FillRectangle($fond, $rectangle)

$or = [System.Drawing.Color]::FromArgb(255, 214, 178, 24)
$vert = [System.Drawing.Color]::FromArgb(255, 125, 255, 178)
$ombre = [System.Drawing.Color]::FromArgb(180, 0, 0, 0)

$penOr = New-Object System.Drawing.Pen $or, 8
$penVert = New-Object System.Drawing.Pen $vert, 3
$brushOr = New-Object System.Drawing.SolidBrush $or
$brushVert = New-Object System.Drawing.SolidBrush $vert
$brushOmbre = New-Object System.Drawing.SolidBrush $ombre

$graphics.DrawEllipse($penOr, 24, 24, 208, 208)
$graphics.DrawArc($penVert, 38, 38, 180, 180, 205, 105)

$fontGrand = New-Object System.Drawing.Font "Georgia", 86, ([System.Drawing.FontStyle]::Bold)
$fontPetit = New-Object System.Drawing.Font "Segoe UI", 18, ([System.Drawing.FontStyle]::Bold)

$format = New-Object System.Drawing.StringFormat
$format.Alignment = [System.Drawing.StringAlignment]::Center
$format.LineAlignment = [System.Drawing.StringAlignment]::Center

$graphics.DrawString("FS", $fontGrand, $brushOmbre, (New-Object System.Drawing.RectangleF 6, 12, 256, 170), $format)
$graphics.DrawString("FS", $fontGrand, $brushOr, (New-Object System.Drawing.RectangleF 0, 6, 256, 170), $format)

$graphics.DrawString("SUBTITRES", $fontPetit, $brushVert, (New-Object System.Drawing.RectangleF 0, 160, 256, 40), $format)

$bitmap.Save($tempPng, [System.Drawing.Imaging.ImageFormat]::Png)

$graphics.Dispose()
$bitmap.Dispose()
$fond.Dispose()
$penOr.Dispose()
$penVert.Dispose()
$brushOr.Dispose()
$brushVert.Dispose()
$brushOmbre.Dispose()
$fontGrand.Dispose()
$fontPetit.Dispose()

$pngBytes = [System.IO.File]::ReadAllBytes($tempPng)
$file = [System.IO.File]::Open($iconPath, [System.IO.FileMode]::Create)
$writer = New-Object System.IO.BinaryWriter $file

$writer.Write([UInt16]0)
$writer.Write([UInt16]1)
$writer.Write([UInt16]1)
$writer.Write([byte]0)
$writer.Write([byte]0)
$writer.Write([byte]0)
$writer.Write([byte]0)
$writer.Write([UInt16]1)
$writer.Write([UInt16]32)
$writer.Write([UInt32]$pngBytes.Length)
$writer.Write([UInt32]22)
$writer.Write($pngBytes)

$writer.Close()
$file.Close()

Remove-Item $tempPng -Force -ErrorAction SilentlyContinue

$desktop = [Environment]::GetFolderPath("Desktop")
$linkPath = Join-Path $desktop "Forge Souveraine.lnk"
$targetPath = Join-Path $racine "start_dev.bat"

if (!(Test-Path $targetPath)) {
  throw "start_dev.bat introuvable: $targetPath"
}

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($linkPath)
$shortcut.TargetPath = $targetPath
$shortcut.WorkingDirectory = $racine
$shortcut.IconLocation = "$iconPath,0"
$shortcut.Description = "Forge Souveraine - локальная кузница субтитров"
$shortcut.Save()

Write-Host "Desktop shortcut created:" -ForegroundColor Green
Write-Host $linkPath -ForegroundColor Yellow
Write-Host "Icon:" -ForegroundColor Green
Write-Host $iconPath -ForegroundColor Yellow
