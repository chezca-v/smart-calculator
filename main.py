from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.animation import Animation

# Import your massive calculator code from the ui folder
from ui.main import CalqRoot

class CalcuteApp(App):
    def build(self):
        self.title = 'Calcute'
        self.layout = FloatLayout()
        
        # Load the animated GIF of your friends
        self.splash = Image(source='friends.gif', anim_delay=0.1, allow_stretch=True, keep_ratio=False)
        self.layout.add_widget(self.splash)
        
        # Start a 3-second timer, then switch to the calculator
        Clock.schedule_once(self.load_calculator, 3.0)
        
        return self.layout

    def load_calculator(self, dt):
        # Fade out the splash screen smoothly
        anim = Animation(opacity=0, duration=0.5)
        anim.bind(on_complete=self.show_calc)
        anim.start(self.splash)

    def show_calc(self, *args):
        # Remove the GIF and load the real app
        self.layout.clear_widgets()
        self.layout.add_widget(CalqRoot())

if __name__ == '__main__':
    CalcuteApp().run()