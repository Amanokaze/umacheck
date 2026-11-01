<#
  업데이트 기능 로컬 테스트 (GitHub 에 아무것도 올리지 않음)

  1) 구버전(OldVersion)과 신버전(NewVersion) 설치 파일을 각각 빌드
  2) 신버전을 가리키는 가짜 릴리즈 목록(feed.json) 생성
  3) 구버전을 설치하고 --update-feed 옵션으로 실행
  → 앱에서 업데이트 창이 뜨면 [업데이트] 를 눌러 설치·재실행까지 확인

  사용 예:
    .\scripts\test_update.ps1             # 빌드 + 설치 + 실행
    .\scripts\test_update.ps1 -SkipBuild  # 이전에 빌드한 설치 파일로 다시 테스트
    .\scripts\test_update.ps1 -BuildOnly  # 설치 파일과 feed.json 만 만들고 설치/실행은 하지 않음
#>
param(
  [string]$OldVersion = "0.0.1",
  [string]$NewVersion = "0.0.2",
  [switch]$SkipBuild,
  [switch]$BuildOnly
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Resolve-Path (Join-Path $ScriptDir "..")
Set-Location $ProjectRoot

$TestDir = Join-Path $env:TEMP "UmaCheck-update-test"
$OldSetup = Join-Path $TestDir "UmaCheck-Setup-v$OldVersion.exe"
$NewSetup = Join-Path $TestDir "UmaCheck-Setup-v$NewVersion.exe"
$Feed = Join-Path $TestDir "feed.json"
$Utf8 = New-Object System.Text.UTF8Encoding($false)

# ── 1) 두 버전 빌드 (src/version.py 를 잠시 바꿨다가 원래대로 복구) ─────────
if (-not $SkipBuild) {
  New-Item -ItemType Directory -Force $TestDir | Out-Null
  $VersionFile = "src\version.py"
  $Original = [IO.File]::ReadAllText($VersionFile)
  try {
    foreach ($v in @($OldVersion, $NewVersion)) {
      $patched = [regex]::Replace($Original, '__version__\s*=\s*"[^"]+"', "__version__ = `"$v`"")
      [IO.File]::WriteAllText($VersionFile, $patched, $Utf8)
      & "$ScriptDir\build_installer.ps1" -Version $v
      Copy-Item "dist-installer\UmaCheck-Setup-v$v.exe" $TestDir -Force
    }
  }
  finally {
    [IO.File]::WriteAllText($VersionFile, $Original, $Utf8)
  }
}
foreach ($f in @($OldSetup, $NewSetup)) {
  if (-not (Test-Path $f)) { throw "Missing $f (run without -SkipBuild first)" }
}

# ── 2) GitHub API 응답 형식의 가짜 릴리즈 목록 ──────────────────────────────
$Asset = Get-Item $NewSetup
$Hash = (Get-FileHash $NewSetup -Algorithm SHA256).Hash.ToLower()
$Release = [ordered]@{
  tag_name   = "v$NewVersion"
  draft      = $false
  prerelease = $false
  html_url   = ""
  body       = "로컬 업데이트 테스트용 릴리즈입니다.`n- 이 내용이 업데이트 창에 표시됩니다."
  assets     = @([ordered]@{
    name                 = $Asset.Name
    size                 = $Asset.Length
    digest               = "sha256:$Hash"
    browser_download_url = ([Uri]$Asset.FullName).AbsoluteUri
  })
}
[IO.File]::WriteAllText($Feed, (ConvertTo-Json -InputObject @($Release) -Depth 5), $Utf8)

if ($BuildOnly) {
  Write-Host "Built: $TestDir"
  exit 0
}

# ── 3) 구버전 설치 후 테스트 피드로 실행 ────────────────────────────────────
Write-Host "Installing v$OldVersion ..."
Start-Process $OldSetup -ArgumentList "/SILENT", "/SUPPRESSMSGBOXES", "/NORESTART" -Wait

$UninstallKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\{A8803416-1B58-4F76-8F03-E59026B8EF2B}_is1"
$InstallDir = (Get-ItemProperty $UninstallKey -ErrorAction SilentlyContinue).InstallLocation
if (-not $InstallDir) { $InstallDir = Join-Path $env:LOCALAPPDATA "Programs\UmaCheck" }
$Exe = Join-Path $InstallDir "UmaCheck.exe"

Write-Host "Launching v$OldVersion with test feed ..."
Start-Process $Exe -ArgumentList "--update-feed", "`"$Feed`""

Write-Host ""
Write-Host "Check in the app:"
Write-Host "  1. Update dialog shows v$OldVersion -> v$NewVersion"
Write-Host "  2. Click [Update] -> download, installer runs, app restarts"
Write-Host "  3. About (i) shows v$NewVersion"
Write-Host ""
Write-Host "Test files: $TestDir"
