# 우마체크 (UmaCheck)

우마무스메 서클원의 팬수 목록을 자동으로 캡처하고, Gemini AI로 숫자를 추출해주는 Windows 데스크탑 앱입니다.

> 제작자: 선두의경치 (한국서버) · v0.2.0

**다른 언어:** [English](README_EN.md) · [日本語](README_JA.md) · [繁體中文](README_ZH.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 주요 기능

### 캡처
- 실행 중인 우마무스메 창을 자동으로 감지
- 서클 정보 화면을 자동 스크롤하며 전체 스크린샷 수집
- 겹치는 영역을 자동으로 제거하고 하나의 긴 이미지로 합성
- 결과 이미지를 `output/` 폴더에 PNG로 저장

### 분석
- Gemini API를 이용해 캡처 이미지에서 팬수 숫자 자동 추출
- 지원 모델 (모두 무료 등급 사용 가능): `gemini-3.6-flash` (추천), `gemini-3.5-flash-lite`, `gemini-3.1-flash-lite`
- 연속 중복 숫자 자동 제거 옵션
- 결과를 클립보드로 복사 가능
- 이미지 드래그 앤 드롭 또는 파일 선택 지원

### 설정
- 게임 설치 폴더 경로 설정
- 스크롤 간격, 스크롤 강도, 유사도 임계값 조정

### 기타
- 앱 내에서 게임 직접 실행 가능
- 새 버전 자동 확인 및 앱 내 업데이트
- 한국어 / English / 日本語 / 繁體中文 다국어 지원

---

## 요구사항

- **OS:** Windows 10 / 11
- **Python:** 3.12 이상 (소스에서 직접 실행할 때만)
- **게임:** 우마무스메 프리티 더비 (카카오게임즈 한국 서버)
- **Gemini API Key:** [Google AI Studio](https://aistudio.google.com/apikey)에서 무료 발급

---

## 설치 및 실행

### 설치 파일로 설치 (일반 사용자)

1. [Releases 페이지](https://github.com/Amanokaze/umacheck/releases/latest)에서 `UmaCheck-Setup-vX.Y.Z.exe`를 내려받습니다.
2. 설치 파일을 실행합니다. 이전 버전이 설치돼 있으면 덮어쓰며, 설정과 API Key는 그대로 유지됩니다.
3. 시작 메뉴 또는 바탕화면의 **UmaCheck**로 실행합니다.

v0.2.0부터는 앱을 실행할 때 새 버전을 자동으로 확인합니다. 업데이트 창에서 **[업데이트]**를 누르면 새 버전을 내려받아 설치한 뒤 앱이 다시 실행됩니다. 정보(i) 창의 **[업데이트 확인]**으로 직접 확인할 수도 있습니다.

### 소스에서 실행 (개발자)

```bash
# 의존성 설치
pip install -r requirements.txt

# 앱 실행
python main.py
```

디버그 모드로 실행하려면:

```bash
python main.py --debug
```

---

## 사용 방법

1. 앱을 실행하면 **초기 설정 모달**이 나타납니다.
   - 게임 설치 폴더 (`UMMS_Launcher.exe`가 있는 경로) 를 입력합니다.
   - Gemini API Key를 입력합니다.

2. **캡처 탭**으로 이동합니다.
   - 우마무스메를 실행하고 **서클 메뉴 → 서클 정보** 화면으로 이동합니다.
   - 팬수 목록을 **맨 위**로 스크롤한 상태에서 **[캡처 시작]** 버튼을 누릅니다.
   - 앱이 자동으로 스크롤하며 화면을 캡처하고, 완료되면 이미지를 합성합니다.

3. **분석 탭**으로 이동합니다.
   - 캡처 완료 후 자동으로 이동하거나, 직접 이미지를 드래그 앤 드롭합니다.
   - Gemini 모델을 선택하고 **[Extract]** 버튼을 누릅니다.
   - 추출된 팬수 목록을 확인하고 클립보드로 복사합니다.

---

## 설정 항목

| 항목 | 기본값 | 설명 |
|------|--------|------|
| 게임 설치 폴더 | `C:\kakaogames\umamusume` | UMMS_Launcher.exe가 있는 폴더 |
| 스크롤 간격 | `1.0`초 | 스크롤 후 다음 캡처까지 대기 시간 (느린 PC는 높게 설정) |
| 스크롤 강도 | `6` | 한 번에 스크롤하는 칸 수 |
| 유사도 임계값 | `99.5%` | 이 값 이상이면 스크롤 끝으로 판단 |

---

## 의존 라이브러리

| 라이브러리 | 용도 |
|-----------|------|
| `pywebview` | 데스크탑 앱 UI (HTML/JS 렌더링) |
| `pyautogui` | 스크린샷 캡처 |
| `Pillow` | 이미지 처리 및 합성 |
| `pywin32` | Windows API (창 제어, 포커스) |
| `numpy` | 이미지 유사도 계산 |
| `psutil` | 게임 프로세스 감지 |

---

## 주의사항

- **Windows 전용** 앱입니다. macOS, Linux에서는 동작하지 않습니다.
- 캡처 중에는 마우스를 건드리지 마세요. 앱이 마우스를 자동 제어합니다.
- `config.json`에 Gemini API Key가 저장됩니다. 이 파일을 외부에 공유하지 마세요.
- Gemini API 무료 등급은 사용량 제한이 있습니다. 대용량 이미지 분석 시 `gemini-3.6-flash` 모델을 권장합니다.

---

## 프로젝트 구조

```
uma-fancheck-app/
├── main.py          # 앱 진입점, pywebview API 정의
├── config.json      # 사용자 설정 (자동 생성)
├── requirements.txt # 의존성 목록
├── icon.png         # 앱 아이콘
├── src/
│   ├── capture.py   # 게임 창 감지 및 자동 캡처
│   ├── stitch.py    # 이미지 겹침 제거 및 합성
│   ├── updater.py   # GitHub Releases 업데이트 확인·설치
│   └── version.py   # 앱 버전 (단일 관리)
├── web/
│   └── app.html     # 앱 UI (HTML/CSS/JS)
├── installer/
│   └── umacheck.iss # Inno Setup 설치 파일 스크립트
├── scripts/         # 빌드·릴리즈·업데이트 테스트 스크립트
├── .github/workflows/release.yml  # 태그 push 시 자동 빌드·릴리즈
└── output/          # 캡처 결과 이미지 저장 폴더
```

---

## 릴리즈 (개발자)

```powershell
# 버전 갱신 → 커밋 → 태그 → push
# 태그가 push되면 GitHub Actions가 설치 파일을 빌드해 Releases에 등록합니다.
.\scripts\release.ps1 -Version 0.3.0 -Notes "변경 사항"

# 릴리즈 전에 로컬에서 업데이트 기능 테스트 (GitHub에 올리지 않음)
.\scripts\test_update.ps1
```

- 릴리즈 노트(`-Notes`)는 앱의 업데이트 창에 일반 텍스트로 그대로 표시됩니다.
- 스크립트 실행이 차단되면 `powershell -ExecutionPolicy Bypass -File .\scripts\release.ps1 -Version ...` 형식으로 실행하세요.

---

## 기여 및 문의

이 프로젝트는 오픈소스입니다. 버그 제보, 기능 제안, Pull Request 모두 환영합니다.

- **버그 제보 / 기능 제안:** [GitHub Issues](https://github.com/Amanokaze/umacheck/issues)

---

## 라이선스

이 프로젝트는 [MIT License](LICENSE) 하에 배포됩니다.
