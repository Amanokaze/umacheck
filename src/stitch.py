"""
stitch.py - 캡처 이미지 세로 이어붙이기 모듈

스크롤 시 겹치는 영역을 자동으로 제거하고 이어붙입니다.
"""
import os
import time
import numpy as np
from PIL import Image

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")


def _find_overlap(img_above: Image.Image, img_below: Image.Image, search_height: int | None = None) -> int:
    """
    img_above 하단과 img_below 상단이 겹치는 픽셀 수를 반환합니다.
    겹치는 부분이 없으면 0을 반환합니다.

    search_height: None이면 프레임 높이의 80%를 자동 사용
    """
    w = min(img_above.width, img_below.width)
    a = np.array(img_above.convert("L"))  # grayscale
    b = np.array(img_below.convert("L"))

    h_above = a.shape[0]
    h_below = b.shape[0]

    if search_height is None:
        search_height = int(min(h_above, h_below) * 0.8)

    max_search = min(search_height, h_above, h_below)

    best_overlap = 0
    best_score = float("inf")

    for overlap in range(max_search, 4, -1):
        strip_a = a[h_above - overlap: h_above, :w].astype(np.int32)
        strip_b = b[0: overlap, :w].astype(np.int32)
        score = np.abs(strip_a - strip_b).mean()
        if score < best_score:
            best_score = score
            best_overlap = overlap
        # 완벽히 일치하면 즉시 반환
        if score < 1.0:
            return overlap

    # 임계값 강화: 멤버 행의 시각적 유사성으로 인한 가짜 겹침 방지
    if best_score > 3.0:
        return 0
    return best_overlap


def _find_next_row_start(arr: np.ndarray, max_search: int = 180) -> int:
    """
    arr 상단에서 max_search px 내 첫 행 구분선 이후 위치를 반환합니다.
    구분선 = 가로 전체가 균일한 밝은 색(회색/흰색) 라인.
    못 찾으면 0 반환 (추가 자르기 없음).
    """
    limit = min(max_search, arr.shape[0] - 2)
    # RGB → 근사 grayscale
    gray = arr[:limit].mean(axis=2)

    for y in range(2, limit):
        row = gray[y]
        # 균일하고 밝은 라인 = 구분선 후보
        if row.std() < 15 and row.mean() > 180:
            # 바로 다음 행에서 색 변화가 있으면 (내용 시작) → y+1이 행 시작
            if y + 1 < limit:
                next_row = gray[y + 1]
                if next_row.std() > 25 or abs(next_row.mean() - row.mean()) > 20:
                    return y + 1
    return 0


def stitch_frames(frames: list[Image.Image]) -> str:
    """
    프레임 리스트를 세로로 이어붙여 단일 이미지로 저장합니다.
    Returns: 저장된 파일의 절대 경로
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if len(frames) == 1:
        out_img = frames[0]
    else:
        # 첫 번째 프레임 기준 너비
        target_w = frames[0].width
        strips = [np.array(frames[0])]

        for i in range(1, len(frames)):
            prev = frames[i - 1]
            curr = frames[i]

            # 너비 통일
            if curr.width != target_w:
                curr = curr.resize((target_w, curr.height), Image.LANCZOS)

            overlap = _find_overlap(prev, curr)
            arr = np.array(curr)
            if overlap > 0:
                arr = arr[overlap:]  # 겹치는 상단 제거

            # overlap 제거 후 상단에 잘린 행이 남아 있으면 다음 행 경계까지 추가 제거
            extra = _find_next_row_start(arr)
            if extra > 0:
                arr = arr[extra:]

            strips.append(arr)

        combined = np.vstack(strips)
        out_img = Image.fromarray(combined)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"fancheck_{timestamp}.png"
    out_path = os.path.join(OUTPUT_DIR, filename)
    out_img.save(out_path, "PNG")
    return out_path
