import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Rectangle, RoundedRectangle
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.properties import BooleanProperty

import paradigms.procedural    as procedural
import paradigms.functional    as functional
import paradigms.event_driven  as event_driven
from paradigms.oop_calculator   import Calculator
from extras.additional_features import square_root

Window.size = (400, 760)

# ─────────────────────────────────────────────────────────────
#  PALETTES
# ─────────────────────────────────────────────────────────────
DARK = {
    'bg':          '#1B2F3F',
    'btn_num':     '#243548',
    'btn_fn':      '#2E4255',
    'btn_op':      '#F5A623',
    'btn_eq':      '#F5A623',
    'text_result': '#FFFFFF',
    'text_expr':   '#4A6880',
    'text_num':    '#FFFFFF',
    'text_fn':     '#C0D2E0',
    'text_op':     '#FFFFFF',
    'toggle_icon': '☀',
}
LIGHT = {
    'bg':          '#E8EDF2',
    'btn_num':     '#FFFFFF',
    'btn_fn':      '#D2DCE8',
    'btn_op':      '#F5A623',
    'btn_eq':      '#F5A623',
    'text_result': '#1B2F3F',
    'text_expr':   '#8FA8BC',
    'text_num':    '#1B2F3F',
    'text_fn':     '#3A5266',
    'text_op':     '#FFFFFF',
    'toggle_icon': '🌙',
}

_OOP = Calculator()


def _c(h, a=1.0):
    r = get_color_from_hex(h)
    return (r[0], r[1], r[2], a)


# ─────────────────────────────────────────────────────────────
#  CIRCLE BUTTON
# ─────────────────────────────────────────────────────────────
class CircBtn(Button):
    def __init__(self, bg, fg, txt, fsz=24, **kw):
        super().__init__(**kw)
        self._bg = bg; self._fg = fg
        self.text = txt
        self.font_size = dp(fsz); self.bold = True
        self.color = _c(fg)
        self.background_normal = self.background_down = ''
        self.background_color = (0,0,0,0)
        self.bind(pos=self._d, size=self._d)

    def _d(self, *_):
        self.canvas.before.clear()
        w, h = self.size; x, y = self.pos
        d = min(w, h) * 0.92
        ox = x + (w-d)/2; oy = y + (h-d)/2
        with self.canvas.before:
            Color(0, 0, 0, 0.22)
            Ellipse(pos=(ox+dp(2), oy-dp(4)), size=(d,d))
            Color(*_c(self._bg))
            Ellipse(pos=(ox, oy), size=(d, d))

    def recolor(self, bg, fg):
        self._bg=bg; self._fg=fg; self.color=_c(fg); self._d()


# ─────────────────────────────────────────────────────────────
#  PILL BUTTON  (wide "0" key)
# ─────────────────────────────────────────────────────────────
class PillBtn(Button):
    def __init__(self, bg, fg, txt, fsz=24, **kw):
        super().__init__(**kw)
        self._bg=bg; self._fg=fg
        self.text=txt; self.font_size=dp(fsz); self.bold=True
        self.color=_c(fg)
        self.background_normal=self.background_down=''
        self.background_color=(0,0,0,0)
        self.halign='left'; self.valign='middle'
        self.bind(pos=self._d, size=self._d)
        self.bind(size=lambda *_: setattr(self,'text_size',(self.width,self.height)))
        self.padding_x = dp(28)

    def _d(self, *_):
        self.canvas.before.clear()
        h = self.height * 0.92
        r = h/2
        oy = self.y + (self.height - h)/2
        with self.canvas.before:
            Color(0,0,0,0.22)
            RoundedRectangle(pos=(self.x+dp(2), oy-dp(4)),
                             size=(self.width, h), radius=[dp(r)])
            Color(*_c(self._bg))
            RoundedRectangle(pos=(self.x, oy),
                             size=(self.width, h), radius=[dp(r)])

    def recolor(self, bg, fg):
        self._bg=bg; self._fg=fg; self.color=_c(fg); self._d()


# ─────────────────────────────────────────────────────────────
#  DISPLAY
# ─────────────────────────────────────────────────────────────
class Display(BoxLayout):
    def __init__(self, t, cb_toggle, **kw):
        super().__init__(orientation='vertical', **kw)
        self._t = t
        self.padding = [dp(22), dp(10), dp(22), dp(0)]
        self.spacing = dp(0)

        # ── top: toggle pill ─────────────
        top = BoxLayout(size_hint=(1, 0.20),
                        orientation='horizontal',
                        padding=[0, dp(6), 0, 0])
        self._tog = Button(
            text=t['toggle_icon'],
            font_size=dp(18),
            size_hint=(None, None), size=(dp(70), dp(28)),
            background_normal='', background_color=(0,0,0,0),
            color=(1,1,1,0.65),
        )
        self._tog.bind(pos=self._pill, size=self._pill)
        self._tog.bind(on_press=cb_toggle)
        top.add_widget(self._tog)
        top.add_widget(Widget())
        self.add_widget(top)

        # ── expression (dim) ─────────────
        self.expr = Label(
            text='', font_size=dp(18),
            halign='right', valign='bottom',
            size_hint=(1, 0.20),
            color=_c(t['text_expr']),
        )
        self.expr.bind(size=lambda *_: setattr(
            self.expr, 'text_size', (self.expr.width, None)))
        self.add_widget(self.expr)

        # ── result (big) ──────────────────
        self.result = Label(
            text='0', font_size=dp(66),
            halign='right', valign='bottom',
            size_hint=(1, 0.60),
            bold=True, color=_c(t['text_result']),
        )
        self.result.bind(size=lambda *_: setattr(
            self.result, 'text_size', (self.result.width, None)))
        self.add_widget(self.result)

        self.bind(pos=self._bg, size=self._bg)
        self._bg()

    def _bg(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*_c(self._t['bg']))
            Rectangle(pos=self.pos, size=self.size)

    def _pill(self, *_):
        b = self._tog
        b.canvas.before.clear()
        with b.canvas.before:
            Color(1,1,1,0.09)
            RoundedRectangle(pos=b.pos, size=b.size, radius=[dp(14)])

    def apply(self, t):
        self._t = t
        self.expr.color   = _c(t['text_expr'])
        self.result.color = _c(t['text_result'])
        self._tog.text    = t['toggle_icon']
        self._bg(); self._pill()


# ─────────────────────────────────────────────────────────────
#  ROOT
# ─────────────────────────────────────────────────────────────
class CalcRoot(BoxLayout):
    dark = BooleanProperty(True)

    ROWS = [
        [('AC','fn'),('+/-','fn'),('←','fn'),('/','op')],
        [('7','num'),('8','num'),('9','num'),('×','op')],
        [('4','num'),('5','num'),('6','num'),('−','op')],
        [('1','num'),('2','num'),('3','num'),('+','op')],
        [('0','wide'),           ('.','num'),('=','eq')],
    ]

    def __init__(self, **kw):
        super().__init__(orientation='vertical', **kw)
        self._t   = DARK
        self._e   = ''
        self._jr  = False
        self._all = []
        self._build()

    def _build(self):
        self._disp = Display(self._t, self._toggle, size_hint=(1, 0.30))
        self.add_widget(self._disp)

        p = dp(14)
        g = BoxLayout(orientation='vertical', size_hint=(1, 0.70),
                      padding=[p, dp(2), p, dp(20)], spacing=dp(12))

        for row_spec in self.ROWS:
            row = BoxLayout(orientation='horizontal', spacing=dp(12))
            for lbl, kind in row_spec:
                w = self._btn(lbl, kind)
                if kind == 'wide':
                    w.size_hint_x = 2.2
                row.add_widget(w)
                self._all.append((w, 'num' if kind=='wide' else kind))
            g.add_widget(row)

        self.add_widget(g)
        self.bind(pos=self._bg, size=self._bg)
        self._bg()

    def _btn(self, lbl, kind):
        t = self._t
        lu = {
            'num': (t['btn_num'], t['text_num']),
            'wide':(t['btn_num'], t['text_num']),
            'fn':  (t['btn_fn'],  t['text_fn']),
            'op':  (t['btn_op'],  t['text_op']),
            'eq':  (t['btn_eq'],  t['text_op']),
        }
        bg, fg = lu.get(kind, lu['num'])
        fsz = 20 if len(lbl)>1 else 24
        if kind == 'wide':
            w = PillBtn(bg, fg, lbl, fsz=fsz, size_hint=(1,1))
        else:
            w = CircBtn(bg, fg, lbl, fsz=fsz, size_hint=(1,1))
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
        lu = {'num':(t['btn_num'],t['text_num']),
              'fn': (t['btn_fn'], t['text_fn']),
              'op': (t['btn_op'], t['text_op']),
              'eq': (t['btn_eq'], t['text_op'])}
        for w, kind in self._all:
            bg, fg = lu.get(kind, lu['num'])
            w.recolor(bg, fg)

    def _key(self, key):
        D = self._disp
        if key == 'AC':
            self._e=''; self._jr=False
            D.result.text='0'; D.expr.text=''; return
        if key == '←':
            e = self._e.rstrip()
            e = e[:-1].rstrip() if (e and e[-1] in '+-*/%^') else e[:-1] if e else e
            self._e=e; D.result.text=e.strip() or '0'; return
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

        sym = {'×':'*','−':'-'}.get(key, key)
        is_op = sym in '+-*/%^'

        if self._jr:
            self._e = sym if is_op and not sym.isdigit() else ''
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
            out = str(int(r)) if r==int(r) else f'{r:.8g}'
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
    if len(p)==2 and p[0]=='√': return square_root(float(p[1]))
    return procedural.calculate(expr)


class SmartCalcApp(App):
    def build(self):
        self.title = 'Smart Calculator'
        return CalcRoot()

if __name__ == '__main__':
    SmartCalcApp().run()