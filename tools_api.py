
import random
from datetime import datetime


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


#===========  工具  =======================
def roll_dice():
    return random.randint(1, 6)

def get_current_time():
    return datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")

def calculate(expr):
    # 1. 白名单：只允许数字、运算符、括号、空格和小数点
    ALLOWED_CHARS = "0123456789+-*/.() "
    
    # 2. 检查表达式是否只包含允许的字符
    if not all(c in ALLOWED_CHARS for c in expr):
        return "错误：表达式包含非法字符，仅允许数字、运算符、括号和空格"

    # 3. 尝试执行计算
    try:
        # 限制 eval 的环境，防止执行危险操作
        result = eval(expr, {"__builtins__": None}, {})
        return result
    except ZeroDivisionError:
        return "错误：不能除以零"
    except (SyntaxError, TypeError, NameError):
        return "错误：表达式语法有误，请检查括号和运算符"
    except Exception as e:
        return f"未知错误：{e}"

