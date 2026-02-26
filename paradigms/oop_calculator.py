# Smart Arithmetic Calculator - Object-Oriented Version

class Calculator:
    def __init__(self, num1, num2):
        self.num1 = num1
        self.num2 = num2

    def add(self):
        return self.num1 + self.num2

    def subtract(self):
        return self.num1 - self.num2

    def multiply(self):
        return self.num1 * self.num2

    def divide(self):
        if self.num2 == 0:
            return "Error: Division by zero is not allowed."
        return self.num1 / self.num2

    def modulus(self):
        if self.num2 == 0:
            return "Error: Modulus by zero is not allowed."
        return self.num1 % self.num2


def main():
    print("=== Smart Arithmetic Calculator (OOP) ===")

    try:
        num1 = float(input("Enter first number: "))
        num2 = float(input("Enter second number: "))
    except ValueError:
        print("Error: Please enter valid numeric values.")
        return

    operation = input("Choose operation (+, -, *, /, %): ")

    calculator = Calculator(num1, num2)

    if operation == "+":
        result = calculator.add()
    elif operation == "-":
        result = calculator.subtract()
    elif operation == "*":
        result = calculator.multiply()
    elif operation == "/":
        result = calculator.divide()
    elif operation == "%":
        result = calculator.modulus()
    else:
        print("Invalid operation selected.")
        return

    print("Result:", result)


if _name_ == "_main_":
    main()
