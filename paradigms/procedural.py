def add(a, b):       return a + b
def subtract(a, b):  return a - b
def multiply(a, b):  return a * b

def divide(a, b):
    if b == 0:
        return None, "Division by zero is not allowed."
    return a / b, None

def modulus(a, b):
    if b == 0:
        return None, "Modulus by zero is not allowed."
    return a % b, None

def calculate(expression: str) -> float:
    parts = expression.strip().split()
    if len(parts) != 3:
        raise ValueError("Invalid format. Use 'num op num'.")
    try:
        a = float(parts[0])
        op = parts[1]
        b = float(parts[2])
    except ValueError:
        raise ValueError("Invalid numbers in expression.")

    dispatch = {
        '+': lambda: (add(a, b), None),
        '-': lambda: (subtract(a, b), None),
        '*': lambda: (multiply(a, b), None),
        '/': lambda: divide(a, b),
        '%': lambda: modulus(a, b),
    }
    if op not in dispatch:
        raise ValueError(f"Unsupported operator: {op}")

    result, error = dispatch[op]()
    if error:
        raise ValueError(error)
    return result
