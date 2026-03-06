# UmaCheck

A Windows desktop app that automatically captures the fan count list of Uma Musume circle members and extracts the numbers using Gemini AI.

> Creator: 선두의경치 (Korean Server) · v0.1.1

**Other languages:** [한국어](README.md) · [日本語](README_JA.md) · [繁體中文](README_ZH.md)

---

## Features

### Capture
- Automatically detects the running Uma Musume game window
- Auto-scrolls through the circle info screen and captures screenshots
- Removes overlapping areas and stitches all frames into a single long image
- Saves the result as a PNG file in the `output/` folder

### Analyze
- Uses the Gemini API to automatically extract fan count numbers from the captured image
- Supported models: `gemini-2.5-flash` (recommended), `gemini-2.0-flash`, `gemini-2.0-flash-lite`, `gemini-2.5-pro`
- Option to automatically remove consecutive duplicate numbers
- Copy results to clipboard
- Supports image drag-and-drop or file selection

### Settings
- Set the game installation folder path
- Adjust scroll delay, scroll amount, and similarity threshold

### Other
- Launch the game directly from the app
- Multilingual support: Korean / English / Japanese / Traditional Chinese

---

## Requirements

- **OS:** Windows 10 / 11
- **Python:** 3.12 or later
- **Game:** Uma Musume Pretty Derby (KakaoGames Korean Server)
- **Gemini API Key:** Get a free key at [Google AI Studio](https://aistudio.google.com/apikey)

---

## Installation & Launch

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

To run in debug mode:

```bash
python main.py --debug
```

---

## How to Use

1. On first launch, an **initial setup modal** will appear.
   - Enter your game installation folder (the path containing `UMMS_Launcher.exe`).
   - Enter your Gemini API Key.

2. Go to the **Capture** tab.
   - Launch Uma Musume and navigate to **Circle Menu → Circle Info**.
   - Scroll the fan count list to the **very top**, then click **[Start Capture]**.
   - The app will auto-scroll and capture the screen, then stitch the images together.

3. Go to the **Analyze** tab.
   - The app navigates here automatically after capture, or you can drag and drop an image manually.
   - Select a Gemini model and click **[Extract]**.
   - Review the extracted fan count list and copy it to the clipboard.

---

## Settings Reference

| Setting | Default | Description |
|---------|---------|-------------|
| Game Folder | `C:\kakaogames\umamusume` | Folder containing UMMS_Launcher.exe |
| Scroll Delay | `1.0` sec | Wait time between scroll and next capture (increase for slow PCs) |
| Scroll Amount | `6` | Number of scroll notches per step |
| Similarity Threshold | `99.5%` | Frames above this similarity are treated as end-of-scroll |

---

## Dependencies

| Library | Purpose |
|---------|---------|
| `pywebview` | Desktop app UI (HTML/JS rendering) |
| `pyautogui` | Screenshot capture |
| `Pillow` | Image processing and stitching |
| `pywin32` | Windows API (window control, focus) |
| `numpy` | Image similarity calculation |
| `psutil` | Game process detection |

---

## Notes

- This app is **Windows only**. It does not run on macOS or Linux.
- Do not move the mouse during capture — the app controls it automatically.
- Your Gemini API Key is stored in `config.json`. Do not share this file publicly.
- The Gemini API free tier has usage limits. For large images, `gemini-2.5-flash` is recommended.

---

## Project Structure

```
uma-fancheck-app/
├── main.py          # App entry point, pywebview API definitions
├── config.json      # User settings (auto-generated)
├── requirements.txt # Dependency list
├── icon.png         # App icon
├── src/
│   ├── capture.py   # Game window detection and auto capture
│   └── stitch.py    # Overlap removal and image stitching
├── web/
│   └── app.html     # App UI (HTML/CSS/JS)
└── output/          # Captured image output folder
```
