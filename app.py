import streamlit as st
import requests

# FastAPI 后端地址
API_URL = "http://localhost:8000/chat"

st.title("胡桃助手")
st.caption("往生堂第七十七代堂主，为你服务")


def stream_chat(message):
    url = "http://localhost:8000/chat/stream"
    try:
        response = requests.post(url, json={"message": message}, stream=True, timeout=120)
        for line in response.iter_lines():
            if line:
                decoded = line.decode('utf-8')
                if decoded.startswith("data: "):
                    content = decoded[6:]
                    if content == "[DONE]":
                        break
                    yield content
    except Exception as e:
        yield f"连接失败: {e}"

with st.sidebar:
    st.header("🎯 工具")
    
    if st.button("🎲 掷骰子"):
        # 发送请求到 /roll
        response = requests.get("http://localhost:8000/roll")
        if response.status_code == 200:
            st.success(f"🎯 结果：{response.json()['result']}")
        else:
            st.error("请求失败")
    
    if st.button("🕐 获取时间"):
        response = requests.get("http://localhost:8000/time")
        if response.status_code == 200:
            st.info(f"🕒 {response.json()['time']}")
        else:
            st.error("请求失败")
    
    # 计算器需要输入框
    st.subheader("🧮 计算器")
    expr = st.text_input("输入算式（如 3*8）")
    if st.button("计算"):
        if expr:
            response = requests.get(f"http://localhost:8000/calc?expr={expr}")
            if response.status_code == 200:
                st.write(f"✅ 结果：{response.json()['result']}")
            else:
                st.error("计算失败")

    # 笔记管理
    st.subheader("📝 笔记")
    note_content = st.text_input("输入笔记内容", key="note_input")
    if st.button("保存笔记"):
        if note_content:
            response = requests.post(
                "http://localhost:8000/note",
                params={"content": note_content}
            )
            if response.status_code == 200:
                st.success("✅ 笔记已保存")
            else:
                st.error("保存失败")
        else:
            st.warning("请输入笔记内容")

    if st.button("📖 查看所有笔记"):
        response = requests.get("http://localhost:8000/notes")
        if response.status_code == 200:
            notes = response.json().get("notes", [])
            if notes:
                for note in notes:
                    st.write(f"- {note}")
            else:
                st.info("暂无笔记")
        else:
            st.error("读取失败")

# 初始化聊天历史
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "你好呀，我是胡桃！有什么需要帮忙的吗？"}
    ]

# 显示历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 用户输入
user_input = st.chat_input("说点什么吧...")
if user_input:
    # 显示用户消息
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 流式助手回复（保留思考提示 + 超时/异常处理）
    with st.chat_message("assistant"):
        with st.spinner("胡桃正在思考..."):
            try:
                response = st.write_stream(stream_chat(user_input))
            except Exception as e:
                response = f"处理请求时发生错误：{e}"
        st.session_state.messages.append({"role": "assistant", "content": response})