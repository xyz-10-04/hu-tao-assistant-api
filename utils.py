import ast
import operator

ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv
}

def _eval_node(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("只支持数字")
    elif isinstance(node, ast.BinOp):
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        op_type = type(node.op)
        if op_type in ALLOWED_OPERATORS:
            try:
                return ALLOWED_OPERATORS[op_type](left, right)
            except ZeroDivisionError:
                raise ValueError("不能除以零")
        else:
            raise ValueError("不支持的运算符")
    elif isinstance(node, ast.UnaryOp):
        operand = _eval_node(node.operand)
        if isinstance(node.op, ast.USub):
            return -operand
        elif isinstance(node.op, ast.UAdd):
            return +operand
        else:
            raise ValueError("不支持的一元运算符")
    else:
        raise ValueError("不支持的语法结构")

def safe_eval(expr: str) -> float:
    if len(expr) > 100:
        raise ValueError("表达式过长")
    try:
        node = ast.parse(expr, mode='eval').body
        return _eval_node(node)
    except Exception:
        raise ValueError("表达式包含非法字符或不支持的运算")