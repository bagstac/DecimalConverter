[app]

# Application metadata
title = Decimal Converter
package.name = decimalconverter
package.domain = org.decimalconverter

# Source
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.exclude_dirs = tests, bin, venv, .venv, __pycache__

# Version (keep in sync with APP_VERSION in main.py)
version = 1.0.0

# Runtime requirements — fractions is stdlib, no extra packages needed
requirements = python3,kivy

# Application icon (place a square PNG here to use it)
# icon.filename = %(source.dir)s/icon.png

# Presplash screen (shown while app loads)
# presplash.filename = %(source.dir)s/presplash.png

# Supported orientations: portrait, landscape, or all
orientation = portrait

# Keep screen on while the app is open
# android.wakelock = False

# Fullscreen: 0 = show status bar, 1 = hide it
fullscreen = 0


# ── Android-specific settings ─────────────────────────────────────────────────

# Target API — 35 is Android 15 (required for new Play Store submissions in 2025+)
android.api = 35

# Minimum supported API — 26 = Android 8.0 Oreo
android.minapi = 26

# NDK version
android.ndk = 25b

# Accept the Android SDK licence automatically during build
android.accept_sdk_license = True

# Architecture(s) to build for.
# arm64-v8a  — modern 64-bit Android devices (recommended)
# armeabi-v7a — older 32-bit ARM devices
android.archs = arm64-v8a, armeabi-v7a

# Android permissions (none required for this app)
# android.permissions = INTERNET

# gradle extras (none required)
# android.gradle_dependencies =

# Enable AndroidX support
android.enable_androidx = True

# logcat filters for 'buildozer android logcat'
android.logcat_filters = *:S python:D


# ── iOS settings (not used) ───────────────────────────────────────────────────

[buildozer]

# Verbosity: 0 = quiet, 1 = normal, 2 = verbose
log_level = 2

# Warn if run as root
warn_on_root = 1

# Build directory (relative to this spec file)
# build_dir = ./.buildozer

# Compiled binaries output directory
# bin_dir = ./bin
