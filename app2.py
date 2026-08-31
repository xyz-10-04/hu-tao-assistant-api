try:
                response = requests.post(f"{API_URL}/chat", json={"message": user_input})
                if response.status_code == 200:
                    reply = response.json().get("reply", "胡桃没有回答，可能是出了点小问题。")
                else:
                    reply = f"后端返回错误：{response.status_code}"
            except Exception as e:
                reply = f"无法连接到后端服务：{e}"