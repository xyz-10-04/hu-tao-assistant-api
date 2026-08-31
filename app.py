import streamlit as st
import requests

# FastAPI 后端地址
API_URL = "http://localhost:8000/chat"

st.title("胡桃助手")
st.caption("往生堂第七十七代堂主，为你服务")

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

    # 调用后端 Agent
    # 调用后端 Agent
    with st.chat_message("assistant"):
        with st.spinner("胡桃正在思考..."):
            try:
                response = requests.post(
                    "http://localhost:8000/chat",
                    json={"message": user_input},
                    timeout=30
            )
                if response.status_code == 200:
                    data = response.json()
                    reply = data.get("reply", "胡桃没有回答，可能是出了点小问题。")
                else:
                    reply = f"后端返回错误：{response.status_code}"
            except requests.exceptions.Timeout:
                reply = "请求超时，请稍后再试"
            except Exception as e:
                reply = f"无法连接到后端服务：{e}"
        st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

    