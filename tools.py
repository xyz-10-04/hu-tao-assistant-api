from langchain.tools import tool
import random
from datetime import datetime
from rag_build import search_hu_tao  
from memory import load_memory, save_memory

import time
import functools


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


@tool
def calculate(expr: str) -> str:
    """计算数学算式（支持加减乘除、括号、取余）"""
    from utils import safe_eval
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


# 修改后的 search_hu_tao_knowledge 工具
@tool
@retry(times=3, delay=1)
def search_hu_tao_knowledge(query: str) -> str:
    """当用户询问关于胡桃的任何设定、食物喜好、角色关系、背景故事时使用此工具。"""
    # 🚨 删掉 try-except，直接让 retry 去接管
    docs = search_hu_tao(query, k=8) 
    if not docs:
        return "未找到相关信息"
    return "以下是从知识库检索到的相关内容：\n" + "\n".join(docs)
search_hu_tao_knowledge.handle_tool_error = "知识库检索暂时不可用，请回答：网络开小差了，请稍后再试。"


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