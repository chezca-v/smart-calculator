import ast, operator as _op
from typing import Dict, Callable

# keep original operation map for simple two-value calls if needed
_OPERATIONS: Dict[str, Callable[[float, float], float]] = {
    '+': _op.add,
    '-': _op.sub,
    '*': _op.mul,
    '/': _op.truediv,
    '%': _op.mod,
}

# AST-based evaluator for arbitrary-length expressions
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
        return _ops[op_type](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _ops:
            raise ValueError(f"Unsupported unary operator: {op_type}")
        return _ops[op_type](_eval_node(node.operand))
    raise ValueError(f"Invalid expression component: {node!r}")

def calculate(expression: str) -> float:
    expr = expression.strip().replace('^', '**')
    try:
        tree = ast.parse(expr, mode='eval')
        return _eval_node(tree.body)
    except Exception:
        raise ValueError(f"Invalid expression: {expression}")

