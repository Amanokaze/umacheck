# UmaCheck (烏馬檢查)

自動截圖賽馬娘圈子成員的粉絲數列表，並使用 Gemini AI 擷取數值的 Windows 桌面應用程式。

> 製作者: 선두의경치 (韓國伺服器) · v0.1.1

**其他語言:** [한국어](README.md) · [English](README_EN.md) · [日本語](README_JA.md)

---

## 主要功能

### 截圖
- 自動偵測正在執行的賽馬娘遊戲視窗
- 自動滾動圈子資訊畫面並連續截圖
- 自動去除重疊區域，將所有截圖合成為一張長圖
- 將結果儲存為 PNG 至 `output/` 資料夾

### 分析
- 使用 Gemini API 自動從截圖中擷取粉絲數數值
- 支援模型：`gemini-2.5-flash`（推薦）、`gemini-2.0-flash`、`gemini-2.0-flash-lite`、`gemini-2.5-pro`
- 可選擇自動移除連續重複數值
- 支援將結果複製到剪貼簿
- 支援圖片拖放或檔案選擇

### 設定
- 設定遊戲安裝資料夾路徑
- 調整滾動間隔、滾動量、相似度閾值

### 其他
- 可直接從應用程式啟動遊戲
- 多語言支援：한국어 / English / 日本語 / 繁體中文

---

## 系統需求

- **作業系統:** Windows 10 / 11
- **Python:** 3.12 以上
- **遊戲:** 賽馬娘 Pretty Derby（KakaoGames 韓國伺服器）
- **Gemini API Key:** 至 [Google AI Studio](https://aistudio.google.com/apikey) 免費取得

---

## 安裝與執行

```bash
# 安裝相依套件
pip install -r requirements.txt

# 執行應用程式
python main.py
```

以除錯模式執行：

```bash
python main.py --debug
```

---

## 使用方式

1. 首次啟動時會顯示**初始設定視窗**。
   - 輸入遊戲安裝資料夾（含有 `UMMS_Launcher.exe` 的路徑）。
   - 輸入 Gemini API Key。

2. 切換至**截圖**頁籤。
   - 啟動賽馬娘並前往 **圈子選單 → 圈子資訊** 畫面。
   - 將粉絲數列表滾動至**最頂端**，然後按下 **[開始截圖]**。
   - 應用程式會自動滾動並截圖，完成後合成圖片。

3. 切換至**分析**頁籤。
   - 截圖完成後會自動切換，或手動拖放圖片。
   - 選擇 Gemini 模型並按下 **[Extract]**。
   - 確認擷取的粉絲數列表，並複製至剪貼簿。

---

## 設定項目

| 項目 | 預設值 | 說明 |
|------|--------|------|
| 遊戲資料夾 | `C:\kakaogames\umamusume` | 含有 UMMS_Launcher.exe 的資料夾 |
| 滾動間隔 | `1.0` 秒 | 滾動後至下次截圖的等待時間（低規格 PC 請調高） |
| 滾動強度 | `6` | 每次滾動的格數 |
| 相似度閾值 | `99.5%` | 超過此值則判定為已滾動至底部 |

---

## 相依套件

| 套件 | 用途 |
|------|------|
| `pywebview` | 桌面應用程式 UI（HTML/JS 渲染） |
| `pyautogui` | 截圖擷取 |
| `Pillow` | 圖片處理與合成 |
| `pywin32` | Windows API（視窗控制、焦點） |
| `numpy` | 圖片相似度計算 |
| `psutil` | 遊戲程序偵測 |

---

## 注意事項

- 本應用程式**僅支援 Windows**，無法在 macOS 或 Linux 上執行。
- 截圖過程中請勿移動滑鼠，應用程式會自動控制。
- Gemini API Key 儲存於 `config.json`，請勿將此檔案公開分享。
- Gemini API 免費方案有使用量限制，分析大型圖片時建議使用 `gemini-2.5-flash`。

---

## 專案結構

```
uma-fancheck-app/
├── main.py          # 應用程式進入點、pywebview API 定義
├── config.json      # 使用者設定（自動產生）
├── requirements.txt # 相依套件清單
├── icon.png         # 應用程式圖示
├── src/
│   ├── capture.py   # 遊戲視窗偵測與自動截圖
│   └── stitch.py    # 重疊去除與圖片合成
├── web/
│   └── app.html     # 應用程式 UI（HTML/CSS/JS）
└── output/          # 截圖結果儲存資料夾
```
