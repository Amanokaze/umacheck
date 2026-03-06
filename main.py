"""
main.py - UmaCheck 메인 진입점
pywebview 기반 Windows 데스크탑 앱
"""
import os
import sys
import json
import queue
import base64
import threading
import subprocess
import ctypes
import webview

# ── 경로 설정 ──────────────────────────────────────────────────────────────
APP_TITLE = "UmaCheck"
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
WEB_DIR   = os.path.join(BASE_DIR, "web")
ICON_PATH = os.path.join(BASE_DIR, "icon.png")
CFG_PATH  = os.path.join(BASE_DIR, "config.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

DEFAULT_CFG = {
    "game_folder":    r"C:\kakaogames\umamusume",
    "scroll_delay":   1.0,
    "scroll_amount":  6,
    "diff_threshold": 0.995,
}


# ── 설정 ───────────────────────────────────────────────────────────────────
def load_config() -> dict:
    if os.path.exists(CFG_PATH):
        try:
            with open(CFG_PATH, "r", encoding="utf-8") as f:
                stored = json.load(f)
            return {**DEFAULT_CFG, **stored}
        except Exception:
            pass
    return dict(DEFAULT_CFG)


def save_config(cfg: dict):
    with open(CFG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


# ── 이벤트 큐 (Python → JS 폴링용) ────────────────────────────────────────
_event_queue: queue.Queue = queue.Queue()


def _push(type_: str, **kw):
    _event_queue.put({"type": type_, **kw})


# ── JS에 노출할 API 클래스 ──────────────────────────────────────────────────
class Api:
    """pywebview에 의해 JS window.pywebview.api 로 노출됩니다."""

    # 설정
    def get_config(self) -> dict:
        return load_config()

    def save_config(self, cfg: dict):
        current = load_config()
        current.update(cfg)
        save_config(current)
        # capture 모듈에 반영
        self._apply_capture_settings(current)

    def _apply_capture_settings(self, cfg: dict):
        try:
            import src.capture as cap
            cap.SCROLL_DELAY    = float(cfg.get("scroll_delay",   0.8))
            cap.SCROLL_AMOUNT   = -abs(int(cfg.get("scroll_amount", 5)))
            cap.DIFF_THRESHOLD  = float(cfg.get("diff_threshold", 0.995))
        except Exception:
            pass

    # 아이콘 → base64 data URL
    def get_icon_url(self) -> str:
        with open(ICON_PATH, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        return f"data:image/png;base64,{b64}"

    # 게임 실행 여부
    def is_game_running(self) -> bool:
        try:
            from src.capture import capturer
            return capturer.is_game_running()
        except Exception:
            return False

    # 폴더 탐색
    def browse_folder(self) -> str | None:
        result = webview.windows[0].create_file_dialog(
            webview.FOLDER_DIALOG
        )
        if result:
            return result[0]
        return None

    # 캡처 시작
    def start_capture(self):
        cfg = load_config()
        self._apply_capture_settings(cfg)

        # 큐 비우기
        while not _event_queue.empty():
            try: _event_queue.get_nowait()
            except Exception: pass

        from src.capture import capturer
        capturer.start(
            on_status=lambda msg: _push("status", msg=msg),
            on_progress=lambda pct: _push("progress", pct=pct),
            on_done=lambda path: _push("done", path=path),
            on_error=lambda msg: _push("error", msg=msg),
        )

    # 캡처 중단
    def stop_capture(self):
        from src.capture import capturer
        capturer.stop()

    # JS 폴링: 이벤트 하나씩 꺼내기
    def poll_event(self) -> dict | None:
        try:
            return _event_queue.get_nowait()
        except queue.Empty:
            return None

    # 이미지 → base64
    def read_image_base64(self, path: str) -> str:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("ascii")

    # 게임 실행 (ShellExecuteW: 런처가 스스로 UAC 요청하도록 위임)
    def launch_game(self) -> str:
        cfg = load_config()
        folder = cfg.get("game_folder", r"C:\kakaogames\umamusume")
        exe = os.path.join(folder, "UMMS_Launcher.exe")
        if not os.path.exists(exe):
            return f"실행 파일을 찾을 수 없습니다: {exe}"
        try:
            ret = ctypes.windll.shell32.ShellExecuteW(
                None, "open", exe, "-env=Live", folder, 1
            )
            # ShellExecuteW: 반환값 > 32 이면 성공
            return "ok" if ret > 32 else f"실행 실패 (코드 {ret})"
        except Exception as e:
            return str(e)

    # Windows 표시 언어 감지
    def get_windows_lang(self) -> str:
        import locale
        try:
            locale.setlocale(locale.LC_ALL, '')
            code = (locale.getlocale()[0] or "").lower()
        except Exception:
            code = ""
        if code.startswith("ko") or code.startswith("korean"):
            return "ko"
        if code.startswith("ja") or code.startswith("japanese"):
            return "ja"
        if "zh_tw" in code or "zh_hk" in code or "taiwan" in code:
            return "zh"
        return "en"

    # config.json 존재 여부 (첫 실행 감지용)
    def has_config(self) -> bool:
        return os.path.exists(CFG_PATH)

    # 앱 창을 전면으로 (캡처 완료 후 게임 창에서 포커스 탈환)
    def focus_window(self) -> None:
        try:
            import win32gui, win32con, win32api, win32process
            hwnd = win32gui.FindWindow(None, APP_TITLE)
            if not hwnd:
                return
            fg = win32gui.GetForegroundWindow()
            tid_fg, _ = win32process.GetWindowThreadProcessId(fg)
            tid_me    = win32api.GetCurrentThreadId()
            # AttachThreadInput으로 포커스 제한 우회
            ctypes.windll.user32.AttachThreadInput(tid_fg, tid_me, True)
            win32gui.BringWindowToTop(hwnd)
            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
            ctypes.windll.user32.SetForegroundWindow(hwnd)
            ctypes.windll.user32.AttachThreadInput(tid_fg, tid_me, False)
        except Exception:
            pass

    # 클립보드 복사 (clip.exe 사용 — pywebview 권한 제한 우회)
    def copy_to_clipboard(self, text: str):
        try:
            subprocess.run(
                "clip",
                input=text.encode("utf-16-le"),
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=0x08000000,  # CREATE_NO_WINDOW
            )
        except Exception:
            pass

    # 탐색기로 폴더 열기
    def open_folder(self, file_path: str):
        folder = os.path.dirname(file_path)
        subprocess.Popen(["explorer", folder])


# ── 앱 진입점 ──────────────────────────────────────────────────────────────
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    api = Api()
    app_html = os.path.join(WEB_DIR, "app.html")

    window = webview.create_window(
        title=APP_TITLE,
        url=app_html,
        js_api=api,
        width=760,
        height=680,
        min_size=(600, 500),
        resizable=True,
        background_color="#0f1117",
    )

    webview.start(
        debug=("--debug" in sys.argv),
        icon=ICON_PATH if os.path.exists(ICON_PATH) else None,
        storage_path=os.path.join(BASE_DIR, ".webview_data"),
    )


if __name__ == "__main__":
    main()
