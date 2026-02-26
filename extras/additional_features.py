import math
from typing import List, Tuple

# ── History tracker ──────────────────────────────────────────
_history: List[Tuple[str, float]] = []

def get_history() -> List[Tuple[str, float]]:
    return list(_history)

def clear_history():
    _history.clear()

def _record(expression: str, result: float):
    _history.append((expression, result))

# ── Extra math operations ─────────────────────────────────────
def exponentiate(base: float, exp: float) -> float:
    result = base ** exp
    _record(f"{base} ^ {exp}", result)
    return result

def square_root(n: float) -> float:
    if n < 0:
        raise ValueError("Cannot take square root of a negative number.")
    result = math.sqrt(n)
    _record(f"√{n}", result)
    return result

def percentage(value: float, percent: float) -> float:
    result = (value * percent) / 100.0
    _record(f"{value} × {percent}%", result)
    return result

def calculate(expression: str) -> float:
    """
    Supports extended expressions:
      'a ^ b'   -> exponentiation
      'sqrt a'  -> square root
      'a % b'   -> percentage of a that b represents
    Falls back to standard 'num op num' for +, -, *, /
    """
    parts = expression.strip().split()

    if len(parts) == 2 and parts[0].lower() == 'sqrt':
        return square_root(float(parts[1]))

    if len(parts) == 3:
        try:
            a = float(parts[0])
            op = parts[1]
            b = float(parts[2])
        except ValueError:
            raise ValueError("Invalid numbers in expression.")

        if op == '^':
            return exponentiate(a, b)
        if op == '%':
            return percentage(a, b)
        if op == '+':
            result = a + b
        elif op == '-':
            result = a - b
        elif op == '*':
            result = a * b
        elif op == '/':
            if b == 0:
                raise ValueError("Division by zero.")
            result = a / b
        else:
            raise ValueError(f"Unsupported operator: {op}")

        _record(expression, result)
        return result

    raise ValueError("Invalid expression format.")
