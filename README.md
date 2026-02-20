# Decimal Equivalent Calculator

A small Windows desktop utility for converting between fractional inches, decimal inches, and millimeters.

[![Latest Release](https://img.shields.io/github/v/release/bagstac/DecimalConverter?label=download&logo=windows)](https://github.com/bagstac/DecimalConverter/releases/latest)

## Download

👉 **[Download the latest installer](https://github.com/bagstac/DecimalConverter/releases/latest)** — grab `DecimalConvertorSetup.exe` from the Assets section.

## Features

- **Fraction → Decimal** — convert fractional inch measurements (e.g. `7/16`) to decimal inches
- **Inches → Millimeters** — convert decimal or fractional inches to millimeters
- **Millimeters → Inches** — convert millimeters to decimal inches with nearest fraction
- Reference table of common fractions up to 64ths on each tab (click a row to populate the calculator)
- **Minimal UI** mode — hide reference tables for a compact window (Settings menu)
- Minimize to system tray (Settings menu)

## Running from Source

```bash
pip install -r requirements.txt
python decimal_convertor.py
```

## Building Locally

Requires [Inno Setup 6](https://jrsoftware.org/isinfo.php) to be installed.

```bat
build.bat
```

Produces `installer_output\DecimalConvertorSetup.exe`.
