import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.animation import Animation
from kivy.properties import BooleanProperty
from kivy.clock import Clock
from decimal import Decimal, Overflow, Context, setcontext

import paradigms.procedural as procedural
import paradigms.functional as functional
import paradigms.event_driven as event_driven
from paradigms.oop_calculator import Calculator
from extras.additional_features import (
    exponentiate, get_history, clear_history, record as hist_record
)

Window.size = (400, 760)

# ──────────────────────────────────────────────────────────────
#  PALETTES
# ──────────────────────────────────────────────────────────────
DARK = {
    'bg':           '#1A0F1E',
    'display_bg':   '#231428',
    'btn_num':      '#2C1A34',
    'btn_fn':       '#231428',
    'btn_sci':      '#271630',
    'btn_op':       '#C2185B',
    'btn_eq':       '#E91E8C',
    'num_text':     '#F5E6F0',
    'fn_text':      '#7A5E85',
    'sci_text':     '#B39DCC',
    'op_text':      '#FFFFFF',
    'result_text':  '#FCE4EC',
    'expr_text':    '#4A2D55',
    'app_name':     '#7A5E85',
    'toggle_bg':    '#3D1F4A',
    'toggle_text':  '#CE93D8',
    'tab_active':   '#E91E8C',
    'tab_text_on':  '#FFFFFF',
    'tab_text_off': '#6A1B9A',
    'divider':      '#3D1F4A',
    'tray_handle':  '#4A2D55',
    'conv_input':   '#2C1A34',
    'conv_text':    '#F5E6F0',
    'hist_bg':      '#1F1226',
    'hist_item':    '#2C1A34',
    'hist_text':    '#F5E6F0',
    'hist_sub':     '#7A5E85',
    'hist_accent':  '#E91E8C',
}
LIGHT = {
    'bg':           '#FFF0F5',
    'display_bg':   '#FFFFFF',
    'btn_num':      '#FFFFFF',
    'btn_fn':       '#FCE4EC',
    'btn_sci':      '#F8BBD9',
    'btn_op':       '#E91E8C',
    'btn_eq':       '#C2185B',
    'num_text':     '#3E0036',
    'fn_text':      '#AD1457',
    'sci_text':     '#6A1B9A',
    'op_text':      '#FFFFFF',
    'result_text':  '#1A0028',
    'expr_text':    '#CE93D8',
    'app_name':     '#F48FB1',
    'toggle_bg':    '#FCE4EC',
    'toggle_text':  '#C2185B',
    'tab_active':   '#E91E8C',
    'tab_text_on':  '#E91E8C',
    'tab_text_off': '#CE93D8',
    'divider':      '#F8BBD9',
    'tray_handle':  '#F48FB1',
    'conv_input':   '#FFFFFF',
    'conv_text':    '#3E0036',
    'hist_bg':      '#FFF0F5',
    'hist_item':    '#FFFFFF',
    'hist_text':    '#3E0036',
    'hist_sub':     '#CE93D8',
    'hist_accent':  '#E91E8C',
}

_OOP = Calculator()

# paradigm selection state; UI spinner will toggle this
PARADIGM_NAMES = ['Procedural', 'OOP', 'Functional', 'Event']
CURRENT_PARADIGM = 'Procedural'

# Descriptions shown in the info card when each paradigm is selected
PARADIGM_INFO = {
    'Procedural': (
        'Procedural',
        'Step-by-step functions\nif op == "+": return a + b'
    ),
    'OOP': (
        'Object-Oriented',
        'Calculator class instance\nself.result = self.num1 + self.num2'
    ),
    'Functional': (
        'Functional',
        'Pure functions via operator module\noperator.add(num1, num2)'
    ),
    'Event': (
        'Event-Driven',
        'Emit / listen event bus\nemit("calc") -> listener returns result'
    ),
}

# simple dispatcher — routes expression to the selected paradigm engine
def _interpret(expr: str) -> float:
    if CURRENT_PARADIGM == 'Procedural':
        return procedural.calculate(expr)
    if CURRENT_PARADIGM == 'OOP':
        return _OOP.calculate(expr)
    if CURRENT_PARADIGM == 'Functional':
        return functional.calculate(expr)
    if CURRENT_PARADIGM == 'Event':
        return event_driven.calculate(expr)
    return procedural.calculate(expr)

custom_context = Context(prec=50, Emax=1000, Emin=-1000)
setcontext(custom_context)

def exponentiate(base, exp):
    try:
        b = Decimal(str(base))
        e = Decimal(str(exp))
        result = b ** e
        if result.is_infinite():
            return Decimal('Infinity')
        try:
            if int(result.log10()) > 1000:
                return Decimal('Infinity')
        except Exception:
            pass
        return result
    except Overflow:
        return Decimal('Infinity')
    except Exception:
        return "Error"

def _format_result(r) -> str:
    import math
    from decimal import Decimal, InvalidOperation

    MAX_EXP =  1000
    MIN_EXP = -1000

    def _inf_str(negative=False):
        return '-inf' if negative else 'inf'

    def _sci(d: Decimal) -> str:
        s = f'{d:e}'
        m, exp_part = s.split('e')
        m = m.rstrip('0').rstrip('.')
        return f'{m}e{int(exp_part):+d}'

    if isinstance(r, int):
        s_int = str(r)
        if len(s_int) > 12:
            try:
                d = Decimal(r)
                return _sci(d)
            except Exception:
                return f"{r:.8e}"
        return s_int

    if isinstance(r, Decimal):
        if not r.is_finite():
            return _inf_str(r < 0)
        try:
            exp = int(r.log10()) if r != 0 else 0
        except (InvalidOperation, Exception):
            exp = 0
        if exp > MAX_EXP:
            return _inf_str(r < 0)
        if r != 0 and exp < MIN_EXP:
            return _inf_str(r < 0)
        if abs(exp) >= 12:
            return _sci(r)
        return f'{r:g}'

    try:
        f = float(r)
    except (OverflowError, ValueError):
        return _inf_str(str(r).startswith('-'))

    if math.isnan(f):
        return 'NaN'
    if math.isinf(f):
        return _inf_str(f < 0)

    if f != 0:
        try:
            exp = int(math.floor(math.log10(abs(f))))
        except Exception:
            exp = 0
        if exp > MAX_EXP:
            return _inf_str(f < 0)
        if exp < MIN_EXP:
            return _inf_str(f < 0)

    if f == int(f) and abs(f) < 1e15:
        return str(int(f))
    if abs(f) >= 1e12 or (f != 0 and abs(f) < 1e-9):
        s = f'{f:.6e}'
        m, ep = s.split('e')
        m = m.rstrip('0').rstrip('.')
        return f'{m}e{int(ep):+d}'
    return f'{f:.8g}'

def _c(h, a=1.0):
    r = get_color_from_hex(h)
    return (r[0], r[1], r[2], a)


# ──────────────────────────────────────────────────────────────
#  TILE BUTTON
# ──────────────────────────────────────────────────────────────
class Tile(Button):
    def __init__(self, bg, fg, txt, fsz=22, r=16, **kw):
        super().__init__(**kw)
        self._bg = bg; self._fg = fg; self._r = r
        self.text = txt
        self.font_size = dp(fsz); self.bold = True
        self.color = _c(fg)
        self.background_normal = self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        self.bind(pos=self._d, size=self._d)

    def _d(self, *_):
        self.canvas.before.clear()
        x, y, w, h = self.x, self.y, self.width, self.height
        r = dp(self._r)
        with self.canvas.before:
            Color(0, 0, 0, 0.35)
            RoundedRectangle(pos=(x+dp(2), y-dp(5)), size=(w, h), radius=[r])
            Color(*_c(self._bg))
            RoundedRectangle(pos=(x, y), size=(w, h), radius=[r])
            Color(1, 1, 1, 0.07)
            Line(rounded_rectangle=(x+1, y+1, w-2, h-2, r), width=1)

    def on_press(self):
        (Animation(opacity=0.5, duration=0.05) +
         Animation(opacity=1.0, duration=0.12)).start(self)

    def recolor(self, bg, fg):
        self._bg = bg; self._fg = fg
        self.color = _c(fg); self._d()


class Pill(Button):
    """Wide pill-shaped 0 key."""
    def __init__(self, bg, fg, txt='0', fsz=22, r=16, **kw):
        super().__init__(**kw)
        self._bg = bg; self._fg = fg; self._r = r
        self.text = txt; self.font_size = dp(fsz); self.bold = True
        self.color = _c(fg)
        self.background_normal = self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        self.halign = 'left'; self.valign = 'middle'
        self.padding = [dp(26), 0, dp(8), 0]
        self.bind(pos=self._d, size=self._d)
        self.bind(size=lambda *_: setattr(
            self, 'text_size', (self.width, self.height)))

    def _d(self, *_):
        self.canvas.before.clear()
        x, y, w, h = self.x, self.y, self.width, self.height
        r = dp(h * 0.40)
        with self.canvas.before:
            Color(0, 0, 0, 0.35)
            RoundedRectangle(pos=(x+dp(2), y-dp(5)), size=(w, h), radius=[r])
            Color(*_c(self._bg))
            RoundedRectangle(pos=(x, y), size=(w, h), radius=[r])
            Color(1, 1, 1, 0.07)
            Line(rounded_rectangle=(x+1, y+1, w-2, h-2, r), width=1)

    def on_press(self):
        (Animation(opacity=0.5, duration=0.05) +
         Animation(opacity=1.0, duration=0.12)).start(self)

    def recolor(self, bg, fg):
        self._bg = bg; self._fg = fg
        self.color = _c(fg); self._d()


# ──────────────────────────────────────────────────────────────
#  DISPLAY AREA
# ──────────────────────────────────────────────────────────────
class Display(BoxLayout):
    def __init__(self, t, toggle_cb, **kw):
        super().__init__(orientation='vertical', **kw)
        self._t = t
        self.padding = [dp(22), dp(14), dp(22), dp(8)]
        self.spacing = dp(0)

        # ── top row: CALQ | paradigm spinner | theme toggle ───
        top = BoxLayout(size_hint=(1, 0.18), orientation='horizontal',
                        spacing=dp(6))

        self._name = Label(
            text='CalCute', font_size=dp(12), bold=True,
            halign='left', valign='middle',
            color=_c(t['app_name']),
            size_hint=(None, 1), width=dp(55))
        self._name.bind(size=lambda *_: setattr(
            self._name, 'text_size', (self._name.width, None)))

        # Spinner — selecting a paradigm updates CURRENT_PARADIGM
        # and immediately shows its description in the info card below
        self._par_spin = Spinner(
            text=CURRENT_PARADIGM, values=PARADIGM_NAMES,
            font_size=dp(9), size_hint=(None, None), size=(dp(88), dp(24)),
            background_normal='', background_color=_c(t['toggle_bg']),
            color=_c(t['toggle_text']),
        )
        self._par_spin.bind(text=self._on_paradigm_change)

        self._tog = Button(
            text='LIGHT', font_size=dp(9), bold=True,
            size_hint=(None, None), size=(dp(52), dp(24)),
            background_normal='', background_color=(0, 0, 0, 0),
            color=_c(t['toggle_text']),
        )
        self._tog.bind(pos=self._tog_draw, size=self._tog_draw)
        self._tog.bind(on_press=toggle_cb)

        top.add_widget(self._name)
        top.add_widget(self._par_spin)
        top.add_widget(Widget())
        top.add_widget(self._tog)
        self.add_widget(top)

        # ── paradigm info card ────────────────────────────────
        # Shows the paradigm name (bold pink) and a one-liner code
        # snippet so the user can see HOW the calculation was done.
        # Updates instantly whenever the spinner changes.
        card = BoxLayout(orientation='vertical',
                         size_hint=(1, 0.20), spacing=dp(1))
        self._para_title = Label(
            text='', font_size=dp(10), bold=True,
            halign='left', valign='bottom',
            color=_c(t['hist_accent']),
            size_hint=(1, 0.45))
        self._para_title.bind(size=lambda *_: setattr(
            self._para_title, 'text_size', (self._para_title.width, None)))
        self._para_desc = Label(
            text='', font_size=dp(9),
            halign='left', valign='top',
            color=_c(t['toggle_text']),
            size_hint=(1, 0.55))
        self._para_desc.bind(size=lambda *_: setattr(
            self._para_desc, 'text_size', (self._para_desc.width, None)))
        card.add_widget(self._para_title)
        card.add_widget(self._para_desc)
        self.add_widget(card)
        self._card = card

        # ── expression label ──────────────────────────────────
        self.expr = Label(
            text='', font_size=dp(13),
            halign='right', valign='bottom',
            size_hint=(1, 0.14), color=_c(t['expr_text']))
        self.expr.bind(size=lambda *_: setattr(
            self.expr, 'text_size', (self.expr.width, None)))
        self.add_widget(self.expr)

        # ── big result ────────────────────────────────────────
        self.result = Label(
            text='0', font_size=dp(54),
            halign='right', valign='bottom',
            size_hint=(1, 0.48), bold=True,
            color=_c(t['result_text']))
        self.result.bind(size=lambda *_: setattr(
            self.result, 'text_size', (self.result.width, None)))
        self.add_widget(self.result)

        self.bind(pos=self._bg, size=self._bg)
        self._bg()

        # populate the info card with the default paradigm on startup
        self._on_paradigm_change(None, CURRENT_PARADIGM)

    def _tog_draw(self, *_):
        b = self._tog; b.canvas.before.clear()
        with b.canvas.before:
            Color(*_c(self._t['toggle_bg']))
            RoundedRectangle(pos=b.pos, size=b.size, radius=[dp(12)])

    def _on_paradigm_change(self, spinner, text):
        """Called when the paradigm spinner value changes.
        Updates the global CURRENT_PARADIGM and refreshes the info card."""
        global CURRENT_PARADIGM
        CURRENT_PARADIGM = text
        title, desc = PARADIGM_INFO.get(text, (text, ''))
        self._para_title.text = title
        self._para_desc.text  = desc

    def _bg(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*_c(self._t['display_bg']))
            RoundedRectangle(pos=self.pos, size=self.size,
                             radius=[0, 0, dp(20), dp(20)])
            Color(*_c(self._t['divider']))
            Line(points=[self.x+dp(16), self.y+dp(1),
                         self.right-dp(16), self.y+dp(1)], width=1)

    def apply(self, t):
        self._t = t
        self._name.color       = _c(t['app_name'])
        self.expr.color        = _c(t['expr_text'])
        self.result.color      = _c(t['result_text'])
        self._tog.text         = 'DARK' if t is LIGHT else 'LIGHT'
        self._tog.color        = _c(t['toggle_text'])
        self._para_title.color = _c(t['hist_accent'])
        self._para_desc.color  = _c(t['toggle_text'])
        self._par_spin.background_color = _c(t['toggle_bg'])
        self._par_spin.color   = _c(t['toggle_text'])
        self._bg(); self._tog_draw()


# ──────────────────────────────────────────────────────────────
#  SCIENTIFIC TRAY
# ──────────────────────────────────────────────────────────────
SCI_ROWS = [
    ['sin', 'cos', 'tan', 'log', 'ln'],
    ['x^y', 'sqrt', '1/x', 'x!', '%'],
    ['(', ')'],
]

class SciTray(BoxLayout):
    def __init__(self, t, on_sci, **kw):
        super().__init__(orientation='vertical', **kw)
        self._t = t
        self.padding = [dp(12), dp(4), dp(12), dp(4)]
        self.spacing = dp(7)

        hr = BoxLayout(size_hint=(1, None), height=dp(16))
        hr.add_widget(Widget())
        h = Widget(size_hint=(None, None), size=(dp(36), dp(4)))
        h.bind(pos=self._hdraw, size=self._hdraw)
        self._h = h
        hr.add_widget(h)
        hr.add_widget(Widget())
        self.add_widget(hr)

        for row in SCI_ROWS:
            r = BoxLayout(orientation='horizontal',
                          spacing=dp(7), size_hint=(1, 1))
            for lbl in row:
                b = Tile(t['btn_sci'], t['sci_text'], lbl,
                         fsz=13, r=12, size_hint=(1, 1))
                b.bind(on_press=lambda btn, l=lbl: on_sci(l))
                r.add_widget(b)
            self.add_widget(r)

        self.bind(pos=self._bg, size=self._bg)
        self._bg()

    def _hdraw(self, *_):
        self._h.canvas.clear()
        with self._h.canvas:
            Color(*_c(self._t['tray_handle']))
            RoundedRectangle(pos=self._h.pos, size=self._h.size, radius=[dp(2)])

    def _bg(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*_c(self._t['display_bg']))
            RoundedRectangle(pos=self.pos, size=self.size,
                             radius=[dp(16), dp(16), 0, 0])

    def apply(self, t):
        self._t = t; self._bg(); self._hdraw()
        for row_w in self.children:
            if isinstance(row_w, BoxLayout):
                for b in row_w.children:
                    if isinstance(b, Tile):
                        b.recolor(t['btn_sci'], t['sci_text'])


# ──────────────────────────────────────────────────────────────
#  HISTORY PANEL
# ──────────────────────────────────────────────────────────────
class HistoryPanel(BoxLayout):
    def __init__(self, t, on_close, **kw):
        super().__init__(orientation='vertical', **kw)
        self._t = t
        self.padding = [dp(14), dp(8), dp(14), dp(8)]
        self.spacing = dp(6)

        hdr = BoxLayout(size_hint=(1, None), height=dp(34),
                        orientation='horizontal')
        title = Label(text='History', font_size=dp(13), bold=True,
                      halign='left', valign='middle',
                      color=_c(t['hist_accent']), size_hint=(1, 1))
        title.bind(size=lambda *_: setattr(
            title, 'text_size', (title.width, None)))

        clr_btn = Button(
            text='Clear', font_size=dp(11), bold=True,
            size_hint=(None, 1), width=dp(48),
            background_normal='', background_color=(0, 0, 0, 0),
            color=_c(t['fn_text']))
        clr_btn.bind(on_press=lambda *_: self._clear())

        close_btn = Button(
            text='X', font_size=dp(11), bold=True,
            size_hint=(None, 1), width=dp(32),
            background_normal='', background_color=(0, 0, 0, 0),
            color=_c(t['fn_text']))
        close_btn.bind(on_press=lambda *_: on_close())

        hdr.add_widget(title)
        hdr.add_widget(clr_btn)
        hdr.add_widget(close_btn)
        self.add_widget(hdr)

        self._scroll = ScrollView(
            size_hint=(1, 1), do_scroll_x=False,
            bar_width=dp(4),
            bar_color=_c(t['hist_accent'], 0.7),
            bar_inactive_color=_c(t['hist_accent'], 0.25),
            scroll_type=['bars', 'content'])
        self._list = BoxLayout(orientation='vertical',
                               size_hint=(1, None), spacing=dp(5))
        self._list.bind(minimum_height=self._list.setter('height'))
        self._scroll.add_widget(self._list)
        self.add_widget(self._scroll)

        self.bind(pos=self._bg, size=self._bg)
        self._bg()
        self.refresh()

    def refresh(self):
        self._list.clear_widgets()
        items = get_history()
        if not items:
            lbl = Label(text='No history yet.', font_size=dp(12),
                        color=_c(self._t['hist_sub']),
                        size_hint=(1, None), height=dp(32))
            self._list.add_widget(lbl)
            return
        for expr, result in reversed(items):
            try:
                r = int(result) if result == int(result) else round(result, 8)
            except Exception:
                r = result
            item = BoxLayout(orientation='vertical',
                             size_hint=(1, None), height=dp(48),
                             padding=[dp(10), dp(6), dp(10), dp(6)])
            item.bind(pos=lambda w, _: self._item_bg(w),
                      size=lambda w, _: self._item_bg(w))
            expr_lbl = Label(text=str(expr), font_size=dp(11),
                             halign='left', valign='bottom',
                             color=_c(self._t['hist_sub']),
                             size_hint=(1, 0.45))
            expr_lbl.bind(size=lambda w, _: setattr(
                w, 'text_size', (w.width, None)))
            res_lbl = Label(text=str(r), font_size=dp(16), bold=True,
                            halign='left', valign='top',
                            color=_c(self._t['hist_text']),
                            size_hint=(1, 0.55))
            res_lbl.bind(size=lambda w, _: setattr(
                w, 'text_size', (w.width, None)))
            item.add_widget(expr_lbl)
            item.add_widget(res_lbl)
            self._list.add_widget(item)

    def _item_bg(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*_c(self._t['hist_item']))
            RoundedRectangle(pos=w.pos, size=w.size, radius=[dp(10)])

    def _clear(self):
        clear_history(); self.refresh()

    def _bg(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*_c(self._t['hist_bg']))
            RoundedRectangle(pos=self.pos, size=self.size,
                             radius=[dp(16), dp(16), 0, 0])

    def apply(self, t):
        self._t = t
        self._scroll.bar_color = _c(t['hist_accent'], 0.7)
        self._scroll.bar_inactive_color = _c(t['hist_accent'], 0.25)
        self._bg(); self.refresh()


# ──────────────────────────────────────────────────────────────
#  CONVERTER TAB
# ──────────────────────────────────────────────────────────────
CONV_CATS = {
    'Length':  {'m':1,'km':1000,'cm':0.01,'mm':0.001,
                'mi':1609.34,'ft':0.3048,'in':0.0254},
    'Mass':    {'kg':1,'g':0.001,'lb':0.453592,
                'oz':0.0283495,'t':1000},
    'Temp':    {'C':1,'F':1,'K':1},
    'Speed':   {'m/s':1,'km/h':0.27778,'mph':0.44704,'knot':0.51444},
    'Area':    {'m2':1,'km2':1e6,'cm2':1e-4,'ft2':0.092903,'ac':4046.86},
    'Volume':  {'L':1,'mL':0.001,'m3':1000,'gal':3.78541},
    'Data':    {'B':1,'KB':1024,'MB':1048576,
                'GB':1073741824,'TB':1099511627776},
    'Time':    {'s':1,'min':60,'hr':3600,'day':86400},
}

def _convert(val, fu, tu, cat):
    if cat == 'Temp':
        if fu == tu: return val
        tbl = {('C','F'):lambda v:v*9/5+32, ('F','C'):lambda v:(v-32)*5/9,
               ('C','K'):lambda v:v+273.15,  ('K','C'):lambda v:v-273.15,
               ('F','K'):lambda v:(v-32)*5/9+273.15,
               ('K','F'):lambda v:(v-273.15)*9/5+32}
        fn = tbl.get((fu, tu))
        return fn(val) if fn else val
    u = CONV_CATS[cat]
    return val * u[fu] / u[tu]


class ConverterView(BoxLayout):
    def __init__(self, t, **kw):
        super().__init__(orientation='vertical', **kw)
        self._t   = t
        self._cat = 'Length'
        self.padding = [dp(16), dp(14), dp(16), dp(16)]
        self.spacing = dp(10)

        scroll = ScrollView(size_hint=(1, None), height=dp(42),
                            do_scroll_y=False, bar_width=0)
        self._chip_row = BoxLayout(orientation='horizontal',
                                   size_hint=(None, 1), spacing=dp(7))
        self._chip_row.bind(minimum_width=self._chip_row.setter('width'))
        self._chip_btns = {}
        for cat in CONV_CATS:
            b = Button(text=cat, font_size=dp(12), bold=True,
                       size_hint=(None, 1), width=dp(72),
                       background_normal='', background_color=(0,0,0,0))
            b.bind(pos=lambda w,_,b=b: self._chip_draw(b),
                   size=lambda w,_,b=b: self._chip_draw(b))
            b.bind(on_press=lambda btn,c=cat: self._set_cat(c))
            self._chip_row.add_widget(b)
            self._chip_btns[cat] = b
        scroll.add_widget(self._chip_row)
        self.add_widget(scroll)

        in_lbl = Label(text='Value to convert', font_size=dp(11),
                       halign='left', valign='middle',
                       color=_c(t['fn_text']),
                       size_hint=(1, None), height=dp(18))
        in_lbl.bind(size=lambda *_: setattr(
            in_lbl, 'text_size', (in_lbl.width, None)))
        self.add_widget(in_lbl)
        self._in_lbl = in_lbl

        def sci_filter(text, from_undo):
            return ''.join(ch for ch in text if ch.isdigit() or ch in '.eE+-')

        self._val = TextInput(
            hint_text='0', font_size=dp(26),
            size_hint=(1, None), height=dp(60),
            input_filter=sci_filter, multiline=False,
            background_normal='',
            background_color=_c(t['conv_input']),
            foreground_color=_c(t['conv_text']),
            cursor_color=_c(t['btn_op']),
            padding=[dp(14), dp(14)])
        self.add_widget(self._val)

        units = list(CONV_CATS[self._cat].keys())
        unit_row = BoxLayout(size_hint=(1, None), height=dp(52),
                             orientation='horizontal', spacing=dp(10))
        from_col = BoxLayout(orientation='vertical', size_hint=(1,1))
        to_col   = BoxLayout(orientation='vertical', size_hint=(1,1))

        lbl_from = Label(text='From', font_size=dp(10),
                         color=_c(t['fn_text']), size_hint=(1,None),
                         height=dp(16), halign='left')
        lbl_from.bind(size=lambda *_: setattr(
            lbl_from,'text_size',(lbl_from.width,None)))
        lbl_to = Label(text='To', font_size=dp(10),
                       color=_c(t['fn_text']), size_hint=(1,None),
                       height=dp(16), halign='left')
        lbl_to.bind(size=lambda *_: setattr(
            lbl_to,'text_size',(lbl_to.width,None)))

        self._from = Spinner(text=units[0], values=units,
                             font_size=dp(14), background_normal='',
                             background_color=_c(t['btn_fn']),
                             color=_c(t['conv_text']), size_hint=(1, 1))
        self._to   = Spinner(text=units[1] if len(units)>1 else units[0],
                             values=units, font_size=dp(14),
                             background_normal='',
                             background_color=_c(t['btn_fn']),
                             color=_c(t['conv_text']), size_hint=(1, 1))

        from_col.add_widget(lbl_from); from_col.add_widget(self._from)
        to_col.add_widget(lbl_to);     to_col.add_widget(self._to)

        arr = Label(text='>>', font_size=dp(16), bold=True,
                    color=_c(t['btn_op']), size_hint=(None,1), width=dp(28))
        unit_row.add_widget(from_col)
        unit_row.add_widget(arr)
        unit_row.add_widget(to_col)
        self.add_widget(unit_row)
        self._arr = arr

        self._go = Tile(t['btn_op'], t['op_text'], 'Convert',
                        fsz=15, r=14, size_hint=(1, None))
        self._go.height = dp(48)
        self._go.bind(on_press=lambda *_: self._do())
        self.add_widget(self._go)

        self._res_card = BoxLayout(orientation='vertical', size_hint=(1, 1),
                                   padding=[dp(14), dp(10)])
        self._res_card.bind(pos=self._res_bg, size=self._res_bg)
        self._res_lbl = Label(text='', font_size=dp(28), bold=True,
                              halign='center', valign='middle',
                              color=_c(t['result_text']), size_hint=(1, 1))
        self._res_lbl.bind(size=lambda *_: setattr(
            self._res_lbl, 'text_size', (self._res_lbl.width, None)))
        self._res_card.add_widget(self._res_lbl)
        self.add_widget(self._res_card)

        self.bind(pos=self._bg, size=self._bg)
        self._bg(); self._highlight()

    def _chip_draw(self, b):
        b.canvas.before.clear()
        active = (b.text == self._cat)
        bg = self._t['btn_op'] if active else self._t['btn_fn']
        fg = self._t['op_text'] if active else self._t['fn_text']
        b.color = _c(fg)
        with b.canvas.before:
            Color(*_c(bg))
            RoundedRectangle(pos=b.pos, size=b.size, radius=[dp(10)])

    def _highlight(self):
        for b in self._chip_btns.values(): self._chip_draw(b)

    def _set_cat(self, cat):
        self._cat = cat
        units = list(CONV_CATS[cat].keys())
        self._from.values = self._to.values = units
        self._from.text = units[0]
        self._to.text   = units[1] if len(units)>1 else units[0]
        self._res_lbl.text = ''; self._highlight()

    def _do(self):
        try:
            val = float(self._val.text or '0')
            res = _convert(val, self._from.text, self._to.text, self._cat)
            out = _format_result(res)
            self._res_lbl.text = (
                f'{self._val.text or val} {self._from.text}\n= {out} {self._to.text}')
        except Exception as e:
            self._res_lbl.text = f'Error: {e}'

    def _res_bg(self, *_):
        self._res_card.canvas.before.clear()
        with self._res_card.canvas.before:
            Color(*_c(self._t['btn_fn']))
            RoundedRectangle(pos=self._res_card.pos,
                             size=self._res_card.size, radius=[dp(14)])

    def _bg(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*_c(self._t['bg']))
            Rectangle(pos=self.pos, size=self.size)

    def apply(self, t):
        self._t = t
        self._val.background_color  = _c(t['conv_input'])
        self._val.foreground_color  = _c(t['conv_text'])
        self._from.background_color = _c(t['btn_fn'])
        self._from.color            = _c(t['conv_text'])
        self._to.background_color   = _c(t['btn_fn'])
        self._to.color              = _c(t['conv_text'])
        self._arr.color             = _c(t['btn_op'])
        self._res_lbl.color         = _c(t['result_text'])
        self._in_lbl.color          = _c(t['fn_text'])
        self._go.recolor(t['btn_op'], t['op_text'])
        self._bg(); self._res_bg(); self._highlight()


# ──────────────────────────────────────────────────────────────
#  CALCULATOR PAGE
# ──────────────────────────────────────────────────────────────
MAIN_ROWS = [
    [('AC','fn'), ('+/-','fn'), ('DEL','fn'), ('/','op')],
    [('7','num'), ('8','num'),  ('9','num'),  ('x','op')],
    [('4','num'), ('5','num'),  ('6','num'),  ('-','op')],
    [('1','num'), ('2','num'),  ('3','num'),  ('+','op')],
    [('SCI','sci'), ('HIST','sci'), ('0','wide'), ('.','num'), ('=','eq')],
]

class CalcPage(BoxLayout):
    def __init__(self, t, toggle_cb, **kw):
        super().__init__(orientation='vertical', **kw)
        self._t         = t
        self._e         = ''
        self._jr        = False
        self._sci_open  = False
        self._hist_open = False
        self._tiles     = []

        self._disp = Display(t, toggle_cb, size_hint=(1, 0.30))
        self.add_widget(self._disp)

        self._tray = SciTray(t, self._sci_key,
                             size_hint=(1, None), height=0, opacity=0)
        self.add_widget(self._tray)

        self._hist = HistoryPanel(t, self._close_hist,
                                  size_hint=(1, None), height=0, opacity=0)
        self.add_widget(self._hist)

        self._grid = BoxLayout(
            orientation='vertical', size_hint=(1, 1),
            padding=[dp(11), dp(5), dp(11), dp(16)], spacing=dp(8))
        self._build_grid()
        self.add_widget(self._grid)

        self.bind(pos=self._bg, size=self._bg)
        self._bg()

    def _build_grid(self):
        self._grid.clear_widgets(); self._tiles.clear()
        for row_spec in MAIN_ROWS:
            row = BoxLayout(orientation='horizontal', spacing=dp(8))
            for lbl, kind in row_spec:
                w = self._make_btn(lbl, kind)
                if kind == 'wide': w.size_hint_x = 2.05
                row.add_widget(w)
                self._tiles.append((w, 'num' if kind=='wide' else kind))
            self._grid.add_widget(row)

    def _make_btn(self, lbl, kind):
        t = self._t
        fsz = 14 if len(lbl) > 2 else (18 if len(lbl) > 1 else 22)
        lu = {
            'num':  (t['btn_num'], t['num_text']),
            'wide': (t['btn_num'], t['num_text']),
            'fn':   (t['btn_fn'],  t['fn_text']),
            'sci':  (t['btn_sci'], t['sci_text']),
            'op':   (t['btn_op'],  t['op_text']),
            'eq':   (t['btn_eq'],  t['op_text']),
        }
        bg, fg = lu.get(kind, lu['num'])
        if kind == 'wide':
            w = Pill(bg, fg, lbl, fsz=22, size_hint=(1, 1))
        else:
            w = Tile(bg, fg, lbl, fsz=fsz, r=15, size_hint=(1, 1))
        w.bind(on_press=lambda b: self._key(b.text))
        return w

    def _bg(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*_c(self._t['bg']))
            Rectangle(pos=self.pos, size=self.size)

    def _open_sci(self):
        if self._hist_open: self._close_hist_anim()
        self._sci_open = not self._sci_open
        h  = dp(118) if self._sci_open else 0
        op = 1.0     if self._sci_open else 0.0
        Animation(height=h, opacity=op, duration=0.2, t='out_cubic').start(self._tray)

    def _close_hist_anim(self):
        self._hist_open = False
        Animation(height=0, opacity=0, duration=0.18, t='out_cubic').start(self._hist)

    def _open_hist(self):
        if self._sci_open: self._open_sci()
        self._hist_open = not self._hist_open
        if self._hist_open: self._hist.refresh()
        h  = dp(200) if self._hist_open else 0
        op = 1.0     if self._hist_open else 0.0
        Animation(height=h, opacity=op, duration=0.2, t='out_cubic').start(self._hist)

    def _close_hist(self):
        self._hist_open = False
        Animation(height=0, opacity=0, duration=0.18, t='out_cubic').start(self._hist)

    def apply_theme(self, t):
        self._t = t
        self._disp.apply(t); self._tray.apply(t); self._hist.apply(t)
        self._bg()
        lu = {
            'num':  (t['btn_num'], t['num_text']),
            'fn':   (t['btn_fn'],  t['fn_text']),
            'sci':  (t['btn_sci'], t['sci_text']),
            'op':   (t['btn_op'],  t['op_text']),
            'eq':   (t['btn_eq'],  t['op_text']),
        }
        for w, kind in self._tiles:
            bg, fg = lu.get(kind, lu['num'])
            w.recolor(bg, fg)

    def get_display_text(self):
        return self._disp.result.text

    def _key(self, key):
        if key == 'SCI':  self._open_sci();  return
        if key == 'HIST': self._open_hist(); return

        D = self._disp
        if key == 'AC':
            self._e = ''; self._jr = False
            D.result.text = '0'; D.expr.text = ''; return

        if key == 'DEL':
            e = self._e.rstrip()
            e = (e[:-1].rstrip() if (e and e[-1] in '+-*/%^')
                 else e[:-1] if e else e)
            self._e = e; D.result.text = e.strip() or '0'; return

        if key == '=':
            self._eval(); return

        if key == '+/-':
            parts = self._e.strip().split()
            if parts:
                try:
                    v = float(parts[-1]); v = -v
                    parts[-1] = str(int(v) if v == int(v) else v)
                    self._e = ' '.join(parts); D.result.text = self._e
                except ValueError: pass
            return

        sym = {'x': '*'}.get(key, key)
        is_op = sym in '+-*/%^'

        if self._jr:
            self._e = D.result.text + ' ' + sym + ' ' if is_op else sym
            self._jr = False
        else:
            if is_op:
                s = self._e.rstrip(); toks = s.split()
                if toks and toks[-1] in '+-*/%^':
                    toks[-1] = sym; self._e = ' '.join(toks) + ' '
                else:
                    self._e = s + ' ' + sym + ' '
            else:
                self._e += sym

        D.result.text = self._e.strip() or '0'
        D.expr.text = ''

    def _sci_key(self, fn):
        D  = self._disp
        ex = self._e.strip()
        try:
            val = float(ex) if ex else 0.0
        except ValueError:
            val = 0.0
        try:
            if fn == 'sin':  res = math.sin(math.radians(val))
            elif fn=='cos':  res = math.cos(math.radians(val))
            elif fn=='tan':  res = math.tan(math.radians(val))
            elif fn=='log':  res = math.log10(val)
            elif fn=='ln':   res = math.log(val)
            elif fn=='x^y':
                D.expr.text = f'{ex} ^'; self._e = ex + ' ^ '; return
            elif fn=='sqrt': res = math.sqrt(val)
            elif fn=='1/x':  res = 1 / val
            elif fn=='x!':   res = float(math.factorial(int(val)))
            elif fn=='%':
                s = (self._e or '').rstrip()
                last = s[-1] if s else None
                if last and (last.isdigit() or last == ')'):
                    self._e = (self._e or '') + ' % '
                    D.result.text = self._e.strip() or '0'; return
                res = val / 100
            elif fn == '(' or fn == ')':
                s = (self._e or '').rstrip()
                last = s[-1] if s else None
                if fn == '(':
                    if last and (last.isdigit() or last == ')'):
                        self._e = (self._e or '') + '*('
                    else:
                        self._e = (self._e or '') + '('
                else:
                    self._e = (self._e or '') + ')'
                D.result.text = self._e.strip() or '0'; return
            else: return
            label = f'{fn}({ex})'
            out   = _format_result(res)
            hist_record(label, res)
            D.expr.text = label; D.result.text = out
            self._e = out; self._jr = True
        except Exception as e:
            D.result.text = 'Error'; D.expr.text = str(e)
            self._e = ''; self._jr = False

    def _eval(self):
        expr = self._e.strip()
        if not expr: return
        self._disp.expr.text = expr
        print(f"[QA] Paradigm: {CURRENT_PARADIGM}  |  Expr: {expr}")
        try:
            r   = _interpret(expr)
            out = _format_result(r)
            hist_record(f"[{CURRENT_PARADIGM}] {expr}", r)
            self._disp.result.text = out
            self._e = out; self._jr = True
        except Exception as ex:
            self._disp.result.text = 'Error'
            self._disp.expr.text   = str(ex)
            self._e = ''; self._jr = False


# ──────────────────────────────────────────────────────────────
#  TAB BAR
# ──────────────────────────────────────────────────────────────
class TabBar(BoxLayout):
    def __init__(self, t, on_tab, **kw):
        kw.setdefault('size_hint', (1, None))
        kw.setdefault('height', dp(42))
        super().__init__(orientation='horizontal', **kw)
        self._t      = t
        self._on_tab = on_tab
        self._btns   = {}
        self._active = 'Calculator'
        self.padding = [dp(14), dp(5), dp(14), dp(0)]
        self.spacing = dp(0)

        for label in ['Calculator', 'Converter']:
            b = Button(text=label, font_size=dp(13), bold=True,
                       size_hint=(1, 1),
                       background_normal='', background_color=(0,0,0,0))
            b.bind(on_press=lambda btn, l=label: self._tap(l))
            b.bind(pos=self._bg, size=self._bg)
            self._btns[label] = b
            self.add_widget(b)

        self._update()
        self.bind(pos=self._bg, size=self._bg)
        self._bg()

    def _tap(self, label):
        self._active = label; self._update(); self._on_tab(label)

    def _update(self):
        for lbl, b in self._btns.items():
            on = (lbl == self._active)
            b.color = _c(self._t['tab_text_on' if on else 'tab_text_off'])
            b.bold  = on
        self._bg()

    def _bg(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*_c(self._t['display_bg']))
            Rectangle(pos=self.pos, size=self.size)
            for lbl, b in self._btns.items():
                if lbl == self._active:
                    Color(*_c(self._t['tab_active']))
                    Line(points=[b.x+dp(4), self.y+dp(3),
                                 b.right-dp(4), self.y+dp(3)],
                         width=dp(2.5))

    def apply(self, t):
        self._t = t; self._update(); self._bg()


# ──────────────────────────────────────────────────────────────
#  ROOT
# ──────────────────────────────────────────────────────────────
class CalqRoot(FloatLayout):
    dark = BooleanProperty(True)

    def __init__(self, **kw):
        super().__init__(**kw)
        self._t = DARK
        self._build()

    def _build(self):
        self._shell = BoxLayout(orientation='vertical',
                                size_hint=(1, 1), pos=(0, 0))
        self._tabs = TabBar(self._t, self._on_tab)
        self._shell.add_widget(self._tabs)

        self._pages = BoxLayout(orientation='horizontal', size_hint=(1, 1))
        self._calc  = CalcPage(self._t, self._toggle, size_hint=(1, 1))
        self._conv  = ConverterView(self._t, size_hint=(1, 1))
        self._pages.add_widget(self._calc)
        self._shell.add_widget(self._pages)
        self.add_widget(self._shell)

    def _on_tab(self, label):
        try:
            self._tabs._active = label
            self._tabs._update()
        except Exception:
            pass
        self._pages.clear_widgets()
        self._pages.add_widget(self._calc if label == 'Calculator' else self._conv)

    def _toggle(self, *_):
        self.dark = not self.dark
        self._t   = DARK if self.dark else LIGHT
        self._tabs.apply(self._t)
        self._calc.apply_theme(self._t)
        self._conv.apply(self._t)


def _run(expr: str) -> float:
    return _interpret(expr)


# ──────────────────────────────────────────────────────────────
#  APP
# ──────────────────────────────────────────────────────────────
class CalqApp(App):
    def build(self):
        self.title = 'CALQ'
        return CalqRoot()

if __name__ == '__main__':
    CalqApp().run()