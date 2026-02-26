import operator
from typing import Dict, Callable

_OPERATIONS: Dict[str, Callable[[float, float], float]] = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv,
    '%': operator.mod,
}

def calculate(expression: str) -> float:
    parts = expression.strip().split()
    if len(parts) != 3:
        raise ValueError("Invalid format. Use 'num op num'.")

    left_val, op, right_val = parts
    try:
        num1 = float(left_val)
        num2 = float(right_val)
    except ValueError:
        raise ValueError("Non-numeric input detected.")

    if op not in _OPERATIONS:
        raise ValueError(f"Unsupported operator '{op}'.")
    if op in ('/', '%') and num2 == 0:
        raise ValueError("Division/Modulo by zero is not allowed.")

    return _OPERATIONS[op](num1, num2)
