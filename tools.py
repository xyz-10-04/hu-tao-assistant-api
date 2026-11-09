from langchain.tools import tool
import random
from datetime import datetime
from rag_build import search_hu_tao  
from memory import load_memory, save_memory

import time
import functools

import ast
import operator


def retry(times=3, delay=1):
    """自定义重试装饰器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if i == times - 1:  # 最后一次如果还失败，就抛出异常
                        raise e
                    print(f"⚠️ 工具 {func.__name__} 执行失败，{delay}秒后重试... 错误信息: {e}")
                    time.sleep(delay)
        return wrapper
    return decorator


# 允许的数学运算符
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
    # 长度限制，防止超长表达式
    if len(expr) > 100:
        raise ValueError("表达式过长")
        
    try:
        # 1. 解析成语法树
        node = ast.parse(expr, mode='eval').body
        return _eval_node(node)
    except Exception:
        raise ValueError("表达式包含非法字符或不支持的运算")

def _eval_node(node):
    # 如果是数字，直接返回
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("只支持数字")
        
    # 如果是二元运算（比如 1 + 2）
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
            
    # 如果是正负号（比如 -5）
    elif isinstance(node, ast.UnaryOp):
        operand = _eval_node(node.operand)
        if isinstance(node.op, ast.USub):
            return -operand
        elif isinstance(node.op, ast.UAdd):
            return +operand
        else:
            raise ValueError("不支持的一元运算符")
            
    # 其他任何东西（比如函数调用、变量名）直接拦截
    else:
        raise ValueError("不支持的语法结构")

@tool
def calculate(expr: str) -> str:
    """计算数学算式（支持加减乘除、括号、取余）"""
    try:
        result = safe_eval(expr)
        # 如果是整数，就返回整数格式；如果有小数，就保留小数
        if isinstance(result, float) and result.is_integer():
            return str(int(result))
        return str(result)
    except ValueError as e:
        return f"计算错误：{e}"
    except Exception as e:
        return f"未知错误：{e}"


@tool
def roll_dice():
    """  掷骰子  """
    return random.randint(1, 6)


@tool
def get_current_time():
    """   实时时间查询   """
    return datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")


# 新函数用不同的名字，保存到数据库

@tool
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


@tool
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


@tool
@retry(times=3, delay=1) # 🚨 加上这行
def search_hu_tao_knowledge(query: str) -> str:
    """当用户询问关于胡桃的任何设定、食物喜好、角色关系、背景故事时使用此工具。"""
    try:
        docs = search_hu_tao(query, k=8)
        if not docs:
            return "未找到相关信息"
        return f"以下是从知识库检索到的相关内容：\n" + "\n".join(docs)
    except Exception as e:
        return f"检索失败：{e}"


@tool
def save_user_info(info_type: str, content: str) -> str:
    """当用户告诉你他的个人信息时使用此工具。
    info_type 可以是 "name"（姓名）、"hobby"（爱好）等。
    content 是具体内容，例如 "刻晴" 或 "吃火锅"。
    """
    memory = load_memory()
    memory[info_type] = content
    save_memory(memory)
    return f"已记住用户的{info_type}是{content}"


@tool
def query_user_info(info_type: str) -> str:
    """当用户询问你他的个人信息时使用此工具。
    info_type 可以是 "name"（姓名）、"hobby"（爱好）等。
    """
    memory = load_memory()
    value = memory.get(info_type)
    if value:
        return f"用户的{info_type}是{value}"
    else:
        return f"未找到用户的{info_type}信息"