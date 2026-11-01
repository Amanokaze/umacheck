# UmaCheck

A Windows desktop app that automatically captures the fan count list of Uma Musume circle members and extracts the numbers using Gemini AI.

> Creator: 선두의경치 (Korean Server) · v0.2.1

**Other languages:** [한국어](README.md) · [日本語](README_JA.md) · [繁體中文](README_ZH.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Features

### Capture
- Automatically detects the running Uma Musume game window
- Auto-scrolls through the circle info screen and captures screenshots
- Removes overlapping areas and stitches all frames into a single long image
- Saves the result as a PNG file in the `output/` folder

### Analyze
- Uses the Gemini API to automatically extract fan count numbers from the captured image
- Supported models (all available on the free tier): `gemini-3.6-flash` (recommended), `gemini-3.5-flash-lite`, `gemini-3.1-flash-lite`
- Option to automatically remove consecutive duplicate numbers
- Copy results to clipboard
- Supports image drag-and-drop or file selection

### Settings
- Set the game installation folder path
- Adjust scroll delay, scroll amount, and similarity threshold

### Other
- Launch the game directly from the app
- Automatic update check and in-app update
- Multilingual support: Korean / English / Japanese / Traditional Chinese

---

## Requirements

- **OS:** Windows 10 / 11
- **Python:** 3.12 or later (only when running from source)
- **Game:** Uma Musume Pretty Derby (KakaoGames Korean Server)
- **Gemini API Key:** Get a free key at [Google AI Studio](https://aistudio.google.com/apikey)

---

## Installation & Launch

### Install with the installer (users)

1. Download `UmaCheck-Setup-vX.Y.Z.exe` from the [Releases page](https://github.com/Amanokaze/umacheck/releases/latest).
2. Run the installer. If a previous version is installed, it is overwritten and your settings and API Key are kept.
3. Launch **UmaCheck** from the Start menu or desktop.

Since v0.2.0, the app checks for a new version on startup. Click **[Update]** in the update dialog to download and install it; the app restarts afterwards. You can also check manually with **[Check for Updates]** in the About (i) dialog.

### Run from source (developers)

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
- The Gemini API free tier has usage limits. For large images, `gemini-3.6-flash` is recommended.

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
│   ├── stitch.py    # Overlap removal and image stitching
│   ├── updater.py   # Update check/install via GitHub Releases
│   └── version.py   # App version (single source)
├── web/
│   └── app.html     # App UI (HTML/CSS/JS)
├── installer/
│   └── umacheck.iss # Inno Setup installer script
├── scripts/         # Build, release, and update test scripts
├── .github/workflows/release.yml  # Auto build & release on tag push
└── output/          # Captured image output folder
```

---

## Release (developers)

```powershell
# Bump version -> commit -> tag -> push
# When the tag is pushed, GitHub Actions builds the installer and publishes it to Releases.
.\scripts\release.ps1 -Version 0.3.0 -Notes "What changed"

# Test the update feature locally before releasing (nothing is uploaded to GitHub)
.\scripts\test_update.ps1
```

- The release notes (`-Notes`) are shown as plain text in the app's update dialog.
- If script execution is blocked, run `powershell -ExecutionPolicy Bypass -File .\scripts\release.ps1 -Version ...`.

---

## Contributing & Support

This is an open-source project. Bug reports, feature requests, and pull requests are all welcome.

- **Bug reports / Feature requests:** [GitHub Issues](https://github.com/Amanokaze/umacheck/issues)

---

## License

This project is distributed under the [MIT License](LICENSE).
