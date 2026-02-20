"""
Decimal Equivalent Calculator
Tabs:
  1. Fraction → Decimal  – converts fractional inch measurements to decimals
  2. Inches → Millimeters – converts a decimal inch value to millimeters

Menu bar → Settings → "Minimize to system tray" controls tray behaviour.
The setting is persisted in %APPDATA%\DecimalConverter\settings.json.
"""

import json
import os
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from fractions import Fraction

import pystray
from PIL import Image, ImageDraw


# ── Version ───────────────────────────────────────────────────────────────────

try:
    APP_VERSION = (Path(__file__).parent / "version.txt").read_text().strip()
except OSError:
    APP_VERSION = "dev"


# ── Constants ─────────────────────────────────────────────────────────────────

INCHES_PER_MM = 1 / 25.4  # exact: 1 inch = 25.4 mm

SETTINGS_FILE = (
    Path(os.environ.get("APPDATA", Path.home())) / "DecimalConverter" / "settings.json"
)

# Common fractional inch sizes up to 64ths, in order
COMMON_FRACTIONS = sorted(set(
    Fraction(n, d)
    for d in [2, 4, 8, 16, 32, 64]
    for n in range(1, d)
    if Fraction(n, d).denominator == d  # only unreduced fractions
))


# ── Tray icon image ───────────────────────────────────────────────────────────

def _make_tray_image() -> Image.Image:
    """Draw a simple ruler icon for the system tray (64×64 px)."""
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([4, 20, 60, 44], radius=4, fill="#1a5fb4")
    for i, x in enumerate(range(8, 58, 7)):
        height = 10 if i % 2 == 0 else 6
        draw.line([(x, 20), (x, 20 + height)], fill="white", width=2)
    return img


# ── Application ───────────────────────────────────────────────────────────────

class DecimalConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"Decimal Equivalent Calculator v{APP_VERSION}")
        self.resizable(False, False)
        self._tray_icon: pystray.Icon | None = None

        # Settings state
        self.minimize_to_tray = tk.BooleanVar(value=self._load_setting("minimize_to_tray", True))
        self.minimal_ui = tk.BooleanVar(value=self._load_setting("minimal_ui", False))
        self._ref_frames: list[ttk.LabelFrame] = []

        self._build_menu()
        self._build_ui()
        self._apply_minimal_ui()

        self.bind("<Unmap>", self._on_unmap)
        self.protocol("WM_DELETE_WINDOW", self._quit_app)

    # ── Settings persistence ─────────────────────────────────────────────────

    def _load_setting(self, key: str, default):
        try:
            data = json.loads(SETTINGS_FILE.read_text())
            return data.get(key, default)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return default

    def _save_settings(self) -> None:
        try:
            SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
            SETTINGS_FILE.write_text(
                json.dumps({
                    "minimize_to_tray": self.minimize_to_tray.get(),
                    "minimal_ui": self.minimal_ui.get(),
                }, indent=2)
            )
        except OSError:
            pass  # silently ignore if the path isn't writable

    # ── Menu bar ─────────────────────────────────────────────────────────────

    def _build_menu(self) -> None:
        menubar = tk.Menu(self)

        settings_menu = tk.Menu(menubar, tearoff=False)
        settings_menu.add_checkbutton(
            label="Minimize to system tray",
            variable=self.minimize_to_tray,
            command=self._save_settings,
        )
        settings_menu.add_checkbutton(
            label="Minimal UI",
            variable=self.minimal_ui,
            command=self._on_minimal_ui_toggle,
        )
        menubar.add_cascade(label="Settings", menu=settings_menu)

        help_menu = tk.Menu(menubar, tearoff=False)
        help_menu.add_command(label="About", command=self._show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.config(menu=menubar)

    def _show_about(self) -> None:
        messagebox.showinfo(
            "About",
            f"Decimal Equivalent Calculator\nVersion {APP_VERSION}\n\nSimple tool by CodingAttempts",
        )

    def _on_minimal_ui_toggle(self) -> None:
        self._apply_minimal_ui()
        self._save_settings()

    def _apply_minimal_ui(self) -> None:
        if self.minimal_ui.get():
            for frame in self._ref_frames:
                frame.grid_remove()
        else:
            for frame in self._ref_frames:
                frame.grid()
        self.update_idletasks()
        self.geometry("")

    # ── System tray ──────────────────────────────────────────────────────────

    def _on_unmap(self, event: tk.Event) -> None:
        if event.widget is self and self.minimize_to_tray.get():
            self.withdraw()
            self._start_tray()

    def _start_tray(self) -> None:
        if self._tray_icon is not None:
            return
        menu = pystray.Menu(
            pystray.MenuItem("Restore", self._restore, default=True),
            pystray.MenuItem("Quit", self._quit_app),
        )
        self._tray_icon = pystray.Icon(
            "DecimalConverter", _make_tray_image(), "Decimal Convertor", menu
        )
        threading.Thread(target=self._tray_icon.run, daemon=True).start()

    def _restore(self, icon: pystray.Icon | None = None, item=None) -> None:
        if self._tray_icon:
            self._tray_icon.stop()
            self._tray_icon = None
        self.after(0, self.deiconify)

    def _quit_app(self, icon: pystray.Icon | None = None, item=None) -> None:
        if self._tray_icon:
            self._tray_icon.stop()
            self._tray_icon = None
        self.after(0, self.destroy)

    # ── UI ───────────────────────────────────────────────────────────────────

    def _build_ui(self):
        notebook = ttk.Notebook(self)
        notebook.grid(row=0, column=0, padx=10, pady=10)

        tab1 = ttk.Frame(notebook, padding=4)
        notebook.add(tab1, text="Fraction → Decimal")
        self._build_fraction_tab(tab1)

        tab2 = ttk.Frame(notebook, padding=4)
        notebook.add(tab2, text="Inches → Millimeters")
        self._build_inches_mm_tab(tab2)

        tab3 = ttk.Frame(notebook, padding=4)
        notebook.add(tab3, text="Millimeters → Inches")
        self._build_mm_inches_tab(tab3)

    # ── Tab 1: Fraction → Decimal ────────────────────────────────────────────

    def _build_fraction_tab(self, parent):
        pad = {"padx": 10, "pady": 6}

        calc_frame = ttk.LabelFrame(parent, text="Convert a Fraction")
        calc_frame.grid(row=0, column=0, sticky="ew", **pad)

        ttk.Label(calc_frame, text="Fraction:").grid(
            row=0, column=0, sticky="e", padx=(8, 4), pady=4
        )
        self.fraction_var = tk.StringVar()
        frac_entry = ttk.Entry(calc_frame, textvariable=self.fraction_var, width=10)
        frac_entry.grid(row=0, column=1, sticky="w", padx=(0, 4), pady=4)
        frac_entry.bind("<Return>", self._convert_fraction)
        ttk.Label(calc_frame, text="e.g.  3/8  or  7/16", foreground="gray").grid(
            row=0, column=2, sticky="w", padx=(2, 8)
        )

        ttk.Button(
            calc_frame, text="Convert", command=self._convert_fraction
        ).grid(row=1, column=0, columnspan=2, pady=(4, 8))

        ttk.Label(calc_frame, text="Decimal (in):").grid(
            row=2, column=0, sticky="e", padx=(8, 4), pady=4
        )
        self.frac_result_var = tk.StringVar(value="—")
        ttk.Label(
            calc_frame,
            textvariable=self.frac_result_var,
            font=("Courier", 14, "bold"),
            foreground="#1a5fb4",
            width=12,
        ).grid(row=2, column=1, sticky="w", padx=(0, 8), pady=4)

        self.frac_error_var = tk.StringVar()
        ttk.Label(
            calc_frame, textvariable=self.frac_error_var, foreground="red"
        ).grid(row=3, column=0, columnspan=2, pady=(0, 6))

        ref_frame = ttk.LabelFrame(parent, text="Common Fractions Reference")
        ref_frame.grid(row=1, column=0, sticky="nsew", **pad)
        self._ref_frames.append(ref_frame)

        columns = ("fraction", "decimal")
        tree = ttk.Treeview(
            ref_frame, columns=columns, show="headings", height=20, selectmode="browse"
        )
        tree.heading("fraction", text="Fraction (in)")
        tree.heading("decimal", text="Decimal (in)")
        tree.column("fraction", width=140, anchor="center")
        tree.column("decimal", width=140, anchor="center")

        scrollbar = ttk.Scrollbar(ref_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        for frac in COMMON_FRACTIONS:
            tree.insert("", "end", values=(str(frac), f"{float(frac):.6f}"))

        tree.bind("<<TreeviewSelect>>", lambda e: self._on_frac_row_select(tree))

        frac_entry.focus_set()

    def _on_frac_row_select(self, tree):
        selection = tree.selection()
        if not selection:
            return
        self.fraction_var.set(tree.item(selection[0], "values")[0])
        self._convert_fraction()

    def _convert_fraction(self, _event=None):
        self.frac_error_var.set("")
        try:
            frac = Fraction(self.fraction_var.get().strip())
        except (ValueError, ZeroDivisionError):
            self.frac_error_var.set("Enter a fraction like  3/8  or  7/16")
            self.frac_result_var.set("—")
            return

        if frac < 0:
            self.frac_error_var.set("Value must be positive.")
            self.frac_result_var.set("—")
            return

        self.frac_result_var.set(f"{float(frac):.6f}")

    # ── Tab 2: Inches → Millimeters ──────────────────────────────────────────

    def _build_inches_mm_tab(self, parent):
        pad = {"padx": 10, "pady": 6}

        calc_frame = ttk.LabelFrame(parent, text="Convert Inches to Millimeters")
        calc_frame.grid(row=0, column=0, sticky="ew", **pad)

        ttk.Label(calc_frame, text="Inches:").grid(
            row=0, column=0, sticky="e", padx=(8, 4), pady=4
        )
        self.inches_var = tk.StringVar()
        inches_entry = ttk.Entry(calc_frame, textvariable=self.inches_var, width=12)
        inches_entry.grid(row=0, column=1, sticky="w", padx=(0, 4), pady=4)
        inches_entry.bind("<Return>", self._convert_inches)
        ttk.Label(calc_frame, text='e.g.  3/8  or  1 3/8  or  0.375', foreground="gray").grid(
            row=0, column=2, sticky="w", padx=(2, 8)
        )

        ttk.Button(
            calc_frame, text="Convert", command=self._convert_inches
        ).grid(row=1, column=0, columnspan=2, pady=(4, 8))

        ttk.Label(calc_frame, text="Millimeters:").grid(
            row=2, column=0, sticky="e", padx=(8, 4), pady=4
        )
        self.mm_result_var = tk.StringVar(value="—")
        ttk.Label(
            calc_frame,
            textvariable=self.mm_result_var,
            font=("Courier", 14, "bold"),
            foreground="#1a5fb4",
            width=14,
        ).grid(row=2, column=1, sticky="w", padx=(0, 8), pady=4)

        self.inches_error_var = tk.StringVar()
        ttk.Label(
            calc_frame, textvariable=self.inches_error_var, foreground="red"
        ).grid(row=3, column=0, columnspan=2, pady=(0, 6))

        ref_frame = ttk.LabelFrame(parent, text="Common Conversions Reference")
        ref_frame.grid(row=1, column=0, sticky="nsew", **pad)
        self._ref_frames.append(ref_frame)

        columns = ("fraction", "inches", "mm")
        tree = ttk.Treeview(
            ref_frame, columns=columns, show="headings", height=20, selectmode="browse"
        )
        tree.heading("fraction", text="Fraction (in)")
        tree.heading("inches", text="Decimal (in)")
        tree.heading("mm", text="Millimeters")
        tree.column("fraction", width=110, anchor="center")
        tree.column("inches", width=110, anchor="center")
        tree.column("mm", width=110, anchor="center")

        scrollbar = ttk.Scrollbar(ref_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        for frac in COMMON_FRACTIONS:
            inch_val = float(frac)
            mm_val = inch_val * 25.4
            tree.insert(
                "", "end",
                values=(str(frac), f"{inch_val:.6f}", f"{mm_val:.4f}")
            )

        tree.bind("<<TreeviewSelect>>", lambda e: self._on_inches_row_select(tree))

        inches_entry.focus_set()

    def _on_inches_row_select(self, tree):
        selection = tree.selection()
        if not selection:
            return
        inch_str = tree.item(selection[0], "values")[1]  # decimal inches column
        self.inches_var.set(inch_str)
        self._convert_inches()

    def _convert_inches(self, _event=None):
        self.inches_error_var.set("")
        raw = self.inches_var.get().strip()

        try:
            parts = raw.split()
            if len(parts) == 2:
                # Mixed number: whole part + fraction, e.g. "1 3/8"
                inches = float(int(parts[0]) + Fraction(parts[1]))
            elif len(parts) == 1:
                # Plain decimal or fraction, e.g. "0.375" or "3/8"
                inches = float(Fraction(raw))
            else:
                raise ValueError
        except (ValueError, ZeroDivisionError):
            self.inches_error_var.set("Enter a value like  3/8,  1 3/8,  or  0.375")
            self.mm_result_var.set("—")
            return

        if inches < 0:
            self.inches_error_var.set("Value must be positive.")
            self.mm_result_var.set("—")
            return

        self.mm_result_var.set(f"{inches * 25.4:.4f}")

    # ── Tab 3: Millimeters → Inches ──────────────────────────────────────────

    def _build_mm_inches_tab(self, parent):
        pad = {"padx": 10, "pady": 6}

        calc_frame = ttk.LabelFrame(parent, text="Convert Millimeters to Inches")
        calc_frame.grid(row=0, column=0, sticky="ew", **pad)

        ttk.Label(calc_frame, text="Millimeters:").grid(
            row=0, column=0, sticky="e", padx=(8, 4), pady=4
        )
        self.mm_input_var = tk.StringVar()
        mm_entry = ttk.Entry(calc_frame, textvariable=self.mm_input_var, width=12)
        mm_entry.grid(row=0, column=1, sticky="w", padx=(0, 4), pady=4)
        mm_entry.bind("<Return>", self._convert_mm)
        ttk.Label(calc_frame, text="e.g.  25.4  or  9.525", foreground="gray").grid(
            row=0, column=2, sticky="w", padx=(2, 8)
        )

        ttk.Button(
            calc_frame, text="Convert", command=self._convert_mm
        ).grid(row=1, column=0, columnspan=2, pady=(4, 8))

        ttk.Label(calc_frame, text="Decimal (in):").grid(
            row=2, column=0, sticky="e", padx=(8, 4), pady=4
        )
        self.mm_to_in_result_var = tk.StringVar(value="—")
        ttk.Label(
            calc_frame,
            textvariable=self.mm_to_in_result_var,
            font=("Courier", 14, "bold"),
            foreground="#1a5fb4",
            width=14,
        ).grid(row=2, column=1, sticky="w", padx=(0, 8), pady=4)

        ttk.Label(calc_frame, text="Nearest fraction:").grid(
            row=3, column=0, sticky="e", padx=(8, 4), pady=4
        )
        self.mm_to_in_frac_var = tk.StringVar(value="—")
        ttk.Label(
            calc_frame,
            textvariable=self.mm_to_in_frac_var,
            font=("Courier", 14, "bold"),
            foreground="#1a5fb4",
            width=14,
        ).grid(row=3, column=1, sticky="w", padx=(0, 8), pady=4)

        self.mm_error_var = tk.StringVar()
        ttk.Label(
            calc_frame, textvariable=self.mm_error_var, foreground="red"
        ).grid(row=4, column=0, columnspan=2, pady=(0, 6))

        ref_frame = ttk.LabelFrame(parent, text="Common Conversions Reference")
        ref_frame.grid(row=1, column=0, sticky="nsew", **pad)
        self._ref_frames.append(ref_frame)

        columns = ("mm", "inches", "fraction")
        tree = ttk.Treeview(
            ref_frame, columns=columns, show="headings", height=20, selectmode="browse"
        )
        tree.heading("mm", text="Millimeters")
        tree.heading("inches", text="Decimal (in)")
        tree.heading("fraction", text="Fraction (in)")
        tree.column("mm", width=110, anchor="center")
        tree.column("inches", width=110, anchor="center")
        tree.column("fraction", width=110, anchor="center")

        scrollbar = ttk.Scrollbar(ref_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        for frac in COMMON_FRACTIONS:
            inch_val = float(frac)
            mm_val = inch_val * 25.4
            tree.insert(
                "", "end",
                values=(f"{mm_val:.4f}", f"{inch_val:.6f}", str(frac))
            )

        tree.bind("<<TreeviewSelect>>", lambda e: self._on_mm_row_select(tree))

        mm_entry.focus_set()

    def _on_mm_row_select(self, tree):
        selection = tree.selection()
        if not selection:
            return
        self.mm_input_var.set(tree.item(selection[0], "values")[0])  # mm column
        self._convert_mm()

    def _convert_mm(self, _event=None):
        self.mm_error_var.set("")
        try:
            mm = float(self.mm_input_var.get().strip())
        except ValueError:
            self.mm_error_var.set("Enter a numeric value in millimeters.")
            self.mm_to_in_result_var.set("—")
            self.mm_to_in_frac_var.set("—")
            return

        if mm < 0:
            self.mm_error_var.set("Value must be positive.")
            self.mm_to_in_result_var.set("—")
            self.mm_to_in_frac_var.set("—")
            return

        inches = mm / 25.4
        self.mm_to_in_result_var.set(f"{inches:.6f}")
        nearest = Fraction(inches).limit_denominator(64)
        whole = int(nearest)
        remainder = nearest - whole
        if whole == 0:
            frac_str = str(remainder)
        elif remainder == 0:
            frac_str = str(whole)
        else:
            frac_str = f"{whole} {remainder}"
        self.mm_to_in_frac_var.set(frac_str)


if __name__ == "__main__":
    app = DecimalConverterApp()
    app.mainloop()
