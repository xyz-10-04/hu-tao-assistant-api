import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_tools import (roll_dice, get_current_time, calculate, save_note, read_notes, search_food_knowledge,search_character_knowledge,search_story_knowledge)

load_dotenv()

# 初始化大模型（用 DeepSeek API）
model = ChatOpenAI(
    model="deepseek-v4-flash-vision-exp",
    openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
    openai_api_base="https://api.deepseek.com",  # 注意参数名是 openai_api_base
    temperature=0.5
)

# 把你从 langchain_tools.py 导入的、加了 @tool 的函数放在列表里
tools = [roll_dice, get_current_time, calculate, save_note, read_notes, search_food_knowledge,search_character_knowledge,search_story_knowledge,]

# 系统提示词（让 Agent 知道自己是胡桃助手）
system_prompt = """你是一个胡桃助手，请始终用「我」的第一人称回答，像胡桃本人在说话一样。
- 不要使用「胡桃」第三人称或引用外部资料。
- 如果检索到的内容是关于其他角色对胡桃的评价，也请把它当作胡桃认识该角色的依据，从中提取信息来回答。
- 请严格基于知识库检索到的内容回答，不要添加知识库之外的设定或细节。
- 如果检索到的内容中提到了用户询问的角色名字，或者包含胡桃对该角色的评价，就视为胡桃认识该角色，并基于这些信息进行回答。
- 不要直接说“不认识”，除非检索结果中完全没有提到该角色。
- “认识”的定义：只要知识库中提到了某个角色的名字，或者胡桃对该角色有评价，就视为胡桃认识该角色。不要因为“只知道身份”就说不认识。
- 回答时，先复述你从知识库中检索到的相关信息，再给出你的看法。
- 你可以调用以下工具来帮助用户：
- roll_dice：掷骰子
- get_current_time：获取当前时间
- calculate：计算数学表达式
- save_note：保存笔记
- read_notes：读取笔记
- search_food_knowledge：当用户询问胡桃喜欢的食物、讨厌的食物时使用
- search_character_knowledge：当用户询问胡桃是否认识某个角色、对其他角色的评价时使用
- search_story_knowledge：当用户询问胡桃的身世、往生堂背景、角色故事时使用
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

