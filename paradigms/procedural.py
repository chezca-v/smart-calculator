import ast, operator as _op

# legacy procedural helpers (still available for two-operand calls)
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

# whitelist of AST node operators used for expression evaluation
_ops = {
    ast.Add: _op.add,
    ast.Sub: _op.sub,
    ast.Mult: _op.mul,
    ast.Div: _op.truediv,
    ast.Mod: _op.mod,
    ast.Pow: _op.pow,
    ast.USub: _op.neg,
    ast.UAdd: lambda x: x,
}

def _eval_node(node):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Num):
        return node.n
    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _ops:
            raise ValueError(f"Unsupported operator: {op_type}")
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        return _ops[op_type](left, right)
    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _ops:
            raise ValueError(f"Unsupported unary operator: {op_type}")
        return _ops[op_type](_eval_node(node.operand))
    raise ValueError(f"Invalid expression component: {node!r}")


def calculate(expression: str) -> float:
    """Evaluate arithmetic expression with PEMDAS.

    The UI sends tokens separated by spaces; '^' is treated as exponent.
    """
    expr = expression.strip().replace('^', '**')
    try:
        tree = ast.parse(expr, mode='eval')
        return float(_eval_node(tree.body))
    except Exception as e:
        raise ValueError(f"Invalid expression: {expression}") from e
