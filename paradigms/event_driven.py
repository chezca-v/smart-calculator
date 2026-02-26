from typing import Callable, Dict, List

_listeners: Dict[str, List[Callable]] = {}

def on(event: str, callback: Callable):
    _listeners.setdefault(event, []).append(callback)

def emit(event: str, data=None):
    for cb in _listeners.get(event, []):
        cb(data)

def calculate(expression: str) -> float:
    parts = expression.strip().split()
    if len(parts) != 3:
        raise ValueError("Invalid format. Use 'num op num'.")
    try:
        num1 = float(parts[0])
        op = parts[1]
        num2 = float(parts[2])
    except ValueError:
        raise ValueError("Invalid numbers in expression.")

    if op == '+':  result = num1 + num2
    elif op == '-': result = num1 - num2
    elif op == '*': result = num1 * num2
    elif op == '/':
        if num2 == 0: raise ValueError("Division by zero is not allowed.")
        result = num1 / num2
    elif op == '%':
        if num2 == 0: raise ValueError("Modulus by zero is not allowed.")
        result = num1 % num2
    else:
        raise ValueError(f"Unsupported operator: {op}")

    emit('result', {'expression': expression, 'result': result})
    return result
