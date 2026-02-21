# Decimal Converter — Android (Kivy)

A port of the Windows desktop app to Android using [Kivy](https://kivy.org/).
The conversion logic (`fractions`, math) is identical to the original; only the UI layer changes.

## Features

| Tab | Description |
|-----|-------------|
| **Frac → Dec** | Type a fraction (e.g. `3/8`) → decimal inches |
| **In → mm** | Type inches (decimal, fraction, or mixed like `1 3/8`) → millimeters |
| **mm → In** | Type millimeters → decimal inches + nearest 64th fraction |

Each tab includes a scrollable reference table of all common fractions up to 64ths. Tapping any row populates the calculator.

---

## Running on Desktop (for local testing)

```bash
cd android
pip install -r requirements.txt
python main.py
```

Requires Python 3.10+ and Kivy 2.3+.

---

## Building an Android APK

### Prerequisites

Buildozer runs on **Linux or macOS** (or WSL2 on Windows).
You will need:

| Tool | Notes |
|------|-------|
| Python 3.10+ | System Python or a venv |
| `buildozer` | `pip install buildozer` |
| `cython` | `pip install cython` |
| Java JDK 17 | e.g. `sudo apt install openjdk-17-jdk` |
| Android SDK/NDK | Downloaded automatically by Buildozer on first run |

### Build steps

```bash
# 1. Clone the repo and enter the android folder
cd android

# 2. Install build tools
pip install buildozer cython

# 3. Build a debug APK (first run takes ~20 min — downloads SDK/NDK automatically)
buildozer android debug

# 4. The APK is written to:  bin/decimalconverter-1.0.0-arm64-v8a_armeabi-v7a-debug.apk
```

### Deploy directly to a connected device

```bash
# Build, push, and launch in one step (device must be in USB debugging mode)
buildozer android debug deploy run

# Stream logcat output
buildozer android logcat
```

### Release build

```bash
buildozer android release
# Then sign the .aab with jarsigner / apksigner before submitting to the Play Store
```

---

## Project structure

```
android/
├── main.py          # Kivy app — all UI and conversion logic
├── buildozer.spec   # Build configuration (API levels, permissions, archs)
├── requirements.txt # Desktop-testing dependencies
└── README.md        # This file
```

## Android API targets

| Setting | Value | Notes |
|---------|-------|-------|
| `android.api` | 35 | Android 15 — required for new Play Store submissions |
| `android.minapi` | 26 | Android 8.0 Oreo minimum |
| `android.archs` | arm64-v8a, armeabi-v7a | 64-bit + legacy 32-bit ARM |

## Differences from the Windows desktop version

| Feature | Desktop | Android |
|---------|---------|---------|
| UI framework | Tkinter (ttk) | Kivy |
| System tray | Yes (pystray) | N/A |
| Minimize to tray | Settings toggle | N/A |
| Minimal UI mode | Settings toggle | N/A |
| Settings file | `%APPDATA%\DecimalConverter\settings.json` | Not implemented |
| Icon | DecimalConverter.png | Configurable via buildozer.spec |
