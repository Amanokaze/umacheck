"""
updater.py - GitHub Releases 기반 업데이트 확인 / 다운로드 / 설치
"""
import os
import re
import json
import ctypes
import hashlib
import tempfile
import urllib.request

from src.version import __version__, GITHUB_REPO

API_URL     = f"https://api.github.com/repos/{GITHUB_REPO}/releases?per_page=20"
ASSET_RE    = re.compile(r"^UmaCheck-Setup-v[\d.]+\.exe$", re.IGNORECASE)
VERSION_RE  = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")
USER_AGENT  = f"UmaCheck/{__version__}"
DOWNLOAD_DIR = os.path.join(tempfile.gettempdir(), "UmaCheck-update")


def parse_version(tag: str) -> tuple | None:
    m = VERSION_RE.match((tag or "").strip())
    return tuple(int(x) for x in m.groups()) if m else None


def _request(url: str, accept: str):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": accept})
    return urllib.request.urlopen(req, timeout=15)


# ── 최신 릴리즈 확인 ────────────────────────────────────────────────────────
def check_latest(feed_url: str | None = None) -> dict:
    """
    정식 릴리즈(draft/prerelease 제외) 중 가장 높은 버전을 찾아 현재 버전과 비교합니다.
    태그는 v1.2.3 형식이어야 하며, 설치 파일(UmaCheck-Setup-v*.exe)이 첨부돼 있어야 합니다.
    feed_url: GitHub API 대신 사용할 릴리즈 목록 (로컬 테스트용, file:// 가능)
    """
    current = parse_version(__version__)
    with _request(feed_url or API_URL, "application/vnd.github+json") as res:
        releases = json.load(res)

    best = None
    for rel in releases:
        if rel.get("draft") or rel.get("prerelease"):
            continue
        ver = parse_version(rel.get("tag_name", ""))
        asset = next((a for a in rel.get("assets", []) if ASSET_RE.match(a.get("name", ""))), None)
        if not ver or not asset:
            continue
        if best is None or ver > best[0]:
            best = (ver, rel, asset)

    if best is None:
        return {"available": False, "current": __version__}

    ver, rel, asset = best
    return {
        "available":  ver > current,
        "current":    __version__,
        "latest":     ".".join(map(str, ver)),
        "notes":      rel.get("body") or "",
        "page_url":   rel.get("html_url"),
        "asset_name": asset["name"],
        "asset_url":  asset["browser_download_url"],
        "asset_size": asset.get("size", 0),
        "digest":     asset.get("digest") or "",   # "sha256:<hex>"
    }


# ── 설치 파일 다운로드 ──────────────────────────────────────────────────────
def download(info: dict, on_progress=None) -> str:
    """설치 파일을 임시 폴더에 받고 크기/SHA-256을 검증한 뒤 경로를 반환합니다."""
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    path = os.path.join(DOWNLOAD_DIR, os.path.basename(info["asset_name"]))
    total = int(info.get("asset_size") or 0)
    sha = hashlib.sha256()
    done = 0

    with _request(info["asset_url"], "application/octet-stream") as res, open(path, "wb") as f:
        total = total or int(res.headers.get("Content-Length") or 0)
        while True:
            chunk = res.read(256 * 1024)
            if not chunk:
                break
            f.write(chunk)
            sha.update(chunk)
            done += len(chunk)
            if on_progress and total:
                on_progress(min(99, done * 100 // total))

    if total and done != total:
        os.remove(path)
        raise RuntimeError("다운로드가 완료되지 않았습니다.")
    digest = info.get("digest", "")
    if digest.startswith("sha256:") and digest[7:].lower() != sha.hexdigest():
        os.remove(path)
        raise RuntimeError("설치 파일 검증(SHA-256)에 실패했습니다.")

    if on_progress:
        on_progress(100)
    return path


# ── 설치 실행 ───────────────────────────────────────────────────────────────
def launch_installer(path: str):
    """
    Inno Setup 설치 파일을 자동 모드로 실행합니다.
    /SILENT: 진행 창만 표시, /CLOSEAPPLICATIONS: 사용 중인 파일이 있으면 앱 종료 후 교체.
    /UPDATE=1: 설치가 끝나면 installer/umacheck.iss 의 [Run] 항목이 앱을 다시 실행합니다.
    """
    params = "/SILENT /SUPPRESSMSGBOXES /NORESTART /CLOSEAPPLICATIONS /UPDATE=1"
    ret = ctypes.windll.shell32.ShellExecuteW(None, "open", path, params, os.path.dirname(path), 1)
    if ret <= 32:
        raise RuntimeError(f"설치 프로그램 실행 실패 (코드 {ret})")
