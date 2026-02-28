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
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line, Ellipse
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.animation import Animation
from kivy.properties import BooleanProperty, NumericProperty
from kivy.clock import Clock

import paradigms.procedural   as procedural
from paradigms.oop_calculator   import Calculator
from extras.additional_features import (
    calculate as extra_calculate,
    square_root,
    percentage,
    get_history,
    clear_history,
)
Window.size = (400, 760)

# ──────────────────────────────────────────────────────────────
#  THEMES
# ──────────────────────────────────────────────────────────────
DARK = {
    'bg':          '#111318',
    'display_bg':  '#1A1D24',
    'btn_num':     '#22262F',
    'btn_fn':      '#1A1D24',
    'btn_sci':     '#1E222A',
    'btn_op':      '#C8873A',
    'btn_eq':      '#C8873A',
    'num_text':    '#E8E2D9',
    'fn_text':     '#6A7484',
    'sci_text':    '#8A9AAE',
    'op_text':     '#FFFFFF',
    'result_text': '#F0EBE3',
    'expr_text':   '#363C48',
    'app_name':    '#363C48',
    'toggle_bg':   '#22262F',
    'toggle_text': '#6A7484',
    'tab_active':  '#C8873A',
    'tab_inactive':'#363C48',
    'tab_text_on': '#FFFFFF',
    'tab_text_off':'#6A7484',
    'conv_bg':     '#1A1D24',
    'conv_input':  '#22262F',
    'conv_text':   '#E8E2D9',
    'divider':     '#22262F',
    'tray_handle': '#2A2F3A',
    'mini_bg':     '#1A1D24',
    'mini_text':   '#F0EBE3',
    'mini_btn':    '#C8873A',
}
LIGHT = {
    'bg':          '#F0EBE3',
    'display_bg':  '#FFFDF8',
    'btn_num':     '#FFFFFF',
    'btn_fn':      '#E8E3D8',
    'btn_sci':     '#EDE8DE',
    'btn_op':      '#C8873A',
    'btn_eq':      '#C8873A',
    'num_text':    '#1A1C22',
    'fn_text':     '#8A8070',
    'sci_text':    '#6A7888',
    'op_text':     '#FFFFFF',
    'result_text': '#1A1C22',
    'expr_text':   '#C0B8A8',
    'app_name':    '#C0B8A8',
    'toggle_bg':   '#E8E3D8',
    'toggle_text': '#8A8070',
    'tab_active':  '#C8873A',
    'tab_inactive':'#DDD8CE',
    'tab_text_on': '#FFFFFF',
    'tab_text_off':'#8A8070',
    'conv_bg':     '#FFFDF8',
    'conv_input':  '#FFFFFF',
    'conv_text':   '#1A1C22',
    'divider':     '#E8E3D8',
    'tray_handle': '#DDD8CE',
    'mini_bg':     '#1A1D24',
    'mini_text':   '#F0EBE3',
    'mini_btn':    '#C8873A',
}

_OOP = Calculator()


def _c(h, a=1.0):
    r = get_color_from_hex(h)
    return (r[0], r[1], r[2], a)


# ──────────────────────────────────────────────────────────────
#  TILE BUTTON
# ──────────────────────────────────────────────────────────────
class Tile(Button):
    def __init__(self, bg, fg, txt, fsz=22, r=14, **kw):
        super().__init__(**kw)
        self._bg = bg; self._fg = fg; self._r = r
        self.text = txt
        self.font_size = dp(fsz); self.bold = True
        self.color = _c(fg)
        self.background_normal = self.background_down = ''
        self.background_color = (0,0,0,0)
        self.bind(pos=self._d, size=self._d)

    def _d(self, *_):
        self.canvas.before.clear()
        x,y,w,h = self.x,self.y,self.width,self.height
        r = dp(self._r)
        with self.canvas.before:
            Color(0,0,0,0.30)
            RoundedRectangle(pos=(x+dp(2),y-dp(4)), size=(w,h), radius=[r])
            Color(*_c(self._bg))
            RoundedRectangle(pos=(x,y), size=(w,h), radius=[r])
            Color(1,1,1,0.05)
            Line(rounded_rectangle=(x+1,y+1,w-2,h-2,r), width=1)

    def on_press(self):
        (Animation(opacity=0.55,duration=0.05)+Animation(opacity=1,duration=0.1)).start(self)

    def recolor(self, bg, fg):
        self._bg=bg; self._fg=fg; self.color=_c(fg); self._d()


class Pill(Button):
    def __init__(self, bg, fg, txt='0', fsz=22, **kw):
        super().__init__(**kw)
        self._bg=bg; self._fg=fg
        self.text=txt; self.font_size=dp(fsz); self.bold=True
        self.color=_c(fg)
        self.background_normal=self.background_down=''
        self.background_color=(0,0,0,0)
        self.halign='left'; self.valign='middle'
        self.padding_x=dp(26)
        self.bind(pos=self._d,size=self._d)
        self.bind(size=lambda *_: setattr(self,'text_size',(self.width,self.height)))

    def _d(self,*_):
        self.canvas.before.clear()
        x,y,w,h=self.x,self.y,self.width,self.height
        r=dp(h*0.38)
        with self.canvas.before:
            Color(0,0,0,0.30)
            RoundedRectangle(pos=(x+dp(2),y-dp(4)),size=(w,h),radius=[r])
            Color(*_c(self._bg))
            RoundedRectangle(pos=(x,y),size=(w,h),radius=[r])
            Color(1,1,1,0.05)
            Line(rounded_rectangle=(x+1,y+1,w-2,h-2,r),width=1)

    def on_press(self):
        (Animation(opacity=0.55,duration=0.05)+Animation(opacity=1,duration=0.1)).start(self)

    def recolor(self,bg,fg):
        self._bg=bg;self._fg=fg;self.color=_c(fg);self._d()


# ──────────────────────────────────────────────────────────────
#  DISPLAY AREA
# ──────────────────────────────────────────────────────────────
class Display(BoxLayout):
    def __init__(self, t, toggle_cb, **kw):
        super().__init__(orientation='vertical', **kw)
        self._t = t
        self.padding = [dp(24),dp(16),dp(24),dp(10)]
        self.spacing = dp(0)

        top = BoxLayout(size_hint=(1,0.22), orientation='horizontal',
                        spacing=dp(8))

        self._name = Label(text='CALQ', font_size=dp(11), bold=True,
                           halign='left', valign='middle',
                           color=_c(t['app_name']),
                           size_hint=(None,1), width=dp(60))
        self._name.bind(size=lambda *_: setattr(
            self._name,'text_size',(self._name.width,None)))

        self._tog = Button(
            text='LIGHT', font_size=dp(9), bold=True,
            size_hint=(None,None), size=(dp(58),dp(24)),
            background_normal='', background_color=(0,0,0,0),
            color=_c(t['toggle_text']),
        )
        self._tog.bind(pos=self._tog_draw, size=self._tog_draw)
        self._tog.bind(on_press=toggle_cb)

        top.add_widget(self._name)
        top.add_widget(Widget())
        top.add_widget(self._tog)
        self.add_widget(top)

        self.expr = Label(text='', font_size=dp(14),
                          halign='right', valign='bottom',
                          size_hint=(1,0.18), color=_c(t['expr_text']))
        self.expr.bind(size=lambda *_: setattr(
            self.expr,'text_size',(self.expr.width,None)))
        self.add_widget(self.expr)

        self.result = Label(text='0', font_size=dp(62),
                            halign='right', valign='bottom',
                            size_hint=(1,0.60), bold=True,
                            color=_c(t['result_text']))
        self.result.bind(size=lambda *_: setattr(
            self.result,'text_size',(self.result.width,None)))
        self.add_widget(self.result)

        self.bind(pos=self._bg, size=self._bg)
        self._bg()

    def _tog_draw(self,*_):
        b=self._tog; b.canvas.before.clear()
        with b.canvas.before:
            Color(*_c(self._t['toggle_bg']))
            RoundedRectangle(pos=b.pos,size=b.size,radius=[dp(12)])

    def _bg(self,*_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*_c(self._t['display_bg']))
            RoundedRectangle(pos=self.pos,size=self.size,
                             radius=[0,0,dp(22),dp(22)])
            Color(*_c(self._t['divider']))
            Line(points=[self.x+dp(18),self.y+dp(1),
                         self.right-dp(18),self.y+dp(1)],width=1)

    def apply(self,t):
        self._t=t
        self._name.color=_c(t['app_name'])
        self.expr.color=_c(t['expr_text'])
        self.result.color=_c(t['result_text'])
        self._tog.text='DARK' if t is LIGHT else 'LIGHT'
        self._tog.color=_c(t['toggle_text'])
        self._bg(); self._tog_draw()


# ──────────────────────────────────────────────────────────────
#  SCIENTIFIC TRAY  (slides up from bottom)
# ──────────────────────────────────────────────────────────────
SCI_BTNS = [
    ['sin','cos','tan','log','ln'],
    ['x^y','sqrt','1/x','x!','%'],
    ['HIS','HC'],
]

class SciTray(BoxLayout):
    def __init__(self, t, on_sci, **kw):
        super().__init__(orientation='vertical', **kw)
        self._t = t
        self.padding = [dp(14),dp(6),dp(14),dp(4)]
        self.spacing = dp(8)

        # handle bar
        handle_row = BoxLayout(size_hint=(1,None), height=dp(18))
        handle_row.add_widget(Widget())
        handle = Widget(size_hint=(None,None), size=(dp(40),dp(4)))
        handle.bind(pos=self._handle_draw, size=self._handle_draw)
        self._handle = handle
        handle_row.add_widget(handle)
        handle_row.add_widget(Widget())
        self.add_widget(handle_row)

        for row_btns in SCI_BTNS:
            row = BoxLayout(orientation='horizontal',
                            spacing=dp(8), size_hint=(1,1))
            for lbl in row_btns:
                b = Tile(t['btn_sci'], t['sci_text'], lbl,
                         fsz=14, r=12, size_hint=(1,1))
                b.bind(on_press=lambda btn, l=lbl: on_sci(l))
                row.add_widget(b)
            self.add_widget(row)

        self.bind(pos=self._bg, size=self._bg)
        self._bg()

    def _handle_draw(self,*_):
        h=self._handle; h.canvas.clear()
        with h.canvas:
            Color(*_c(self._t['tray_handle']))
            RoundedRectangle(pos=h.pos,size=h.size,radius=[dp(2)])

    def _bg(self,*_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*_c(self._t['display_bg']))
            RoundedRectangle(pos=self.pos,size=self.size,
                             radius=[dp(18),dp(18),0,0])

    def apply(self,t):
        self._t=t; self._bg(); self._handle_draw()


# ──────────────────────────────────────────────────────────────
#  CONVERTER TAB
# ──────────────────────────────────────────────────────────────
CONV_CATS = {
    'Length':      {'m':1,'km':1000,'cm':0.01,'mm':0.001,
                    'mi':1609.34,'ft':0.3048,'in':0.0254},
    'Mass':        {'kg':1,'g':0.001,'lb':0.453592,'oz':0.0283495,'t':1000},
    'Temperature': {'C':1,'F':1,'K':1},   # handled specially
    'Speed':       {'m/s':1,'km/h':1/3.6,'mph':0.44704,'knot':0.514444},
    'Area':        {'m2':1,'km2':1e6,'cm2':1e-4,'ft2':0.092903,'ac':4046.86},
    'Volume':      {'L':1,'mL':0.001,'m3':1000,'gal':3.78541,'fl oz':0.0295735},
    'Data':        {'B':1,'KB':1024,'MB':1048576,'GB':1073741824,'TB':1099511627776},
    'Time':        {'s':1,'min':60,'hr':3600,'day':86400,'wk':604800},
}

def _convert(val, from_u, to_u, cat):
    if cat == 'Temperature':
        if from_u == to_u: return val
        if from_u=='C' and to_u=='F': return val*9/5+32
        if from_u=='F' and to_u=='C': return (val-32)*5/9
        if from_u=='C' and to_u=='K': return val+273.15
        if from_u=='K' and to_u=='C': return val-273.15
        if from_u=='F' and to_u=='K': return (val-32)*5/9+273.15
        if from_u=='K' and to_u=='F': return (val-273.15)*9/5+32
        return val
    units = CONV_CATS[cat]
    base  = val * units[from_u]
    return base / units[to_u]


class ConverterView(BoxLayout):
    def __init__(self, t, **kw):
        super().__init__(orientation='vertical', **kw)
        self._t   = t
        self._cat = 'Length'
        self.padding  = [dp(18),dp(16),dp(18),dp(16)]
        self.spacing  = dp(12)

        # category row
        cat_scroll = ScrollView(size_hint=(1,None), height=dp(44),
                                do_scroll_y=False)
        self._cat_row = BoxLayout(orientation='horizontal',
                                  size_hint=(None,1),
                                  spacing=dp(8))
        self._cat_row.bind(minimum_width=self._cat_row.setter('width'))
        for cat in CONV_CATS:
            b = Button(text=cat, font_size=dp(12), bold=True,
                       size_hint=(None,1), width=dp(80),
                       background_normal='', background_color=(0,0,0,0))
            b.bind(pos=lambda w,_,b=b: self._cat_btn_draw(b),
                   size=lambda w,_,b=b: self._cat_btn_draw(b))
            b.bind(on_press=lambda btn, c=cat: self._set_cat(c))
            self._cat_row.add_widget(b)
        cat_scroll.add_widget(self._cat_row)
        self.add_widget(cat_scroll)

        # input
        self._val_in = TextInput(
            hint_text='Enter value', font_size=dp(22),
            size_hint=(1,None), height=dp(56),
            input_filter='float', multiline=False,
            background_normal='', background_color=_c(t['conv_input']),
            foreground_color=_c(t['conv_text']),
            cursor_color=_c(t['btn_op']),
            padding=[dp(14),dp(14)],
        )
        self.add_widget(self._val_in)

        # from/to row
        unit_row = BoxLayout(orientation='horizontal',
                             size_hint=(1,None), height=dp(48),
                             spacing=dp(10))
        units = list(CONV_CATS[self._cat].keys())
        self._from = Spinner(text=units[0], values=units,
                             font_size=dp(14),
                             background_normal='',
                             background_color=_c(t['btn_fn']),
                             color=_c(t['conv_text']),
                             size_hint=(1,1))
        arr = Label(text='->',font_size=dp(18),bold=True,
                    color=_c(t['btn_op']),size_hint=(None,1),width=dp(28))
        self._to = Spinner(text=units[1] if len(units)>1 else units[0],
                           values=units,
                           font_size=dp(14),
                           background_normal='',
                           background_color=_c(t['btn_fn']),
                           color=_c(t['conv_text']),
                           size_hint=(1,1))
        unit_row.add_widget(self._from)
        unit_row.add_widget(arr)
        unit_row.add_widget(self._to)
        self.add_widget(unit_row)
        self._arr = arr

        # convert button
        go = Tile(t['btn_op'], t['op_text'], 'Convert',
                  fsz=16, r=14, size_hint=(1,None))
        go.height = dp(50)
        go.bind(on_press=lambda *_: self._do_convert())
        self.add_widget(go)
        self._go = go

        # result
        self._res = Label(text='', font_size=dp(30),
                          bold=True, halign='center',
                          color=_c(t['result_text']),
                          size_hint=(1,1))
        self._res.bind(size=lambda *_: setattr(
            self._res,'text_size',(self._res.width,None)))
        self.add_widget(self._res)

        self.bind(pos=self._bg, size=self._bg)
        self._bg()
        self._highlight_cat()

    def _cat_btn_draw(self,b):
        b.canvas.before.clear()
        active = (b.text == self._cat)
        bg = self._t['tab_active'] if active else self._t['btn_fn']
        fg = self._t['tab_text_on'] if active else self._t['fn_text']
        b.color = _c(fg)
        with b.canvas.before:
            Color(*_c(bg))
            RoundedRectangle(pos=b.pos,size=b.size,radius=[dp(10)])

    def _highlight_cat(self):
        for b in self._cat_row.children:
            self._cat_btn_draw(b)

    def _set_cat(self, cat):
        self._cat = cat
        units = list(CONV_CATS[cat].keys())
        self._from.values = units
        self._to.values   = units
        self._from.text   = units[0]
        self._to.text     = units[1] if len(units)>1 else units[0]
        self._res.text    = ''
        self._highlight_cat()

    def _do_convert(self):
        try:
            val = float(self._val_in.text)
            res = _convert(val, self._from.text, self._to.text, self._cat)
            r   = int(res) if res == int(res) else round(res, 8)
            self._res.text = f'{val} {self._from.text}  =  {r} {self._to.text}'
        except Exception as e:
            self._res.text = f'Error: {e}'

    def _bg(self,*_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*_c(self._t['bg']))
            Rectangle(pos=self.pos,size=self.size)

    def apply(self,t):
        self._t=t
        self._val_in.background_color=_c(t['conv_input'])
        self._val_in.foreground_color=_c(t['conv_text'])
        self._from.background_color=_c(t['btn_fn'])
        self._from.color=_c(t['conv_text'])
        self._to.background_color=_c(t['btn_fn'])
        self._to.color=_c(t['conv_text'])
        self._arr.color=_c(t['btn_op'])
        self._res.color=_c(t['result_text'])
        self._go.recolor(t['btn_op'],t['op_text'])
        self._bg(); self._highlight_cat()


# ──────────────────────────────────────────────────────────────
#  MINI FLOATING BUBBLE
# ──────────────────────────────────────────────────────────────
MINI_W  = dp(180)
MINI_H  = dp(80)

class MiniBubble(BoxLayout):
    """
    Draggable mini calculator. Stays at last position.
    Shows current expression/result + basic num input.
    """
    def __init__(self, t, on_restore, on_key, get_display, **kw):
        super().__init__(orientation='horizontal', **kw)
        self._t          = t
        self._on_restore = on_restore
        self._on_key     = on_key
        self._get_display= get_display
        self._touch_ox   = 0
        self._touch_oy   = 0

        self.size_hint = (None,None)
        self.size      = (MINI_W, MINI_H)
        self.pos       = (Window.width - MINI_W - dp(10),
                          Window.height//2 - MINI_H//2)
        self.padding   = [dp(8),dp(6),dp(8),dp(6)]
        self.spacing   = dp(6)

        # result label
        self._lbl = Label(
            text='0', font_size=dp(22), bold=True,
            halign='right', valign='middle',
            color=_c(t['mini_text']),
            size_hint=(1,1),
        )
        self._lbl.bind(size=lambda *_: setattr(
            self._lbl,'text_size',(self._lbl.width,None)))
        self.add_widget(self._lbl)

        # restore button
        rb = Button(
            text='[ ]', font_size=dp(11), bold=True,
            size_hint=(None,None), size=(dp(32),dp(32)),
            background_normal='', background_color=(0,0,0,0),
            color=_c(t['mini_btn']),
        )
        rb.bind(on_press=lambda *_: on_restore())
        self.add_widget(rb)

        self.bind(pos=self._bg, size=self._bg)
        self._bg()

    def _bg(self,*_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0,0,0,0.55)
            RoundedRectangle(pos=(self.x+dp(3),self.y-dp(4)),
                             size=self.size, radius=[dp(20)])
            Color(*_c(self._t['mini_bg']))
            RoundedRectangle(pos=self.pos,size=self.size,radius=[dp(20)])
            Color(*_c(self._t['mini_btn'],0.6))
            Line(rounded_rectangle=(self.x+1,self.y+1,
                                    self.width-2,self.height-2,dp(20)),
                 width=1)

    def update_text(self, txt):
        self._lbl.text = txt

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._touch_ox = touch.x - self.x
            self._touch_oy = touch.y - self.y
            touch.grab(self)
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            nx = touch.x - self._touch_ox
            ny = touch.y - self._touch_oy
            # clamp to window
            nx = max(0, min(nx, Window.width  - self.width))
            ny = max(0, min(ny, Window.height - self.height))
            self.pos = (nx, ny)
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            return True
        return super().on_touch_up(touch)


# ──────────────────────────────────────────────────────────────
#  CALCULATOR PAGE
# ──────────────────────────────────────────────────────────────
MAIN_ROWS = [
    [('AC','fn'),('+/-','fn'),('DEL','fn'),('/','op')],
    [('7','num'),('8','num'), ('9','num'), ('x','op')],
    [('4','num'),('5','num'), ('6','num'), ('-','op')],
    [('1','num'),('2','num'), ('3','num'), ('+','op')],
    [('SCI','sci'),('0','wide'),           ('.','num'),('=','eq')],
]

class CalcPage(BoxLayout):
    def __init__(self, t, toggle_cb, minimize_cb, **kw):
        super().__init__(orientation='vertical', **kw)
        self._t         = t
        self._minimize  = minimize_cb
        self._e         = ''
        self._jr        = False
        self._sci_open  = False
        self._tiles     = []

        # display
        self._disp = Display(t, toggle_cb, size_hint=(1,0.28))
        self.add_widget(self._disp)

        # sci tray (hidden by default, height=0)
        self._tray = SciTray(t, self._sci_key,
                             size_hint=(1,None), height=0, opacity=0)
        self.add_widget(self._tray)

        # button grid
        pad = dp(12)
        self._grid = BoxLayout(
            orientation='vertical', size_hint=(1,1),
            padding=[pad,dp(6),pad,dp(18)], spacing=dp(9),
        )
        self._build_grid()
        self.add_widget(self._grid)

        self.bind(pos=self._bg, size=self._bg)
        self._bg()

    def _build_grid(self):
        self._grid.clear_widgets()
        self._tiles.clear()
        t = self._t
        for row_spec in MAIN_ROWS:
            row = BoxLayout(orientation='horizontal', spacing=dp(9))
            for lbl, kind in row_spec:
                w = self._make_btn(lbl, kind)
                if kind == 'wide':
                    w.size_hint_x = 2.1
                row.add_widget(w)
                self._tiles.append((w, 'num' if kind=='wide' else kind))
            self._grid.add_widget(row)

    def _make_btn(self, lbl, kind):
        t   = self._t
        fsz = 16 if len(lbl)>1 else 22
        lu  = {
            'num':  (t['btn_num'], t['num_text']),
            'wide': (t['btn_num'], t['num_text']),
            'fn':   (t['btn_fn'],  t['fn_text']),
            'sci':  (t['btn_sci'], t['sci_text']),
            'op':   (t['btn_op'],  t['op_text']),
            'eq':   (t['btn_eq'],  t['op_text']),
        }
        bg, fg = lu.get(kind, lu['num'])
        if kind == 'wide':
            w = Pill(bg, fg, lbl, fsz=22, size_hint=(1,1))
        else:
            w = Tile(bg, fg, lbl, fsz=fsz, r=14, size_hint=(1,1))
        w.bind(on_press=lambda b: self._key(b.text))
        return w

    def _bg(self,*_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*_c(self._t['bg']))
            Rectangle(pos=self.pos,size=self.size)

    def toggle_sci(self):
        self._sci_open = not self._sci_open
        target_h  = dp(120) if self._sci_open else 0
        target_op = 1.0     if self._sci_open else 0.0
        Animation(height=target_h, opacity=target_op,
                  duration=0.22, t='out_cubic').start(self._tray)

    def apply_theme(self, t):
        self._t = t
        self._disp.apply(t)
        self._tray.apply(t)
        self._bg()
        lu = {
            'num': (t['btn_num'], t['num_text']),
            'fn':  (t['btn_fn'],  t['fn_text']),
            'sci': (t['btn_sci'], t['sci_text']),
            'op':  (t['btn_op'],  t['op_text']),
            'eq':  (t['btn_eq'],  t['op_text']),
        }
        for w, kind in self._tiles:
            bg, fg = lu.get(kind, lu['num'])
            w.recolor(bg, fg)

    def get_display_text(self):
        return self._disp.result.text

    # ── key handling ──────────────────────────────────────────
    def _key(self, key):
        if key == 'SCI':
            self.toggle_sci(); return

        D = self._disp
        if key == 'AC':
            self._e=''; self._jr=False
            D.result.text='0'; D.expr.text=''; return

        if key == 'DEL':
            e = self._e.rstrip()
            if e and e[-1] in '+-*/%^':
                e = e[:-1].rstrip()
            elif e:
                e = e[:-1]
            self._e=e; D.result.text=e.strip() or '0'; return

        if key == '=':
            self._eval(); return
        
        if key == 'HIS':
            self._show_history(); return


        if key == '+/-':
            parts=self._e.strip().split()
            if parts:
                try:
                    v=float(parts[-1]); v=-v
                    parts[-1]=str(int(v) if v==int(v) else v)
                    self._e=' '.join(parts); D.result.text=self._e
                except ValueError: pass
            return

        sym = {'x':'*'}.get(key, key)
        is_op = sym in '+-*/%^'

        if self._jr:
            self._e = D.result.text+' '+sym+' ' if is_op else sym
            self._jr=False
        else:
            if is_op:
                s=self._e.rstrip(); toks=s.split()
                if toks and toks[-1] in '+-*/%^':
                    toks[-1]=sym; self._e=' '.join(toks)+' '
                else:
                    self._e=s+' '+sym+' '
            else:
                self._e+=sym

        D.result.text=self._e.strip() or '0'
        D.expr.text=''

    def _sci_key(self, fn):
        D  = self._disp
        ex = self._e.strip()
        try:
            val = float(ex) if ex else 0.0
        except ValueError:
            val = 0.0

        try:
            if fn=='sin':   res=math.sin(math.radians(val))
            elif fn=='cos': res=math.cos(math.radians(val))
            elif fn=='tan': res=math.tan(math.radians(val))
            elif fn=='log': res=math.log10(val)
            elif fn=='ln':  res=math.log(val)
            elif fn=='x^y':
                D.expr.text=f'{ex} ^'; self._e=ex+' ^ '; return
            elif fn=='sqrt': res=square_root(val)
            elif fn=='1/x':  res=1/val
            elif fn=='x!':   res=float(math.factorial(int(val)))
            elif fn=='%':    res=percentage(val, 1)
            elif fn=='HIS':
                self._show_history(); return
            elif fn=='HC':
                clear_history()
                D.expr.text='History cleared'
                return
            else: return
            out=str(int(res)) if res==int(res) else f'{res:.8g}'
            D.expr.text=f'{fn}({ex})'
            D.result.text=out; self._e=out; self._jr=True
        except Exception as e:
            D.result.text='Error'; D.expr.text=str(e)
            self._e=''; self._jr=False
    
    def _show_history(self):
        hist = get_history()
        if not hist:
            self._disp.expr.text = 'History is empty'
            self._disp.result.text = '0'
            return

        last_items = hist[-3:]
        compact = ' | '.join(f"{expr}={res:.8g}" for expr, res in last_items)
        last_expr, last_res = hist[-1]
        self._disp.expr.text = compact
        self._disp.result.text = str(int(last_res)) if last_res == int(last_res) else f'{last_res:.8g}'
        self._e = str(last_res)
        self._jr = True

    def _eval(self):
        expr=self._e.strip()
        if not expr: return
        self._disp.expr.text=expr
        try:
            r=_run(expr)
            out=str(int(r)) if r==int(r) else f'{r:.8g}'
            self._disp.result.text=out
            self._e=out; self._jr=True
        except Exception as ex:
            self._disp.result.text='Error'
            self._disp.expr.text=str(ex)
            self._e=''; self._jr=False


# ──────────────────────────────────────────────────────────────
#  TAB BAR
# ──────────────────────────────────────────────────────────────
class TabBar(BoxLayout):
    def __init__(self, t, on_tab, **kw):
        kw.setdefault('size_hint', (1, None))
        kw.setdefault('height', dp(44))
        super().__init__(orientation='horizontal', **kw)
        self._t      = t
        self._on_tab = on_tab
        self._btns   = {}
        self.padding = [dp(16),dp(6),dp(16),dp(0)]
        self.spacing = dp(0)

        for label in ['Calculator','Converter']:
            b = Button(
                text=label, font_size=dp(13), bold=True,
                size_hint=(1,1),
                background_normal='', background_color=(0,0,0,0),
            )
            b.bind(on_press=lambda btn, l=label: self._tap(l))
            self._btns[label] = b
            self.add_widget(b)

        self._active = 'Calculator'
        self._update()
        self.bind(pos=self._bg, size=self._bg)
        self._bg()

    def _tap(self, label):
        self._active=label; self._update(); self._on_tab(label)

    def _update(self):
        t=self._t
        for lbl,b in self._btns.items():
            active=(lbl==self._active)
            b.color=_c(t['tab_text_on'] if active else t['tab_text_off'])
            b.bold=active

    def _bg(self,*_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*_c(self._t['display_bg']))
            Rectangle(pos=self.pos,size=self.size)
            # underline indicator
            for lbl,b in self._btns.items():
                if lbl==self._active:
                    Color(*_c(self._t['tab_active']))
                    Line(points=[b.x+dp(12),self.y+dp(2),
                                 b.right-dp(12),self.y+dp(2)],
                         width=dp(2))

    def apply(self,t):
        self._t=t; self._update(); self._bg()


# ──────────────────────────────────────────────────────────────
#  ROOT  —  FloatLayout so mini bubble can float freely
# ──────────────────────────────────────────────────────────────
class CalqRoot(FloatLayout):
    dark = BooleanProperty(True)

    def __init__(self, **kw):
        super().__init__(**kw)
        self._t        = DARK
        self._mini_mode= False
        self._mini     = None
        self._build()

    def _build(self):
        # full-app shell (fills the float)
        self._shell = BoxLayout(orientation='vertical',
                                size_hint=(1,1), pos=(0,0))

        # tab bar
        self._tabs = TabBar(self._t, self._on_tab)
        self._shell.add_widget(self._tabs)

        # pages container
        self._pages = BoxLayout(orientation='horizontal', size_hint=(1,1))
        self._calc_page = CalcPage(self._t, self._toggle,
                                   self._go_mini, size_hint=(1,1))
        self._conv_page = ConverterView(self._t, size_hint=(1,1))
        self._pages.add_widget(self._calc_page)
        self._shell.add_widget(self._pages)

        self.add_widget(self._shell)

    def _on_tab(self, label):
        self._pages.clear_widgets()
        if label == 'Calculator':
            self._pages.add_widget(self._calc_page)
        else:
            self._pages.add_widget(self._conv_page)

    def _toggle(self, *_):
        self.dark = not self.dark
        self._t   = DARK if self.dark else LIGHT
        self._tabs.apply(self._t)
        self._calc_page.apply_theme(self._t)
        self._conv_page.apply(self._t)
        if self._mini:
            self._mini._t = self._t
            self._mini._bg()

    def _go_mini(self, *_):
        if self._mini_mode: return
        self._mini_mode = True
        # shrink shell
        Animation(size_hint_y=None, height=0,
                  opacity=0, duration=0.2).start(self._shell)

        self._mini = MiniBubble(
            self._t,
            on_restore  = self._restore,
            on_key      = self._calc_page._key,
            get_display = self._calc_page.get_display_text,
            size_hint   = (None, None),
        )
        self._mini.update_text(self._calc_page.get_display_text())
        self.add_widget(self._mini)
        # keep display in sync
        self._sync_ev = Clock.schedule_interval(self._sync_mini, 0.25)

    def _sync_mini(self, *_):
        if self._mini:
            self._mini.update_text(self._calc_page.get_display_text())

    def _restore(self, *_):
        if not self._mini_mode: return
        self._mini_mode = False
        if hasattr(self,'_sync_ev'):
            self._sync_ev.cancel()
        self.remove_widget(self._mini)
        self._mini = None
        self._shell.size_hint_y = 1
        self._shell.opacity    = 0
        self._shell.height     = self.height
        Animation(opacity=1, duration=0.18).start(self._shell)


# ──────────────────────────────────────────────────────────────
#  DISPATCHER
# ──────────────────────────────────────────────────────────────
def _run(expr: str) -> float:
    # Route through extras.additional_features so exponentiation, square root,
    # percentage, retry normalization, and history tracking stay aligned.
    return extra_calculate(expr)


# ──────────────────────────────────────────────────────────────
#  APP
# ──────────────────────────────────────────────────────────────
class CalqApp(App):
    def build(self):
        self.title = 'CALQ'
        return CalqRoot()

if __name__ == '__main__':
    CalqApp().run()