import os
import sys
from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.utils import get_color_from_hex

# Add current directory to path for clean imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from ui.main import CalqRoot
except ImportError:
    print("CRITICAL: Could not find ui/main.py. Verify your folder structure.")

class CalcuteApp(App):
    def build(self):
        self.title = 'Calcute'
        # Matching your Light Theme background color
        Window.clearcolor = get_color_from_hex('#FFF0F5')
        self.layout = FloatLayout()
        
        # Define the absolute path to your ZIP sequence
        base_path = os.path.dirname(os.path.abspath(__file__))
        zip_path = os.path.join(base_path, 'friends.zip')
        
        print(f"DEBUG: Loading sequence from: {zip_path}")
        
        if os.path.exists(zip_path):
            # Kivy plays the images inside the zip in alphabetical order
            self.splash = Image(
                source=zip_path, 
                anim_delay=0.1, 
                allow_stretch=True,
                keep_ratio=True
            )
        else:
            self.splash = Image(source='')
            print(f"ERROR: friends.zip missing at {zip_path}")

        self.layout.add_widget(self.splash)
        
        # Transition to calculator after 3 seconds
        Clock.schedule_once(self.load_calculator, 3.0)
        return self.layout

    def load_calculator(self, dt):
        # Smooth fade transition
        anim = Animation(opacity=0, duration=0.5)
        anim.bind(on_complete=self.show_calc)
        anim.start(self.splash)

    def show_calc(self, *args):
        self.layout.clear_widgets()
        try:
            self.layout.add_widget(CalqRoot())
        except Exception as e:
            print(f"ERROR: Failed to load CalqRoot: {e}")

if __name__ == '__main__':
    CalcuteApp().run()