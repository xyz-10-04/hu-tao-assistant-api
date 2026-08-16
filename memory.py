import json
from config import MEMORY_FILE


def load_memory():
    try:
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_memory(data):
    # MEMORY_FILE = MEMORY + MEMORY_FILE
    try:
        with open(MEMORY_FILE, 'w',  encoding='utf-8') as f:
            return json.dump(data, f, indent=2)
    except Exception as e:
        print(f"保存记忆失败：{e}")

#====================匹配规则=============
def match_memory_rules(user_input):
    query_keywords = ("我叫什么", "我是谁", "我喜欢干什么", "我的名字")     #######清晰表示“查询关键词列表”
    field_display= {"name": "名字", "hobby": "爱好"}
    rule = {"我叫": "name", "我是": "name", "我喜欢": "hobby"}

    if any(user_input.startswith(k) for k in query_keywords):
        memory = load_memory()
        name = memory.get('name')
        if name:
           return False

    for keyword, field in rule.items():
        if user_input.startswith(keyword):
            remaining = user_input[len(keyword):].strip()
            memory = load_memory()
            memory[field] = remaining
            save_memory(memory)
            print(f"好的，我记住{field_display[field]}{remaining}了")
            return True
    else:
        return False
