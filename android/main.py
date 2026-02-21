"""
Decimal Equivalent Calculator — Android / Kivy edition

Three-tab measurement converter:
  1. Fraction → Decimal     — fractional inches to decimal inches
  2. Inches → Millimeters   — decimal/fractional inches to mm
  3. Millimeters → Inches   — mm to decimal inches + nearest fraction

Build for Android with Buildozer (from this directory):
    pip install buildozer cython
    buildozer android debug
"""
from __future__ import annotations

from fractions import Fraction

from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.textinput import TextInput

# ── Constants ─────────────────────────────────────────────────────────────────

MM_PER_INCH: float = 25.4
APP_VERSION = "1.0.0"

# All unique reduced fractions with denominators 2, 4, 8, 16, 32, 64 — sorted
COMMON_FRACTIONS: list[Fraction] = sorted(set(
    Fraction(n, d)
    for d in [2, 4, 8, 16, 32, 64]
    for n in range(1, d)
    if Fraction(n, d).denominator == d
))

# Pre-computed reference table rows (avoids repeated computation at runtime)
_FRAC_ROWS   = [(str(f), f"{float(f):.6f}") for f in COMMON_FRACTIONS]
_INCHES_ROWS = [(str(f), f"{float(f):.6f}", f"{float(f) * MM_PER_INCH:.4f}") for f in COMMON_FRACTIONS]
_MM_ROWS     = [(f"{float(f) * MM_PER_INCH:.4f}", f"{float(f):.6f}", str(f)) for f in COMMON_FRACTIONS]

# ── Colours (r, g, b, a) ──────────────────────────────────────────────────────

_C_ACCENT = (0.102, 0.373, 0.706, 1)   # #1a5fb4
_C_HDR    = (0.15,  0.42,  0.75,  1)   # table column headers
_C_EVEN   = (0.97,  0.97,  0.97,  1)   # even table rows
_C_ODD    = (0.90,  0.93,  0.97,  1)   # odd table rows
_C_WHITE  = (1,     1,     1,     1)
_C_TEXT   = (0.10,  0.10,  0.10,  1)
_C_RED    = (0.75,  0.10,  0.10,  1)
_C_GRAY   = (0.50,  0.50,  0.50,  1)

# ── KV style rules ────────────────────────────────────────────────────────────

Builder.load_string("""
#:import dp kivy.metrics.dp

<_ConvertButton@Button>:
    size_hint: 1, None
    height: dp(52)
    font_size: dp(17)
    bold: True
    background_normal: ''
    background_color: 0.102, 0.373, 0.706, 1
    color: 1, 1, 1, 1

<_CalcInput@TextInput>:
    size_hint: 1, None
    height: dp(52)
    font_size: dp(19)
    multiline: False
    padding: dp(12), dp(14), dp(12), dp(14)

<_ResultLabel@Label>:
    size_hint: 1, None
    height: dp(52)
    font_size: dp(26)
    bold: True
    color: 0.102, 0.373, 0.706, 1
    halign: 'center'
    valign: 'middle'

<_SmallLabel@Label>:
    size_hint: 1, None
    height: dp(22)
    font_size: dp(13)
    halign: 'left'
    valign: 'middle'

<_ErrorLabel@Label>:
    size_hint: 1, None
    height: dp(26)
    font_size: dp(13)
    color: 0.75, 0.1, 0.1, 1
""")


# ── Widget helpers ────────────────────────────────────────────────────────────

def _attach_bg(widget, color: tuple) -> Rectangle:
    """Draw a solid background rectangle on *widget* and keep it synced."""
    with widget.canvas.before:
        Color(*color)
        rect = Rectangle(size=widget.size, pos=widget.pos)
    widget.bind(
        size=lambda _, v: setattr(rect, 'size', v),
        pos=lambda _, v: setattr(rect, 'pos', v),
    )
    return rect


def _section_header(text: str) -> Label:
    """Accent-coloured section header label."""
    lbl = Label(
        text=f"  {text}",
        size_hint=(1, None),
        height=dp(34),
        bold=True,
        font_size=dp(14),
        color=_C_WHITE,
        halign="left",
        valign="middle",
    )
    lbl.bind(size=lbl.setter("text_size"))
    _attach_bg(lbl, _C_ACCENT)
    return lbl


def _ref_table(col_headers: list[str], rows: list[tuple], on_select) -> ScrollView:
    """
    Scrollable reference table.

    Each data row is a set of Buttons — clicking any cell in a row calls
    on_select(row_tuple).
    """
    sv = ScrollView(size_hint=(1, 1))

    grid = GridLayout(cols=len(col_headers), size_hint_y=None, spacing=0, padding=0)
    grid.bind(minimum_height=grid.setter("height"))

    # ── Header row ──────────────────────────────────────────────────────────
    for h in col_headers:
        lbl = Label(
            text=h,
            size_hint_y=None,
            height=dp(36),
            bold=True,
            font_size=dp(12),
            color=_C_WHITE,
            halign="center",
            valign="middle",
        )
        lbl.bind(size=lbl.setter("text_size"))
        _attach_bg(lbl, _C_HDR)
        grid.add_widget(lbl)

    # ── Data rows ────────────────────────────────────────────────────────────
    for i, row in enumerate(rows):
        bg = _C_EVEN if i % 2 == 0 else _C_ODD
        for cell in row:
            btn = Button(
                text=cell,
                size_hint_y=None,
                height=dp(36),
                background_normal="",
                background_color=bg,
                background_down="",
                color=_C_TEXT,
                font_size=dp(13),
                halign="center",
                valign="middle",
            )
            # Clicking any cell in a row delivers the full row to the callback
            btn.bind(on_release=lambda b, r=row: on_select(r))
            grid.add_widget(btn)

    sv.add_widget(grid)
    return sv


def _calc_label(text: str, color=_C_GRAY) -> Label:
    """Small field-name label used inside the calculator section."""
    lbl = Label(
        text=text,
        size_hint=(1, None),
        height=dp(22),
        font_size=dp(13),
        color=color,
        halign="left",
        valign="middle",
    )
    lbl.bind(size=lbl.setter("text_size"))
    return lbl


def _result_label() -> Label:
    lbl = Label(
        text="—",
        size_hint=(1, None),
        height=dp(52),
        font_size=dp(26),
        bold=True,
        color=_C_ACCENT,
        halign="center",
        valign="middle",
    )
    lbl.bind(size=lbl.setter("text_size"))
    return lbl


def _error_label() -> Label:
    return Label(
        text="",
        size_hint=(1, None),
        height=dp(26),
        font_size=dp(13),
        color=_C_RED,
    )


def _convert_button(text: str = "Convert") -> Button:
    return Button(
        text=text,
        size_hint=(1, None),
        height=dp(52),
        font_size=dp(17),
        bold=True,
        background_normal="",
        background_color=_C_ACCENT,
        color=_C_WHITE,
    )


def _text_input(hint: str) -> TextInput:
    return TextInput(
        hint_text=hint,
        size_hint=(1, None),
        height=dp(52),
        font_size=dp(19),
        multiline=False,
        padding=(dp(12), dp(14), dp(12), dp(14)),
    )


def _calc_section(*children, height_dp: int) -> BoxLayout:
    """Wrapper BoxLayout for the calculator portion of a tab."""
    box = BoxLayout(
        orientation="vertical",
        size_hint=(1, None),
        height=dp(height_dp),
        padding=(dp(12), dp(8), dp(12), dp(8)),
        spacing=dp(6),
    )
    for child in children:
        box.add_widget(child)
    return box


# ── Tab 1: Fraction → Decimal ─────────────────────────────────────────────────

class FractionTab(BoxLayout):
    """Fraction → Decimal converter tab."""

    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=0, padding=0, **kwargs)

        self._entry = _text_input("e.g.  3/8  or  7/16")
        self._entry.bind(on_text_validate=lambda *_: self._convert())

        btn = _convert_button()
        btn.bind(on_release=lambda *_: self._convert())

        self._result = _result_label()
        self._error  = _error_label()

        calc = _calc_section(
            _calc_label("Fraction:"),
            self._entry,
            _calc_label("e.g.  3/8  or  7/16", _C_GRAY),
            btn,
            _calc_label("Decimal inches:"),
            self._result,
            self._error,
            height_dp=280,
        )

        self.add_widget(calc)
        self.add_widget(_section_header("Common Fractions Reference"))
        self.add_widget(_ref_table(
            ["Fraction (in)", "Decimal (in)"],
            _FRAC_ROWS,
            self._on_row_select,
        ))

    def _on_row_select(self, row: tuple) -> None:
        self._entry.text = row[0]
        self._convert()

    def _convert(self) -> None:
        self._error.text = ""
        try:
            frac = Fraction(self._entry.text.strip())
        except (ValueError, ZeroDivisionError):
            self._error.text = "Enter a fraction like  3/8  or  7/16"
            self._result.text = "—"
            return
        if frac < 0:
            self._error.text = "Value must be positive."
            self._result.text = "—"
            return
        self._result.text = f"{float(frac):.6f}"


# ── Tab 2: Inches → Millimeters ───────────────────────────────────────────────

class InchesMMTab(BoxLayout):
    """Inches → Millimeters converter tab."""

    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=0, padding=0, **kwargs)

        self._entry = _text_input("e.g.  3/8  or  1 3/8  or  0.375")
        self._entry.bind(on_text_validate=lambda *_: self._convert())

        btn = _convert_button()
        btn.bind(on_release=lambda *_: self._convert())

        self._result = _result_label()
        self._error  = _error_label()

        calc = _calc_section(
            _calc_label("Inches:"),
            self._entry,
            _calc_label("e.g.  3/8,  1 3/8,  or  0.375", _C_GRAY),
            btn,
            _calc_label("Millimeters:"),
            self._result,
            self._error,
            height_dp=280,
        )

        self.add_widget(calc)
        self.add_widget(_section_header("Common Conversions Reference"))
        self.add_widget(_ref_table(
            ["Fraction (in)", "Decimal (in)", "Millimeters"],
            _INCHES_ROWS,
            self._on_row_select,
        ))

    def _on_row_select(self, row: tuple) -> None:
        # row = (fraction_str, decimal_str, mm_str) — populate with decimal inches
        self._entry.text = row[1]
        self._convert()

    def _convert(self) -> None:
        self._error.text = ""
        raw = self._entry.text.strip()
        try:
            parts = raw.split()
            if len(parts) == 2:
                # Mixed number e.g. "1 3/8"
                inches = float(int(parts[0]) + Fraction(parts[1]))
            elif len(parts) == 1:
                # Plain decimal or bare fraction e.g. "0.375" or "3/8"
                inches = float(Fraction(raw))
            else:
                raise ValueError
        except (ValueError, ZeroDivisionError):
            self._error.text = "Enter a value like  3/8,  1 3/8,  or  0.375"
            self._result.text = "—"
            return
        if inches < 0:
            self._error.text = "Value must be positive."
            self._result.text = "—"
            return
        self._result.text = f"{inches * MM_PER_INCH:.4f}"


# ── Tab 3: Millimeters → Inches ───────────────────────────────────────────────

class MMInchesTab(BoxLayout):
    """Millimeters → Inches converter tab."""

    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=0, padding=0, **kwargs)

        self._entry = _text_input("e.g.  25.4  or  9.525")
        self._entry.bind(on_text_validate=lambda *_: self._convert())

        btn = _convert_button()
        btn.bind(on_release=lambda *_: self._convert())

        self._result_in   = _result_label()
        self._result_frac = Label(
            text="—",
            size_hint=(1, None),
            height=dp(40),
            font_size=dp(20),
            bold=True,
            color=_C_ACCENT,
            halign="center",
            valign="middle",
        )
        self._result_frac.bind(size=self._result_frac.setter("text_size"))
        self._error = _error_label()

        calc = _calc_section(
            _calc_label("Millimeters:"),
            self._entry,
            _calc_label("e.g.  25.4  or  9.525", _C_GRAY),
            btn,
            _calc_label("Decimal inches:"),
            self._result_in,
            _calc_label("Nearest fraction:"),
            self._result_frac,
            self._error,
            height_dp=360,
        )

        self.add_widget(calc)
        self.add_widget(_section_header("Common Conversions Reference"))
        self.add_widget(_ref_table(
            ["Millimeters", "Decimal (in)", "Fraction (in)"],
            _MM_ROWS,
            self._on_row_select,
        ))

    def _on_row_select(self, row: tuple) -> None:
        # row = (mm_str, decimal_str, fraction_str) — populate with mm value
        self._entry.text = row[0]
        self._convert()

    def _convert(self) -> None:
        self._error.text = ""
        try:
            mm = float(self._entry.text.strip())
        except ValueError:
            self._error.text = "Enter a numeric millimeter value."
            self._result_in.text = "—"
            self._result_frac.text = "—"
            return
        if mm < 0:
            self._error.text = "Value must be positive."
            self._result_in.text = "—"
            self._result_frac.text = "—"
            return

        inches = mm / MM_PER_INCH
        self._result_in.text = f"{inches:.6f}"

        nearest = Fraction(inches).limit_denominator(64)
        whole = int(nearest)
        remainder = nearest - whole
        if whole == 0:
            frac_str = str(remainder)
        elif remainder == 0:
            frac_str = str(whole)
        else:
            frac_str = f"{whole} {remainder}"
        self._result_frac.text = frac_str


# ── App ───────────────────────────────────────────────────────────────────────

class DecimalConverterApp(App):
    """Kivy application — builds the root TabbedPanel."""

    def build(self):
        self.title = f"Decimal Converter v{APP_VERSION}"

        panel = TabbedPanel(
            do_default_tab=False,
            tab_pos="top_mid",
            tab_height=dp(48),
        )

        for label, content_cls in [
            ("Frac → Dec", FractionTab),
            ("In → mm",   InchesMMTab),
            ("mm → In",   MMInchesTab),
        ]:
            item = TabbedPanelItem(text=label, font_size=dp(14))
            item.add_widget(content_cls())
            panel.add_widget(item)

        return panel


if __name__ == "__main__":
    DecimalConverterApp().run()
