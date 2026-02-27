import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import (Color, Ellipse, Rectangle,
                            RoundedRectangle, Line)
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.animation import Animation

import paradigms.procedural    as procedural
import paradigms.functional    as functional
import paradigms.event_driven  as event_driven
from paradigms.oop_calculator   import Calculator
from extras.additional_features import square_root

Window.size = (400, 760)
Window.clearcolor = (0.07, 0.07, 0.09, 1)

# ─────────────────────────────────────────────────────────────
#  PALETTE  — Obsidian Glass
#  One base, one mid, one accent. Nothing more.
# ─────────────────────────────────────────────────────────────
P = {
    'base':       '#0D0F12',   # near-black body
    'surface':    '#161A20',   # card / display surface
    'glass':      '#1E242D',   # button resting state
    'glass_op':   '#141820',   # operator buttons (slightly deeper)
    'rim':        '#2A3340',   # button border rim
    'teal':       '#00D4B4',   # THE accent — cold electric teal
    'teal_dim':   '#007A68',   # dim teal for expression line
    'teal_glow':  '#00FFD4',   # brightest teal for equals
    'white':      '#E8EEF5',   # primary text
    'mid':        '#5A6A78',   # secondary text
    'danger':     '#FF4D6A',   # AC button accent
}

_OOP = Calculator()


def _c(h, a=1.0):
    r = get_color_from_hex(h)
    return (r[0], r[1], r[2], a)


# ─────────────────────────────────────────────────────────────
#  GLASS TILE BUTTON
#  Square-ish with rounded corners. Layered:
#    1. Deep shadow below
#    2. Matte glass face
#    3. Thin luminous rim on top+left edges (bevel illusion)
# ─────────────────────────────────────────────────────────────
class GlassBtn(Button):
    def __init__(self, face, rim, txt, fg, fsz=22, **kw):
        super().__init__(**kw)
        self._face = face
        self._rim  = rim
        self._fg   = fg
        self.text  = txt
        self.font_size         = dp(fsz)
        self.bold              = True
        self.color             = _c(fg)
        self.background_normal = ''
        self.background_down   = ''
        self.background_color  = (0, 0, 0, 0)
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *_):
        self.canvas.before.clear()
        x, y, w, h = self.x, self.y, self.width, self.height
        r = dp(16)
        with self.canvas.before:
            # ── deep shadow ──
            Color(0, 0, 0, 0.55)
            RoundedRectangle(pos=(x+dp(2), y-dp(5)),
                             size=(w, h), radius=[r])
            # ── glass face ──
            Color(*_c(self._face))
            RoundedRectangle(pos=(x, y), size=(w, h), radius=[r])
            # ── top-left bevel rim (luminous edge) ──
            Color(*_c(self._rim, 0.55))
            Line(rounded_rectangle=(x+dp(1), y+dp(1),
                                    w-dp(2), h-dp(2),
                                    r-dp(1)), width=dp(0.8))

    def on_press(self):
        anim = Animation(opacity=0.55, duration=0.07) + \
               Animation(opacity=1.0,  duration=0.10)
        anim.start(self)

    def recolor(self, face, rim, fg):
        self._face=face; self._rim=rim; self._fg=fg
        self.color=_c(fg); self._draw()


# ─────────────────────────────────────────────────────────────
#  ACCENT BUTTON  — teal glow for = and operators
# ─────────────────────────────────────────────────────────────
class AccentBtn(GlassBtn):
    def __init__(self, glow_hex, txt, fsz=24, **kw):
        super().__init__(
            face=P['glass_op'], rim=glow_hex,
            txt=txt, fg=glow_hex, fsz=fsz, **kw)
        self._glow = glow_hex

    def _draw(self, *_):
        self.canvas.before.clear()
        x, y, w, h = self.x, self.y, self.width, self.height
        r = dp(16)
        with self.canvas.before:
            # glow halo
            Color(*_c(self._glow, 0.12))
            RoundedRectangle(pos=(x-dp(3), y-dp(7)),
                             size=(w+dp(6), h+dp(6)), radius=[r+dp(4)])
            # shadow
            Color(0, 0, 0, 0.50)
            RoundedRectangle(pos=(x+dp(2), y-dp(5)),
                             size=(w, h), radius=[r])
            # face
            Color(*_c(P['glass_op']))
            RoundedRectangle(pos=(x, y), size=(w, h), radius=[r])
            # teal rim — full border glowing
            Color(*_c(self._glow, 0.70))
            Line(rounded_rectangle=(x+dp(1), y+dp(1),
                                    w-dp(2), h-dp(2),
                                    r-dp(1)), width=dp(1.2))

    def recolor(self, face, rim, fg):
        self._glow = rim
        super().recolor(face, rim, fg)


# ─────────────────────────────────────────────────────────────
#  WIDE PILL  — "0" key spans two columns
# ─────────────────────────────────────────────────────────────
class PillBtn(Button):
    def __init__(self, txt='0', **kw):
        super().__init__(**kw)
        self.text              = txt
        self.font_size         = dp(24)
        self.bold              = True
        self.color             = _c(P['white'])
        self.background_normal = ''
        self.background_down   = ''
        self.background_color  = (0, 0, 0, 0)
        self.halign            = 'left'
        self.valign            = 'middle'
        self.padding_x         = dp(28)
        self.bind(pos=self._draw, size=self._draw)
        self.bind(size=lambda *_: setattr(
            self, 'text_size', (self.width, self.height)))

    def _draw(self, *_):
        x, y, w, h = self.x, self.y, self.width, self.height
        r = dp(h * 0.42)
        with self.canvas.before:
            self.canvas.before.clear()
            Color(0, 0, 0, 0.55)
            RoundedRectangle(pos=(x+dp(2), y-dp(5)),
                             size=(w, h), radius=[r])
            Color(*_c(P['glass']))
            RoundedRectangle(pos=(x, y), size=(w, h), radius=[r])
            Color(*_c(P['rim'], 0.50))
            Line(rounded_rectangle=(x+dp(1), y+dp(1),
                                    w-dp(2), h-dp(2), r-dp(1)),
                 width=dp(0.8))

    def on_press(self):
        anim = Animation(opacity=0.55, duration=0.07) + \
               Animation(opacity=1.0,  duration=0.10)
        anim.start(self)

    def recolor(self, *_): pass   # static


# ─────────────────────────────────────────────────────────────
#  DISPLAY PANEL
# ─────────────────────────────────────────────────────────────
class Display(BoxLayout):
    def __init__(self, **kw):
        super().__init__(orientation='vertical', **kw)
        self.padding = [dp(28), dp(20), dp(28), dp(8)]
        self.spacing = dp(4)

        # ── header row: label left, mode dot right ────────────
        hdr = BoxLayout(size_hint=(1, 0.15), orientation='horizontal')
        self._mode_lbl = Label(
            text='SMART CALC',
            font_size=dp(10),
            halign='left', valign='middle',
            color=_c(P['mid']),
            bold=True,
        )
        self._mode_lbl.bind(size=lambda *_: setattr(
            self._mode_lbl, 'text_size', (self._mode_lbl.width, None)))

        self._theme_btn = Button(
            text='◑',
            font_size=dp(18),
            size_hint=(None, 1), width=dp(36),
            background_normal='', background_color=(0,0,0,0),
            color=_c(P['mid']),
        )
        hdr.add_widget(self._mode_lbl)
        hdr.add_widget(Widget())
        hdr.add_widget(self._theme_btn)
        self.add_widget(hdr)

        # ── expression dim line ───────────────────────────────
        self.expr = Label(
            text='', font_size=dp(15),
            halign='right', valign='bottom',
            size_hint=(1, 0.20),
            color=_c(P['teal_dim']),
        )
        self.expr.bind(size=lambda *_: setattr(
            self.expr, 'text_size', (self.expr.width, None)))
        self.add_widget(self.expr)

        # ── big result ────────────────────────────────────────
        self.result = Label(
            text='0',
            font_size=dp(72),
            halign='right', valign='bottom',
            size_hint=(1, 0.65),
            bold=True,
            color=_c(P['white']),
        )
        self.result.bind(size=lambda *_: setattr(
            self.result, 'text_size', (self.result.width, None)))
        self.add_widget(self.result)

        # ── teal underline separator ──────────────────────────
        self.add_widget(Widget(size_hint=(1, 0.02)))

        self.bind(pos=self._bg, size=self._bg)
        self._bg()

    def _bg(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            # surface card
            Color(*_c(P['surface']))
            RoundedRectangle(pos=self.pos, size=self.size,
                             radius=[0, 0, dp(28), dp(28)])
            # teal bottom rule
            Color(*_c(P['teal'], 0.35))
            Line(points=[self.x + dp(28),
                         self.y + dp(6),
                         self.right - dp(28),
                         self.y + dp(6)],
                 width=dp(1.2))


# ─────────────────────────────────────────────────────────────
#  ROOT
# ─────────────────────────────────────────────────────────────
class CalcRoot(BoxLayout):

    ROWS = [
        [('AC','danger'),('+/-','fn'),('←','fn'),('/','op')],
        [('7','num'),   ('8','num'), ('9','num'), ('×','op')],
        [('4','num'),   ('5','num'), ('6','num'), ('−','op')],
        [('1','num'),   ('2','num'), ('3','num'), ('+','op')],
        [('0','wide'),              ('.','num'),  ('=','eq')],
    ]

    def __init__(self, **kw):
        super().__init__(orientation='vertical', **kw)
        self._e  = ''
        self._jr = False
        self._build()

    def _build(self):
        self._disp = Display(size_hint=(1, 0.34))
        self.add_widget(self._disp)
        self._disp._theme_btn.bind(on_press=lambda *_: None)  # no theme swap needed

        p = dp(14)
        g = BoxLayout(
            orientation='vertical',
            size_hint=(1, 0.66),
            padding=[p, dp(10), p, dp(22)],
            spacing=dp(11),
        )

        for row_spec in self.ROWS:
            row = BoxLayout(orientation='horizontal', spacing=dp(11))
            for lbl, kind in row_spec:
                w = self._make(lbl, kind)
                if kind == 'wide':
                    w.size_hint_x = 2.18
                row.add_widget(w)
            g.add_widget(row)

        self.add_widget(g)
        self.bind(pos=self._bg, size=self._bg)
        self._bg()

    def _make(self, lbl, kind):
        fsz = 18 if len(lbl) > 1 else 22

        if kind == 'wide':
            w = PillBtn(size_hint=(1, 1))
        elif kind == 'eq':
            w = AccentBtn(P['teal_glow'], lbl, fsz=26, size_hint=(1,1))
        elif kind == 'op':
            w = AccentBtn(P['teal'], lbl, fsz=fsz, size_hint=(1,1))
        elif kind == 'danger':
            w = AccentBtn(P['danger'], lbl, fsz=fsz, size_hint=(1,1))
        elif kind == 'fn':
            w = GlassBtn(P['glass'], P['mid'], lbl,
                         fg=P['mid'], fsz=fsz, size_hint=(1,1))
        else:  # num
            w = GlassBtn(P['glass'], P['rim'], lbl,
                         fg=P['white'], fsz=fsz, size_hint=(1,1))

        w.bind(on_press=lambda b: self._key(b.text))
        return w

    def _bg(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*_c(P['base']))
            Rectangle(pos=self.pos, size=self.size)

    # ── input handling ────────────────────────────────────────
    def _key(self, key):
        D = self._disp

        if key == 'AC':
            self._e=''; self._jr=False
            D.result.text='0'; D.expr.text=''
            return

        if key == '←':
            e = self._e.rstrip()
            if e and e[-1] in '+-*/%^':
                e = e[:-1].rstrip()
            elif e:
                e = e[:-1]
            self._e = e
            D.result.text = e.strip() or '0'
            return

        if key == '=':
            self._eval(); return

        if key == '+/-':
            parts = self._e.strip().split()
            if parts:
                try:
                    v = float(parts[-1]); v = -v
                    parts[-1] = str(int(v) if v==int(v) else v)
                    self._e = ' '.join(parts)
                    D.result.text = self._e
                except ValueError: pass
            return

        sym = {'×':'*','−':'-'}.get(key, key)
        is_op = sym in '+-*/%^'

        if self._jr:
            if is_op:
                self._e = D.result.text + ' ' + sym + ' '
            else:
                self._e = sym
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
        D.expr.text   = ''

    def _eval(self):
        expr = self._e.strip()
        if not expr: return
        self._disp.expr.text = expr
        try:
            r = _run(expr)
            out = str(int(r)) if r == int(r) else f'{r:.8g}'
            self._disp.result.text = out
            self._e = out; self._jr = True
        except Exception as ex:
            self._disp.result.text = 'Error'
            self._disp.expr.text   = str(ex)
            self._e = ''; self._jr = False


# ─────────────────────────────────────────────────────────────
#  DISPATCHER
# ─────────────────────────────────────────────────────────────
def _run(expr: str) -> float:
    p = expr.split()
    if len(p) == 1: return float(p[0])
    if len(p) == 2 and p[0] == '√': return square_root(float(p[1]))
    return procedural.calculate(expr)


class SmartCalcApp(App):
    def build(self):
        self.title = 'Smart Calculator'
        return CalcRoot()

if __name__ == '__main__':
    SmartCalcApp().run()