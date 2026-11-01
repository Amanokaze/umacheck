param(
  # 생략 시 src/version.py 의 __version__ 을 사용
  [string]$Version = ""
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Resolve-Path (Join-Path $ScriptDir "..")
Set-Location $ProjectRoot

if (-not $Version) {
  $Match = Select-String -Path "src\version.py" -Pattern '__version__\s*=\s*"([^"]+)"'
  if (-not $Match) { throw "Cannot read __version__ from src\version.py" }
  $Version = $Match.Matches[0].Groups[1].Value
}

# ISCC.exe 탐색: 사용자 설치 → 시스템 설치(GitHub Actions 등) → PATH
$IsccCandidates = @(
  (Join-Path $env:LOCALAPPDATA "Programs\Inno Setup 6\ISCC.exe"),
  (Join-Path ${env:ProgramFiles(x86)} "Inno Setup 6\ISCC.exe"),
  (Join-Path $env:ProgramFiles "Inno Setup 6\ISCC.exe")
)
$IsccPath = $IsccCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $IsccPath) {
  $IsccPath = (Get-Command ISCC.exe -ErrorAction SilentlyContinue).Source
}
if (-not $IsccPath) {
  throw "ISCC.exe not found. Install Inno Setup 6."
}

Write-Host "Building UmaCheck v$Version"

Write-Host "[1/4] Cleaning previous build artifacts..."
Remove-Item -Recurse -Force build, dist, dist-installer -ErrorAction SilentlyContinue

Write-Host "[2/4] Creating app icon (ICO)..."
python -c "from PIL import Image; im=Image.open('icon.png').convert('RGBA'); w,h=im.size; s=max(w,h); canvas=Image.new('RGBA',(s,s),(0,0,0,0)); canvas.paste(im,((s-w)//2,(s-h)//2)); canvas.save('icon.ico', sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])"
if ($LASTEXITCODE -ne 0) { throw "Icon creation failed" }

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
if ($LASTEXITCODE -ne 0) { throw "PyInstaller build failed" }

Write-Host "[4/4] Building Windows installer..."
& $IsccPath "/DAppVersion=$Version" "installer\umacheck.iss"
if ($LASTEXITCODE -ne 0) { throw "Inno Setup build failed" }

Write-Host ""
Write-Host "Done."
Write-Host "Installer path: dist-installer\UmaCheck-Setup-v$Version.exe"
