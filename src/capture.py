"""
capture.py - 우마무스메 서클원 팬수 화면 자동 캡처 모듈
"""
import time
import threading
import ctypes
import ctypes.wintypes
import numpy as np
import pyautogui
import win32gui
import win32con
import win32process
import psutil
from PIL import Image

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05

# DPI 인식 설정 (좌표 불일치 방지)
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

WHEEL_DELTA = 120  # Windows 표준: 마우스 휠 한 칸 = 120

# ── SendInput 구조체 정의 ──────────────────────────────────────────────────
_INPUT_MOUSE        = 0
_MOUSEEVENTF_MOVE   = 0x0001
_MOUSEEVENTF_WHEEL  = 0x0800
_MOUSEEVENTF_ABS    = 0x8000

class _MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx",          ctypes.wintypes.LONG),
        ("dy",          ctypes.wintypes.LONG),
        ("mouseData",   ctypes.wintypes.DWORD),
        ("dwFlags",     ctypes.wintypes.DWORD),
        ("time",        ctypes.wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.wintypes.ULONG)),
    ]

class _INPUT(ctypes.Structure):
    _fields_ = [("type", ctypes.wintypes.DWORD), ("mi", _MOUSEINPUT)]

_u32 = ctypes.windll.user32

def _move_cursor(x: int, y: int) -> bool:
    """마우스 커서 이동 — ctypes 직접 호출 (win32api 우회)"""
    # 방법 1: SetCursorPos 직접
    if _u32.SetCursorPos(x, y):
        return True
    # 방법 2: SendInput ABSOLUTE 이동
    sw = _u32.GetSystemMetrics(0) or 1
    sh = _u32.GetSystemMetrics(1) or 1
    ax = int(x * 65535 / sw)
    ay = int(y * 65535 / sh)
    inp = _INPUT(type=_INPUT_MOUSE,
                 mi=_MOUSEINPUT(dx=ax, dy=ay, mouseData=0,
                                dwFlags=_MOUSEEVENTF_MOVE | _MOUSEEVENTF_ABS,
                                time=0, dwExtraInfo=None))
    return bool(_u32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp)))

def _send_one_wheel(delta: int):
    """SendInput으로 마우스 휠 120 단위 1회 전송 (delta 음수 = 아래로)"""
    inp = _INPUT(type=_INPUT_MOUSE,
                 mi=_MOUSEINPUT(dx=0, dy=0, mouseData=ctypes.c_int(delta).value,
                                dwFlags=_MOUSEEVENTF_WHEEL, time=0, dwExtraInfo=None))
    _u32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

def _scroll(notches: int):
    """notches 만큼 휠 스크롤 — 음수 = 아래로, 120 단위씩 개별 전송"""
    per_tick = -WHEEL_DELTA if notches < 0 else WHEEL_DELTA
    for _ in range(abs(notches)):
        _send_one_wheel(per_tick)
        time.sleep(0.03)

GAME_EXE = "umamusume.exe"
SCROLL_AMOUNT = -5          # 휠 스크롤 한 칸 (음수 = 아래)
SCROLL_DELAY = 0.8          # 스크롤 후 대기 시간(초)
CAPTURE_DELAY = 0.3         # 캡처 전 대기 시간(초)
DIFF_THRESHOLD = 0.995      # 이미지 유사도 임계값 (1.0 = 완전히 동일)
MAX_CAPTURES = 200          # 무한루프 방지용 최대 캡처 수


def _find_window_by_exe(exe_name: str) -> int | None:
    """실행 중인 프로세스 이름으로 윈도우 핸들 반환"""
    target_pids = {
        p.pid for p in psutil.process_iter(['name'])
        if p.info['name'] and p.info['name'].lower() == exe_name.lower()
    }
    if not target_pids:
        return None

    result = []

    def _cb(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            if pid in target_pids and win32gui.GetWindowText(hwnd):
                result.append(hwnd)
        except Exception:
            pass

    win32gui.EnumWindows(_cb, None)
    return result[0] if result else None


def _get_window_rect(hwnd: int) -> tuple[int, int, int, int]:
    """윈도우 클라이언트 영역 좌표 반환 (left, top, right, bottom)"""
    return win32gui.GetWindowRect(hwnd)


def _capture_region(left: int, top: int, right: int, bottom: int) -> Image.Image:
    """지정 영역 스크린샷"""
    time.sleep(CAPTURE_DELAY)
    width = right - left
    height = bottom - top
    screenshot = pyautogui.screenshot(region=(left, top, width, height))
    return screenshot.convert("RGB")


def _image_similarity(img1: Image.Image, img2: Image.Image) -> float:
    """두 이미지의 픽셀 유사도 (0.0 ~ 1.0)"""
    if img1.size != img2.size:
        img2 = img2.resize(img1.size, Image.LANCZOS)
    a = np.array(img1, dtype=np.int32)
    b = np.array(img2, dtype=np.int32)
    diff = np.abs(a - b).mean()
    # diff=0 → 1.0, diff=255 → 0.0
    return 1.0 - (diff / 255.0)


def _set_foreground(hwnd: int):
    """Windows 10/11 제약을 우회해 강제로 창을 포그라운드로 올림"""
    try:
        cur_tid = ctypes.windll.kernel32.GetCurrentThreadId()
        tgt_tid, _ = win32process.GetWindowThreadProcessId(hwnd)
        if cur_tid != tgt_tid:
            win32process.AttachThreadInput(cur_tid, tgt_tid, True)
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        win32gui.BringWindowToTop(hwnd)
        if cur_tid != tgt_tid:
            win32process.AttachThreadInput(cur_tid, tgt_tid, False)
    except Exception:
        pass


def _focus_and_scroll(hwnd: int, cx: int, cy: int, notches: int):
    """창 포커스 후 마우스 이동 → 휠 스크롤
    notches: 음수 = 아래로 스크롤
    """
    _set_foreground(hwnd)
    time.sleep(0.2)

    # 마우스 이동 (ctypes 직접 / SendInput 폴백)
    _move_cursor(cx, cy)
    time.sleep(0.15)

    # 120 단위씩 개별 전송 (큰 delta 한방보다 게임이 더 잘 인식)
    _scroll(notches)


class Capturer:
    def __init__(self):
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def is_game_running(self) -> bool:
        return _find_window_by_exe(GAME_EXE) is not None

    def start(self, on_status, on_progress, on_done, on_error):
        """
        캡처를 별도 스레드에서 시작.

        콜백:
            on_status(msg: str)          - 상태 메시지
            on_progress(pct: int)        - 진행률 0~100
            on_done(image_path: str)     - 완성된 이미지 경로
            on_error(msg: str)           - 오류 메시지
        """
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run,
            args=(on_status, on_progress, on_done, on_error),
            daemon=True,
        )
        self._thread.start()

    def stop(self):
        self._stop_event.set()

    def _run(self, on_status, on_progress, on_done, on_error):
        try:
            on_status("우마무스메 창 탐색 중...")
            hwnd = _find_window_by_exe(GAME_EXE)
            if not hwnd:
                on_error("우마무스메가 실행 중이지 않습니다.")
                return

            left, top, right, bottom = _get_window_rect(hwnd)
            cx = (left + right) // 2
            # 스크롤 가능 영역: 화면 중앙에서 아래쪽 1/2 지점 (전체 높이의 75%)
            cy = top + int((bottom - top) * 0.75)

            on_status("창을 포커스합니다...")
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.5)

            frames: list[Image.Image] = []
            prev_img: Image.Image | None = None

            for i in range(MAX_CAPTURES):
                if self._stop_event.is_set():
                    on_status("캡처가 중단되었습니다.")
                    return

                # 스크린샷
                img = _capture_region(left, top, right, bottom)

                # 첫 캡처가 아닐 때 중복 검사
                if prev_img is not None:
                    sim = _image_similarity(prev_img, img)
                    if sim >= DIFF_THRESHOLD:
                        on_status(f"스크롤 끝 감지 (유사도 {sim:.4f}) — 이미지 합성 시작")
                        break

                frames.append(img)
                prev_img = img

                pct = min(90, int((i + 1) / MAX_CAPTURES * 90))
                on_progress(pct)
                on_status(f"캡처 {i + 1}장 완료, 스크롤 중...")

                # 스크롤
                _focus_and_scroll(hwnd, cx, cy, SCROLL_AMOUNT)
                time.sleep(SCROLL_DELAY)

            if not frames:
                on_error("캡처된 이미지가 없습니다.")
                return

            on_status("이미지 합성 중...")
            on_progress(92)

            from src.stitch import stitch_frames
            out_path = stitch_frames(frames)

            on_progress(100)
            on_done(out_path)

        except Exception as e:
            on_error(f"오류 발생: {e}")


# 싱글톤
capturer = Capturer()
