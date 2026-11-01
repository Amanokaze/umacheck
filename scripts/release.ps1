<#
  새 버전 릴리즈: src/version.py 갱신 → 커밋 → 태그 → push
  태그가 push 되면 GitHub Actions(.github/workflows/release.yml)가
  설치 파일을 빌드하고 GitHub Release 를 자동으로 만듭니다.

  사용 예:
    .\scripts\release.ps1 -Version 0.2.0 -Notes "업데이트 자동 확인 기능 추가`n- Gemini 모델 목록 갱신"
#>
param(
  [Parameter(Mandatory = $true)][string]$Version,
  # 릴리즈 노트 (앱의 업데이트 창에 표시됨)
  [string]$Notes = ""
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Resolve-Path (Join-Path $ScriptDir "..")
Set-Location $ProjectRoot

$Version = $Version.TrimStart("v")
if ($Version -notmatch '^\d+\.\d+\.\d+$') { throw "Version must be X.Y.Z (e.g. 0.2.0)" }
$Tag = "v$Version"

# 사전 확인
$Branch = (git rev-parse --abbrev-ref HEAD).Trim()
if ($Branch -ne "main") { throw "Release must be made from 'main' (current: $Branch)" }
if (git status --porcelain) { throw "Working tree is not clean. Commit or stash changes first." }
if (git tag -l $Tag) { throw "Tag $Tag already exists." }

$VersionFile = "src\version.py"
$Content = [IO.File]::ReadAllText($VersionFile)
$Current = [regex]::Match($Content, '__version__\s*=\s*"([^"]+)"').Groups[1].Value
if ([version]$Version -le [version]$Current) { throw "New version $Version must be greater than current $Current" }

# 버전 갱신 + 커밋 + 태그
$Utf8 = New-Object System.Text.UTF8Encoding($false)
$Content = [regex]::Replace($Content, '__version__\s*=\s*"[^"]+"', "__version__ = `"$Version`"")
[IO.File]::WriteAllText($VersionFile, $Content, $Utf8)

$MsgFile = Join-Path $env:TEMP "umacheck-tag-msg.txt"
$Message = if ($Notes) { $Notes } else { "UmaCheck $Tag" }
[IO.File]::WriteAllText($MsgFile, $Message, $Utf8)

git add $VersionFile
git commit -m "Release $Tag"
git tag -a $Tag -F $MsgFile
Remove-Item $MsgFile

Write-Host "Pushing main and $Tag ..."
git push origin main
git push origin $Tag

Write-Host ""
Write-Host "Done. GitHub Actions will build and publish the release:"
Write-Host "  https://github.com/Amanokaze/umacheck/actions"
