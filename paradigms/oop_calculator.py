import ast, operator as _op

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

    # AST helpers for full expression support
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

    def _eval_node(self, node):
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Num):
            return node.n
        if isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in self._ops:
                raise ValueError(f"Unsupported operator: {op_type}")
            return self._ops[op_type](self._eval_node(node.left), self._eval_node(node.right))
        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in self._ops:
                raise ValueError(f"Unsupported unary operator: {op_type}")
            return self._ops[op_type](self._eval_node(node.operand))
        raise ValueError(f"Invalid expression component: {node!r}")

    def calculate(self, expression: str) -> float:
        expr = expression.strip().replace('^', '**')
        try:
            tree = ast.parse(expr, mode='eval')
            return self._eval_node(tree.body)
        except Exception:
            raise ValueError(f"Invalid expression: {expression}")

