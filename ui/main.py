# =========================
# FILE: ui/main.py
# =========================

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.properties import StringProperty, BooleanProperty
from kivy.clock import Clock

import paradigms.procedural as procedural
import paradigms.functional as functional
import paradigms.event_driven as event_driven
from paradigms.oop_calculator import Calculator
from extras.additional_features import (
    exponentiate, square_root, percentage,
    get_history, clear_history
)

Window.size = (390, 780)

# ── Themes ───────────────────────────────────────────────────
DARK = {
    'bg':          '#1C2B3A',
    'display_bg':  '#152231',
    'btn_num':     '#243447',
    'btn_op':      '#F5A623',
    'btn_fn':      '#2E3F52',
    'btn_eq':      '#F5A623',
    'btn_ac':      '#2E3F52',
    'text_main':   '#FFFFFF',
    'text_expr':   '#7A8FA0',
    'text_op':     '#FFFFFF',
    'text_fn':     '#CBD8E3',
    'spinner_bg':  '#2E3F52',
    'spinner_text':'#CBD8E3',
    'toggle_bg':   '#2E3F52',
    'shadow':      (0, 0, 0, 0.4),
}
LIGHT = {
    'bg':          '#F0F4F8',
    'display_bg':  '#FFFFFF',
    'btn_num':     '#FFFFFF',
    'btn_op':      '#F5A623',
    'btn_fn':      '#DDE5EE',
    'btn_eq':      '#F5A623',
    'btn_ac':      '#DDE5EE',
    'text_main':   '#1C2B3A',
    'text_expr':   '#8899AA',
    'text_op':     '#FFFFFF',
    'text_fn':     '#3D5066',
    'spinner_bg':  '#FFFFFF',
    'spinner_text':'#1C2B3A',
    'toggle_bg':   '#DDE5EE',
    'shadow':      (0, 0, 0, 0.12),
}


def hex_rgba(h, a=1.0):
    c = get_color_from_hex(h)
    return (c[0], c[1], c[2], a)


class RoundButton(Button):
    def __init__(self, bg_hex='#243447', text_hex='#FFFFFF',
                 radius=18, font_size_val=22, **kwargs):
        super().__init__(**kwargs)
        self.bg_hex = bg_hex
        self.text_hex = text_hex
        self.radius_val = radius
        self.font_size = dp(font_size_val)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        self.color = hex_rgba(text_hex)
        self.bold = True
        self.bind(pos=self._redraw, size=self._redraw)
        self._redraw()

    def _redraw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            # Shadow
            Color(0, 0, 0, 0.18)
            RoundedRectangle(
                pos=(self.x + dp(2), self.y - dp(3)),
                size=(self.width, self.height),
                radius=[dp(self.radius_val)]
            )
            # Button face
            Color(*hex_rgba(self.bg_hex))
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(self.radius_val)]
            )

    def update_theme(self, bg_hex, text_hex='#FFFFFF'):
        self.bg_hex = bg_hex
        self.text_hex = text_hex
        self.color = hex_rgba(text_hex)
        self._redraw()


class DisplayPanel(BoxLayout):
    def __init__(self, theme, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.theme = theme
        self.padding = [dp(24), dp(16), dp(24), dp(16)]
        self.spacing = dp(4)

        self.expr_label = Label(
            text='',
            font_size=dp(17),
            halign='right',
            valign='middle',
            size_hint=(1, 0.35),
            color=hex_rgba(theme['text_expr'])
        )
        self.expr_label.bind(size=lambda *_: setattr(
            self.expr_label, 'text_size', (self.expr_label.width, None)))

        self.result_label = Label(
            text='0',
            font_size=dp(52),
            halign='right',
            valign='middle',
            size_hint=(1, 0.65),
            bold=True,
            color=hex_rgba(theme['text_main'])
        )
        self.result_label.bind(size=lambda *_: setattr(
            self.result_label, 'text_size', (self.result_label.width, None)))

        self.add_widget(self.expr_label)
        self.add_widget(self.result_label)

        self.bind(pos=self._redraw, size=self._redraw)
        self._redraw()

    def _redraw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*hex_rgba(self.theme['display_bg']))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(20)])

    def update_theme(self, theme):
        self.theme = theme
        self.expr_label.color = hex_rgba(theme['text_expr'])
        self.result_label.color = hex_rgba(theme['text_main'])
        self._redraw()


class SmartCalculatorUI(BoxLayout):
    dark_mode = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.padding = dp(16)
        self.spacing = dp(10)
        self.expression = ''
        self.just_result = False
        self._oop_calc = Calculator()
        self.theme = DARK

        self._build_ui()
        self._apply_theme()

    def _build_ui(self):
        # ── Top bar: paradigm spinner + theme toggle ──────────
        top_bar = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.07),
            spacing=dp(10)
        )

        self.paradigm_spinner = Spinner(
            text='Procedural',
            values=['Procedural', 'OOP', 'Functional', 'Event-Driven', 'Extended'],
            size_hint=(0.72, 1),
            font_size=dp(14),
            background_normal='',
            background_color=hex_rgba(self.theme['spinner_bg']),
            color=hex_rgba(self.theme['spinner_text']),
        )

        self.theme_btn = RoundButton(
            text='☀',
            bg_hex=self.theme['toggle_bg'],
            text_hex=self.theme['text_fn'],
            font_size_val=18,
            size_hint=(0.28, 1),
        )
        self.theme_btn.bind(on_press=self._toggle_theme)

        top_bar.add_widget(self.paradigm_spinner)
        top_bar.add_widget(self.theme_btn)
        self.add_widget(top_bar)

        # ── Display panel ─────────────────────────────────────
        self.display = DisplayPanel(self.theme, size_hint=(1, 0.22))
        self.add_widget(self.display)

        # ── Buttons ───────────────────────────────────────────
        btn_area = BoxLayout(orientation='vertical',
                             size_hint=(1, 0.71),
                             spacing=dp(10))

        # Row: AC, +/-, %, /
        row1 = self._make_row([
            ('AC',  'fn'),
            ('+/-', 'fn'),
            ('√',   'fn'),
            ('/',   'op'),
        ])
        # Row: 7, 8, 9, ×
        row2 = self._make_row([
            ('7', 'num'), ('8', 'num'), ('9', 'num'), ('×', 'op'),
        ])
        # Row: 4, 5, 6, −
        row3 = self._make_row([
            ('4', 'num'), ('5', 'num'), ('6', 'num'), ('−', 'op'),
        ])
        # Row: 1, 2, 3, +
        row4 = self._make_row([
            ('1', 'num'), ('2', 'num'), ('3', 'num'), ('+', 'op'),
        ])
        # Row: ^, 0, ., =
        row5 = self._make_row([
            ('^', 'fn'), ('0', 'num'), ('.', 'num'), ('=', 'eq'),
        ])

        for row in [row1, row2, row3, row4, row5]:
            btn_area.add_widget(row)

        self.add_widget(btn_area)

        # Store all button widgets for theme updates
        self._all_rows = [row1, row2, row3, row4, row5]

    def _make_row(self, specs):
        row = BoxLayout(orientation='horizontal', spacing=dp(10))
        for label, kind in specs:
            btn = self._create_btn(label, kind)
            row.add_widget(btn)
        return row

    def _create_btn(self, label, kind):
        t = self.theme
        if kind == 'num':
            bg = t['btn_num'];   fg = t['text_main']
        elif kind == 'op':
            bg = t['btn_op'];    fg = t['text_op']
        elif kind == 'fn':
            bg = t['btn_fn'];    fg = t['text_fn']
        elif kind == 'eq':
            bg = t['btn_eq'];    fg = t['text_op']
        else:
            bg = t['btn_num'];   fg = t['text_main']

        btn = RoundButton(
            text=label,
            bg_hex=bg,
            text_hex=fg,
            font_size_val=22,
            size_hint=(1, 1),
        )
        btn.bind(on_press=lambda b: self._on_button(b.text))
        return btn

    # ── Theme ─────────────────────────────────────────────────
    def _toggle_theme(self, *_):
        self.dark_mode = not self.dark_mode
        self.theme = DARK if self.dark_mode else LIGHT
        self.theme_btn.text = '☀' if self.dark_mode else '🌙'
        self._apply_theme()

    def _apply_theme(self):
        t = self.theme
        # Root bg
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*hex_rgba(t['bg']))
            Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._redraw_bg, size=self._redraw_bg)

        # Display
        self.display.update_theme(t)

        # Spinner
        self.paradigm_spinner.background_color = hex_rgba(t['spinner_bg'])
        self.paradigm_spinner.color = hex_rgba(t['spinner_text'])

        # Buttons - re-color by kind
        kind_map = {
            'AC': 'fn', '+/-': 'fn', '√': 'fn', '^': 'fn',
            '/': 'op', '×': 'op', '−': 'op', '+': 'op',
            '=': 'eq',
        }
        for row in self._all_rows:
            for btn in row.children:
                if isinstance(btn, RoundButton):
                    lbl = btn.text
                    kind = kind_map.get(lbl, 'num')
                    if kind == 'num':
                        btn.update_theme(t['btn_num'], t['text_main'])
                    elif kind == 'op':
                        btn.update_theme(t['btn_op'], t['text_op'])
                    elif kind == 'fn':
                        btn.update_theme(t['btn_fn'], t['text_fn'])
                    elif kind == 'eq':
                        btn.update_theme(t['btn_eq'], t['text_op'])

        self.theme_btn.update_theme(t['toggle_bg'], t['text_fn'])

    def _redraw_bg(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*hex_rgba(self.theme['bg']))
            Rectangle(pos=self.pos, size=self.size)

    # ── Button logic ──────────────────────────────────────────
    def _on_button(self, key):
        if key == 'AC':
            self.expression = ''
            self.just_result = False
            self.display.result_label.text = '0'
            self.display.expr_label.text = ''
            return

        if key == '=':
            self._evaluate()
            return

        if key == '+/-':
            if self.expression:
                if self.expression.startswith('-'):
                    self.expression = self.expression[1:]
                else:
                    self.expression = '-' + self.expression
                self.display.result_label.text = self.expression
            return

        # Map display symbols to expression symbols
        sym_map = {'×': '*', '−': '-'}
        sym = sym_map.get(key, key)

        if self.just_result:
            # If last was a result and user taps a number, start fresh
            if sym.isdigit() or sym == '.':
                self.expression = sym
            else:
                # Continue with result as operand
                self.expression = self.display.result_label.text + ' ' + sym + ' '
            self.just_result = False
        else:
            if sym in ('+', '-', '*', '/', '%', '^'):
                self.expression = self.expression.rstrip() + ' ' + sym + ' '
            else:
                self.expression += sym

        self.display.result_label.text = self.expression.strip() or '0'
        self.display.expr_label.text = ''

    def _evaluate(self):
        expr = self.expression.strip()
        if not expr:
            return

        paradigm = self.paradigm_spinner.text
        self.display.expr_label.text = expr

        try:
            result = self._dispatch(paradigm, expr)
            # Format nicely
            if isinstance(result, float) and result == int(result):
                display_result = str(int(result))
            else:
                display_result = f'{result:.6g}'

            self.display.result_label.text = display_result
            self.expression = display_result
            self.just_result = True

        except Exception as e:
            self.display.result_label.text = 'Error'
            self.display.expr_label.text = str(e)
            self.expression = ''
            self.just_result = False

    def _dispatch(self, paradigm: str, expr: str) -> float:
        # Handle special single-operand operations
        parts = expr.split()
        if len(parts) == 1:
            try:
                return float(parts[0])
            except ValueError:
                raise ValueError("Incomplete expression.")

        # sqrt
        if len(parts) == 2 and parts[0] == '√':
            return square_root(float(parts[1]))

        if paradigm == 'Procedural':
            return procedural.calculate(expr)
        elif paradigm == 'OOP':
            return self._oop_calc.calculate(expr)
        elif paradigm == 'Functional':
            return functional.calculate(expr)
        elif paradigm == 'Event-Driven':
            return event_driven.calculate(expr)
        elif paradigm == 'Extended':
            from extras import additional_features
            return additional_features.calculate(expr)
        else:
            return procedural.calculate(expr)


class SmartCalculatorApp(App):
    def build(self):
        self.title = 'Smart Calculator'
        return SmartCalculatorUI()


if __name__ == '__main__':
    SmartCalculatorApp().run()