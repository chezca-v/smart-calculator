import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from kivy.uix. textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window

from paradigms import procedural

class CalculatorUI(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=10, **kwargs)

        # Title
        self.add_widget(Label(text="Smart Arithmetic Calculator",
                              font_size=22,
                              size_hint=(1, 0.15)))

        # First number input
        self.num1 = TextInput(
            hint_text="Enter First Number",
            multiline=False,
            input_filter='float'
        )
        self.add_widget(self.num1)

        # Second number input
        self.num2 = TextInput(
            hint_text="Enter Second Number",
            multiline=False,
            input_filter='float'
        )
        self.add_widget(self.num2)

        # Operation selection
        self.operation_spinner = Spinner(
            text="Select Operation",
            values=["Add (+)", "Subtract (-)", "Multiply (*)", "Divide (/)", "Modulus (%)"],
            size_hint=(1, 0.12)
        )
        self.add_widget(self.operation_spinner)

        # Calculate button
        calc_button = Button(text="Calculate", size_hint=(1, 0.12))
        calc_button.bind(on_press=self.calculate)
        self.add_widget(calc_button)

        # Result Label
        self.result_label = Label(text="Result: ",
                                  font_size=18,
                                  size_hint=(1, 0.2))
        self.add_widget(self.result_label)

    def calculate(self, instance):
        try:
            num1 = float(self.num1.text)
            num2 = float(self.num2.text)
            operation = self.operation_spinner.text

            if operation == "Add (+)":
                result = procedural.add(num1, num2)
            elif operation == "Subtract (-)":
                result = procedural.subtract(num1, num2)
            elif operation == "Multiply (*)":
                result = procedural.multiply(num1, num2)
            elif operation == "Divide (/)":
                result = procedural.divide(num1, num2)
            elif operation == "Modulus (%)":
                result = procedural.modulus(num1, num2)
            else:
                result = "Please select an operation."

            self.result_label.text = f"Result: {result}"
        except ValueError:
            self.result_label.text = "Invalid input! Please enter numbers."