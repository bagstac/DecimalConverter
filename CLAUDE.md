# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A small Python/Tkinter desktop app with three tabs:
1. **Fraction → Decimal** — converts fractional inch measurements (e.g., 7/16") to decimal inches
2. **Inches → Millimeters** — converts an inch value to millimeters (1 in = 25.4 mm exactly)
3. **Millimeters → Inches** — converts a millimeter value to decimal inches

Both tabs include a reference table of common fractions up to 64ths; clicking a row populates the calculator.

## Running the App

```bash
python decimal_convertor.py
```

Runtime dependencies (install once with `pip install -r requirements.txt`):
- `pystray` — system tray icon
- `Pillow` — draws the tray icon image

## Building a Windows Installer

Two-step process:

Run `build.bat` (double-click or from a terminal). It handles everything in order:
1. Installs/upgrades PyInstaller via pip
2. Builds `dist\DecimalConvertor.exe` (single standalone file, no console window)
3. Locates `ISCC.exe` (checks PATH then common Inno Setup install directories)
4. Compiles `installer.iss` and writes `installer_output\DecimalConvertorSetup.exe`

**Prerequisite:** [Inno Setup 6](https://jrsoftware.org/isinfo.php) must be installed before running the script.

The installer adds a Start Menu entry, an optional desktop shortcut, and a standard uninstaller.

## Architecture

Single-file application: [decimal_convertor.py](decimal_convertor.py)

- `COMMON_FRACTIONS` — module-level list of all unique reduced fractions up to 64ths, sorted; shared by both tabs.
- `DecimalConvertorApp(tk.Tk)` — the main window class.
  - `_build_menu()` — creates the menu bar (Settings → "Minimize to system tray" checkbutton).
  - `_build_ui()` — creates a `ttk.Notebook` and adds the two tab frames.
  - `_build_fraction_tab()` — builds the Fraction → Decimal UI (calculator + reference table).
  - `_build_inches_mm_tab()` — builds the Inches → Millimeters UI (calculator + reference table with fraction, decimal, and mm columns).
  - `_build_mm_inches_tab()` — builds the Millimeters → Inches UI (calculator + reference table with mm, decimal inches, and fraction columns).
  - `_convert_fraction()` / `_convert_inches()` — validate input and display results.
  - `_on_frac_row_select()` / `_on_inches_row_select()` — handle reference table row clicks.
  - `_load_setting()` / `_save_settings()` — read/write `%APPDATA%\DecimalConvertor\settings.json`.
  - `_on_unmap()` — intercepts minimize; sends to tray only when the setting is enabled.

## Key Conventions

- The app is intentionally kept as a single file; do not split into multiple modules unless the feature set grows significantly.
- Use `fractions.Fraction` for exact rational arithmetic when building the reference table.
- Fraction/decimal results display to 6 decimal places (`:.6f`); mm results display to 4 decimal places (`:.4f`).
- The conversion factor is `25.4` mm per inch (exact, defined by international agreement).
