from langchain.tools import tool
import random
from datetime import datetime
from rag_build import search_hu_tao  


@tool
def calculate(expr):
    """ 计算数学算式 """
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
def search_character_knowledge(query: str) -> str:
    """当用户询问胡桃是否认识某个角色、对其他角色的评价时使用此工具。"""
    try:
        docs = search_hu_tao(query, k=8, category="character")
        if not docs:
            return "未找到相关信息"
        context = "\n".join(docs)
        return f"以下内容说明胡桃认识相关角色，请据此回答：\n{context}"
    except Exception as e:
        return f"检索失败：{e}"

@tool
def search_food_knowledge(query: str) -> str:
    """当用户询问胡桃喜欢的食物、讨厌的食物、料理相关问题时使用此工具。"""
    try:
        docs = search_hu_tao(query, k=8, category="food")
        if not docs:
                return "未找到相关信息"
        context = "\n".join(docs)
        return f"以下内容说明胡桃对食物的偏好，请据此回答：\n{context}"
    except Exception as e:
        return f"检索失败：{e}"

@tool
def search_story_knowledge(query: str) -> str:
    """当用户询问胡桃的身世、往生堂背景、角色故事时使用此工具。"""
    try:
        docs = search_hu_tao(query, k=8, category="story")
        if not docs:
            return "未找到相关信息"
        context = "\n".join(docs)
        return f"以下内容说明胡桃的身世和背景，请据此回答：\n{context}"
    except Exception as e:
        return f"检索失败：{e}"