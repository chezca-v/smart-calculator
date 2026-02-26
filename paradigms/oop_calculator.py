# =========================
# FILE: paradigms/oop_calculator.py
# =========================

class Calculator:
    def __init__(self):
        self.num1 = 0.0
        self.num2 = 0.0

    def add(self):        return self.num1 + self.num2
    def subtract(self):   return self.num1 - self.num2
    def multiply(self):   return self.num1 * self.num2

    def divide(self):
        if self.num2 == 0:
            raise ValueError("Division by zero is not allowed.")
        return self.num1 / self.num2

    def modulus(self):
        if self.num2 == 0:
            raise ValueError("Modulus by zero is not allowed.")
        return self.num1 % self.num2

    def calculate(self, expression: str) -> float:
        parts = expression.strip().split()
        if len(parts) != 3:
            raise ValueError("Invalid format. Use 'num op num'.")
        try:
            self.num1 = float(parts[0])
            op = parts[1]
            self.num2 = float(parts[2])
        except ValueError:
            raise ValueError("Invalid numbers in expression.")

        ops = {
            '+': self.add,
            '-': self.subtract,
            '*': self.multiply,
            '/': self.divide,
            '%': self.modulus,
        }
        if op not in ops:
            raise ValueError(f"Unsupported operator: {op}")
        return ops[op]()
