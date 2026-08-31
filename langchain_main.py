import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_tools import roll_dice, get_current_time, calculate, save_note, read_notes, retrieve_hu_tao_knowledge

load_dotenv()

# 初始化大模型（用 DeepSeek API）
model = ChatOpenAI(
    model="deepseek-v4-pro",
    openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
    openai_api_base="https://api.deepseek.com",  # 注意参数名是 openai_api_base
    temperature=0.7
)
 
# 把你从 langchain_tools.py 导入的、加了 @tool 的函数放在列表里
tools = [roll_dice, get_current_time, calculate, save_note, read_notes, retrieve_hu_tao_knowledge]

# 系统提示词（让 Agent 知道自己是胡桃助手）
system_prompt = """你是一个胡桃助手，你可以调用以下工具来帮助用户：
- roll_dice：掷骰子
- get_current_time：获取当前时间
- calculate：计算数学表达式
- save_note：保存笔记
- read_notes：读取笔记
如果用户只是闲聊，直接回复。全部回答用中文。
"""

agent = create_agent(
    model=model,
    tools=tools,
    system_prompt=system_prompt
)

print("工具助手已启动，输入 exit 或 quit 退出")

if __name__ == "__main__":
    while True:
        user_input = input("你：")
        if user_input.lower() in ('exit', 'quit'):
            break

        # LangChain 1.0 推荐的调用方式[reference:3][reference:4]
        result = agent.invoke({
            "messages": [{"role": "user", "content": user_input}]
        })

        # 提取最后一条回复
        reply = result["messages"][-1].content
        print(f"胡桃：{reply}")

