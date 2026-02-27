import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.animation import Animation
from kivy.properties import BooleanProperty

import paradigms.procedural   as procedural
import paradigms.functional   as functional
import paradigms.event_driven as event_driven
from paradigms.oop_calculator   import Calculator
from extras.additional_features import square_root

Window.size = (400, 760)

# ─────────────────────────────────────────────────────────────
#  THEMES
#  DARK  = warm midnight ink  —  charcoal + amber
#  LIGHT = soft cream         —  ivory + slate
# ─────────────────────────────────────────────────────────────
DARK = {
    'bg':           '#16181D',   # midnight ink
    'display_bg':   '#1E2128',   # slightly lifted surface
    'btn_num':      '#252830',   # dark slate tile
    'btn_fn':       '#1E2128',   # slightly recessed function keys
    'btn_op':       '#C8873A',   # warm amber — operators
    'btn_eq':       '#C8873A',   # same amber — equals
    'num_text':     '#E8E2D9',   # warm off-white
    'fn_text':      '#7A8494',   # dim grey
    'op_text':      '#FFFFFF',   # white on amber
    'result_text':  '#F0EBE3',   # warm cream
    'expr_text':    '#3E4450',   # very dim
    'app_name':     '#3E4450',   # dim label
    'toggle_bg':    '#252830',
    'toggle_text':  '#7A8494',
    'divider':      '#252830',
    'name':         'CALQ',
}
LIGHT = {
    'bg':           '#F5F0E8',   # ivory cream
    'display_bg':   '#FFFDF8',   # brightest surface
    'btn_num':      '#FFFFFF',   # pure white tile
    'btn_fn':       '#E8E3D8',   # warm grey function keys
    'btn_op':       '#C8873A',   # same amber
    'btn_eq':       '#C8873A',
    'num_text':     '#1E2330',   # near-black
    'fn_text':      '#8A8070',   # warm grey
    'op_text':      '#FFFFFF',
    'result_text':  '#1A1C22',
    'expr_text':    '#C0B8A8',
    'app_name':     '#C0B8A8',
    'toggle_bg':    '#E8E3D8',
    'toggle_text':  '#8A8070',
    'divider':      '#E8E3D8',
    'name':         'CALQ',
}

_OOP = Calculator()


def _c(h, a=1.0):
    r = get_color_from_hex(h)
    return (r[0], r[1], r[2], a)


# ─────────────────────────────────────────────────────────────
#  TILE BUTTON
#  Rounded square. Shadow below. Thin top-edge highlight.
#  Press → quick opacity dip.
# ─────────────────────────────────────────────────────────────
class Tile(Button):
    def __init__(self, bg, fg, txt, fsz=22, radius=14, **kw):
        super().__init__(**kw)
        self._bg = bg; self._fg = fg
        self._r  = radius
        self.text              = txt
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
        r = dp(self._r)
        with self.canvas.before:
            # shadow
            Color(0, 0, 0, 0.28)
            RoundedRectangle(pos=(x + dp(2), y - dp(4)),
                             size=(w, h), radius=[r])
            # face
            Color(*_c(self._bg))
            RoundedRectangle(pos=(x, y), size=(w, h), radius=[r])
            # top highlight edge (1px lighter line = depth)
            Color(1, 1, 1, 0.06)
            Line(rounded_rectangle=(x+dp(1), y+dp(1),
                                    w-dp(2), h-dp(2),
                                    r), width=dp(1))

    def on_press(self):
        a = Animation(opacity=0.6, duration=0.06) + \
            Animation(opacity=1.0, duration=0.12)
        a.start(self)

    def recolor(self, bg, fg):
        self._bg = bg; self._fg = fg
        self.color = _c(fg); self._draw()


# ─────────────────────────────────────────────────────────────
#  PILL BUTTON  (wide 0 key)
# ─────────────────────────────────────────────────────────────
class Pill(Button):
    def __init__(self, bg, fg, txt='0', fsz=22, **kw):
        super().__init__(**kw)
        self._bg = bg; self._fg = fg
        self.text              = txt
        self.font_size         = dp(fsz)
        self.bold              = True
        self.color             = _c(fg)
        self.background_normal = ''
        self.background_down   = ''
        self.background_color  = (0, 0, 0, 0)
        self.halign            = 'left'
        self.valign            = 'middle'
        self.bind(pos=self._draw, size=self._draw)
        self.bind(size=lambda *_: setattr(
            self, 'text_size', (self.width, self.height)))
        self.padding_x = dp(26)

    def _draw(self, *_):
        self.canvas.before.clear()
        x, y, w, h = self.x, self.y, self.width, self.height
        r = dp(h * 0.40)
        with self.canvas.before:
            Color(0, 0, 0, 0.28)
            RoundedRectangle(pos=(x+dp(2), y-dp(4)),
                             size=(w, h), radius=[r])
            Color(*_c(self._bg))
            RoundedRectangle(pos=(x, y), size=(w, h), radius=[r])
            Color(1, 1, 1, 0.06)
            Line(rounded_rectangle=(x+dp(1), y+dp(1),
                                    w-dp(2), h-dp(2), r),
                 width=dp(1))

    def on_press(self):
        a = Animation(opacity=0.6, duration=0.06) + \
            Animation(opacity=1.0, duration=0.12)
        a.start(self)

    def recolor(self, bg, fg):
        self._bg=bg; self._fg=fg
        self.color=_c(fg); self._draw()


# ─────────────────────────────────────────────────────────────
#  DISPLAY
# ─────────────────────────────────────────────────────────────
class Display(BoxLayout):
    def __init__(self, t, toggle_cb, **kw):
        super().__init__(orientation='vertical', **kw)
        self._t = t
        self.padding = [dp(26), dp(18), dp(26), dp(12)]
        self.spacing = dp(0)

        # ── row 1: app name  +  theme toggle ─────────────────
        top = BoxLayout(size_hint=(1, 0.20),
                        orientation='horizontal')

        self._name_lbl = Label(
            text=t['name'],
            font_size=dp(11),
            bold=True,
            halign='left', valign='middle',
            color=_c(t['app_name']),
            size_hint=(None, 1),
            width=dp(80),
        )
        self._name_lbl.bind(size=lambda *_: setattr(
            self._name_lbl, 'text_size',
            (self._name_lbl.width, None)))

        # theme toggle pill: shows "DARK" or "LIGHT" text
        self._tog_bg = Widget(size_hint=(None, None),
                              size=(dp(70), dp(26)))
        self._tog = Button(
            text='LIGHT',
            font_size=dp(10),
            bold=True,
            size_hint=(None, None),
            size=(dp(70), dp(26)),
            background_normal='',
            background_color=(0,0,0,0),
        )
        self._tog.bind(pos=self._draw_tog, size=self._draw_tog)
        self._tog.bind(on_press=toggle_cb)
        self._update_tog_color(t)

        top.add_widget(self._name_lbl)
        top.add_widget(Widget())
        top.add_widget(self._tog)
        self.add_widget(top)

        # ── row 2: expression (dim, right) ───────────────────
        self.expr = Label(
            text='', font_size=dp(15),
            halign='right', valign='bottom',
            size_hint=(1, 0.18),
            color=_c(t['expr_text']),
        )
        self.expr.bind(size=lambda *_: setattr(
            self.expr, 'text_size', (self.expr.width, None)))
        self.add_widget(self.expr)

        # ── row 3: big result ─────────────────────────────────
        self.result = Label(
            text='0',
            font_size=dp(68),
            halign='right', valign='bottom',
            size_hint=(1, 0.62),
            bold=True,
            color=_c(t['result_text']),
        )
        self.result.bind(size=lambda *_: setattr(
            self.result, 'text_size', (self.result.width, None)))
        self.add_widget(self.result)

        self.bind(pos=self._bg, size=self._bg)
        self._bg()

    def _draw_tog(self, *_):
        b = self._tog
        b.canvas.before.clear()
        with b.canvas.before:
            Color(*_c(self._t['toggle_bg']))
            RoundedRectangle(pos=b.pos, size=b.size, radius=[dp(13)])

    def _update_tog_color(self, t):
        self._tog.color = _c(t['toggle_text'])

    def _bg(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*_c(self._t['display_bg']))
            RoundedRectangle(pos=self.pos, size=self.size,
                             radius=[0, 0, dp(24), dp(24)])
            # thin divider line at bottom
            Color(*_c(self._t['divider']))
            Line(points=[self.x + dp(20), self.y + dp(1),
                         self.right - dp(20), self.y + dp(1)],
                 width=dp(1))

    def apply(self, t):
        self._t = t
        self._name_lbl.color  = _c(t['app_name'])
        self.expr.color       = _c(t['expr_text'])
        self.result.color     = _c(t['result_text'])
        self._tog.text        = 'DARK' if t is LIGHT else 'LIGHT'
        self._update_tog_color(t)
        self._bg()
        self._draw_tog()


# ─────────────────────────────────────────────────────────────
#  ROOT
# ─────────────────────────────────────────────────────────────
class CalcRoot(BoxLayout):
    dark = BooleanProperty(True)

    # label, kind
    ROWS = [
        [('AC','fn'),  ('+/-','fn'), ('DEL','fn'), ('/','op')],
        [('7','num'),  ('8','num'),  ('9','num'),  ('x','op')],
        [('4','num'),  ('5','num'),  ('6','num'),  ('-','op')],
        [('1','num'),  ('2','num'),  ('3','num'),  ('+','op')],
        [('0','wide'),              ('.','num'),   ('=','eq')],
    ]

    def __init__(self, **kw):
        super().__init__(orientation='vertical', **kw)
        self._t  = DARK
        self._e  = ''
        self._jr = False
        self._tiles = []   # (widget, kind)
        self._build()

    def _build(self):
        self._disp = Display(self._t, self._toggle,
                             size_hint=(1, 0.32))
        self.add_widget(self._disp)

        pad = dp(14)
        grid = BoxLayout(
            orientation='vertical',
            size_hint=(1, 0.68),
            padding=[pad, dp(8), pad, dp(20)],
            spacing=dp(10),
        )

        for row_spec in self.ROWS:
            row = BoxLayout(orientation='horizontal', spacing=dp(10))
            for lbl, kind in row_spec:
                w = self._make(lbl, kind)
                if kind == 'wide':
                    w.size_hint_x = 2.17
                row.add_widget(w)
                self._tiles.append((w, 'num' if kind=='wide' else kind))
            grid.add_widget(row)

        self.add_widget(grid)
        self.bind(pos=self._bg, size=self._bg)
        self._bg()

    def _make(self, lbl, kind):
        t   = self._t
        fsz = 17 if len(lbl) > 1 else 22
        if kind == 'wide':
            w = Pill(t['btn_num'], t['num_text'],
                     txt=lbl, fsz=22, size_hint=(1,1))
        elif kind == 'eq':
            w = Tile(t['btn_eq'],  t['op_text'],
                     lbl, fsz=26, radius=14, size_hint=(1,1))
        elif kind == 'op':
            w = Tile(t['btn_op'],  t['op_text'],
                     lbl, fsz=fsz, radius=14, size_hint=(1,1))
        elif kind == 'fn':
            w = Tile(t['btn_fn'],  t['fn_text'],
                     lbl, fsz=fsz, radius=14, size_hint=(1,1))
        else:
            w = Tile(t['btn_num'], t['num_text'],
                     lbl, fsz=22,  radius=14, size_hint=(1,1))
        w.bind(on_press=lambda b: self._key(b.text))
        return w

    def _bg(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*_c(self._t['bg']))
            Rectangle(pos=self.pos, size=self.size)

    def _toggle(self, *_):
        self.dark = not self.dark
        self._t   = DARK if self.dark else LIGHT
        self._bg()
        self._disp.apply(self._t)
        t  = self._t
        lu = {
            'num': (t['btn_num'], t['num_text']),
            'fn':  (t['btn_fn'],  t['fn_text']),
            'op':  (t['btn_op'],  t['op_text']),
            'eq':  (t['btn_eq'],  t['op_text']),
        }
        for w, kind in self._tiles:
            bg, fg = lu.get(kind, lu['num'])
            w.recolor(bg, fg)

    # ── key logic ─────────────────────────────────────────────
    def _key(self, key):
        D = self._disp

        if key == 'AC':
            self._e=''; self._jr=False
            D.result.text='0'; D.expr.text=''
            return

        if key == 'DEL':
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
                    v=float(parts[-1]); v=-v
                    parts[-1]=str(int(v) if v==int(v) else v)
                    self._e=' '.join(parts); D.result.text=self._e
                except ValueError: pass
            return

        # map display label → internal symbol
        sym = {'x':'*'}.get(key, key)
        is_op = sym in '+-*/%^'

        if self._jr:
            if is_op:
                self._e = D.result.text + ' ' + sym + ' '
            else:
                self._e = sym
            self._jr = False
        else:
            if is_op:
                s=self._e.rstrip(); toks=s.split()
                if toks and toks[-1] in '+-*/%^':
                    toks[-1]=sym; self._e=' '.join(toks)+' '
                else:
                    self._e=s+' '+sym+' '
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
            self._e=''; self._jr=False


# ─────────────────────────────────────────────────────────────
#  DISPATCHER
# ─────────────────────────────────────────────────────────────
def _run(expr: str) -> float:
    p = expr.split()
    if len(p)==1: return float(p[0])
    if len(p)==2 and p[0]=='sqrt': return square_root(float(p[1]))
    return procedural.calculate(expr)


class CalqApp(App):
    def build(self):
        self.title = 'CALQ'
        return CalcRoot()

if __name__ == '__main__':
    CalqApp().run()