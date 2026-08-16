from config import MAX_HISTORY


def trim_messages(messages):
        #=========限制上下文长度==========
    if len(messages) > MAX_HISTORY * 2 + 1: # +1 是 system 消息
        # 1. 取出系统消息（第一条）
        system_msg = messages[0]
        # 2. 取出除系统消息外的所有消息
        user_messages = messages[1:]
# 3. 保留最近 MAX_HISTORY * 2 条（即 MAX_HISTORY 轮）
    # 注意：需要保证成对保留（user + assistant）
        rest = user_messages[-MAX_HISTORY * 2:]
# 4. 重新组合：system_msg + 最近的消息
        messages = [system_msg] + rest
    return messages
