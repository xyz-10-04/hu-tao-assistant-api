import random
from datetime import datetime
import ast
import operator

# ================== AST 安全求值器 ==================
ALLOWED_OPERATORS = {
    ast.Add: operator.add,      # +
    ast.Sub: operator.sub,      # -
    ast.Mult: operator.mul,     # *
    ast.Div: operator.truediv,  # /
    ast.Mod: operator.mod,      # %
    ast.FloorDiv: operator.floordiv # //
}

def safe_eval(expr: str) -> float:
    """安全的数学表达式求值，只允许基础四则运算"""
    if len(expr) > 100:
        raise ValueError("表达式过长")
        
    try:
        node = ast.parse(expr, mode='eval').body
        return _eval_node(node)
    except Exception:
        raise ValueError("表达式包含非法字符或不支持的运算")

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


# ================== 业务工具 ==================
def save_note(content):
    """保存笔记到数据库"""
    from database import SessionLocal
    from models import Note
    db = SessionLocal()
    try:
        note = Note(content=content)
        db.add(note)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"保存失败: {e}")
        return False
    finally:
        db.close()

def read_notes():
    """读取数据库中的所有笔记"""
    from database import SessionLocal
    from models import Note
    db = SessionLocal()
    try:
        notes = db.query(Note).all()
        return [note.content for note in notes]
    except Exception as e:
        print(f"读取失败: {e}")
        return []
    finally:
        db.close()

def roll_dice():
    return random.randint(1, 6)

def get_current_time():
    return datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")

def calculate(expr):
    """API 端的计算器（已升级为 AST 安全求值）"""
    try:
        result = safe_eval(expr)
        if isinstance(result, float) and result.is_integer():
            return str(int(result))
        return str(result)
    except ValueError as e:
        return f"错误：{e}"
    except Exception as e:
        return f"未知错误：{e}"