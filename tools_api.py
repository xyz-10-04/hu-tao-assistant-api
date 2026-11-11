import random
from datetime import datetime

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
    from utils import safe_eval
    try:
        result = safe_eval(expr)
        if isinstance(result, float) and result.is_integer():
            return str(int(result))
        return str(result)
    except ValueError as e:
        return f"错误：{e}"
    except Exception as e:
        return f"未知错误：{e}"