from tools import save_note, read_notes, execute_tool, parse_tool_call
from memory import load_memory, match_memory_rules
from prompt import build_system_prompt
from api import call_api
from utils import trim_messages


def main():
    memory = load_memory()
    user_name = memory.get("name")
    print("工具助手已启动，输入：exit或quit退出")

    #=============初始化配置===============
    SYSTEM_PROMPT = build_system_prompt(user_name)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
        ]

    if user_name:
        print(f"欢迎回来，{user_name}")
    else:
        print("新朋友，你好！你可以告诉我你的名字，例如：我叫张三")

    while True:
        user_input = input("你：")
        if user_input.lower() in ('exit' , 'quit'): 
            break
        
        #==============功能说明============
        if user_input in ["帮助" ,"你能做什么"]:
            reply = "我能掷骰子、计算数学和告知现在时间"
            print(reply)
            messages.append({"role": "user", "content": user_input})
            messages.append({"role": "assistant", "content": reply})
            continue

        # ===========记笔记=============
        # print(f"【调试】用户输入：{user_input}")
        if user_input.startswith("记住："):
            content = user_input[3:]
            # print("【调试】进入保存分支")
            save_note(content)
            messages.append({"role": "user", "content": user_input})
            continue
        elif user_input in ["我有什么笔记", "我的笔记", "查看笔记"]:
            notes = read_notes()
            if notes:
                messages.append({"role": "user", "content": f"这是我记的笔记：{notes}"})
                continue
            else:
                messages.append({"role": "user", "content": "你还没有记笔记"})
                continue

        ##=========加入用户消息==========
        messages.append({"role": "user", "content": user_input})

        messages = trim_messages(messages)

        #============自动匹配规则=======
        if match_memory_rules(user_input):
            new_memory = load_memory()
            user_name = new_memory.get('name')

         #=========调用API===========
        response = call_api(messages)
        assistant_reply = response.choices[0].message.content
        # print("【调试】模型返回:", assistant_reply)

        tool_name, param = parse_tool_call(assistant_reply)

        if tool_name:
            #  ====  本地工具=====
            # print(f"【调试】execute_tool 收到 tool_name: {tool_name}")
            messages.append({"role": "assistant", "content": assistant_reply})
            tool_result = execute_tool(tool_name, param)
            # print(f"【调试】tool_result: {tool_result}")
              ##  ====== 再次调用API   ======
            messages.append({"role": "user", "content": f"工具返回：{tool_result}，请用自然语言回复用户"})
            response2 = call_api(messages)
            final_reply = response2.choices[0].message.content
            messages.append({"role": "assistant", "content": final_reply})
            print(f"胡桃：{final_reply}")
            
        else:
            messages.append({"role": "assistant", "content": assistant_reply})
            print(f"胡桃：{assistant_reply}")

if __name__ == "__main__":
    main()