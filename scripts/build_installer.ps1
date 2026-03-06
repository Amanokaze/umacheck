param(
  [string]$Version = "0.1.1"
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Resolve-Path (Join-Path $ScriptDir "..")
Set-Location $ProjectRoot

$IsccPath = Join-Path $env:LOCALAPPDATA "Programs\Inno Setup 6\ISCC.exe"
if (-not (Test-Path $IsccPath)) {
  throw "ISCC.exe not found: $IsccPath"
}

Write-Host "[1/4] Cleaning previous build artifacts..."
Remove-Item -Recurse -Force build, dist, dist-installer -ErrorAction SilentlyContinue

Write-Host "[2/4] Creating app icon (ICO)..."
python -c "from PIL import Image; im=Image.open('icon.png').convert('RGBA'); w,h=im.size; s=max(w,h); canvas=Image.new('RGBA',(s,s),(0,0,0,0)); canvas.paste(im,((s-w)//2,(s-h)//2)); canvas.save('icon.ico', sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])"

Write-Host "[3/4] Building executable with PyInstaller..."
python -m PyInstaller `
  --noconfirm `
  --clean `
  --windowed `
  --uac-admin `
  --name UmaCheck `
  --icon icon.ico `
  --add-data "web;web" `
  --add-data "icon.png;." `
  --add-data "LICENSE;." `
  main.py

Write-Host "[4/4] Building Windows installer..."
& $IsccPath "/DAppVersion=$Version" "installer\umacheck.iss"

Write-Host ""
Write-Host "Done."
Write-Host "Installer path: dist-installer\UmaCheck-Setup-v$Version.exe"
