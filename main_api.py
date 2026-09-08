import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

from fastapi import FastAPI, Query, HTTPException
from tools import roll_dice, get_current_time, calculate, save_note, read_notes
from memory import load_memory, save_memory

from pydantic import BaseModel, Field
from fastapi import FastAPI
from langchain_main import agent
# from database import engine
# from models import Base

from fastapi.responses import StreamingResponse

import time

import logging
from logging.handlers import RotatingFileHandler
import uuid

# 创建 logger
logger = logging.getLogger("huTao")   # "huTao" 可以改成你喜欢的名字，但不是必须改
logger.setLevel(logging.INFO)   # 这一行保留，它控制了日志级别

# 文件处理器（轮转）
file_handler = RotatingFileHandler("huTao.log", maxBytes=10*1024*1024, backupCount=5)
file_handler.setLevel(logging.INFO)

# 控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 添加处理器
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# 然后你就可以在代码中使用 logger.info(...)、logger.error(...) 等

app = FastAPI(
    title="胡桃助手API",
    description="往生堂第七十七代堂主胡桃为你服务——掷骰子、查时间、算算术、记笔记，样样精通。",
    version="1.0.0"
)
@app.get("/roll")
async def api_roll():
    return {"result": roll_dice()}

@app.get("/time")
async def api_time():
    return {"time": get_current_time()}

@app.get("/calc")
async def api_calc(expr: str = Query(...)):
    try:
        result = calculate(expr)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/note")
async def api_save_note(content: str):
    result = save_note(content)
    return {"status": "saved" if result else "failed"}

@app.get("/notes")
async def api_read_notes():
    notes = read_notes()
    return {"notes": notes}

class MemoryUpdate(BaseModel):
    data: dict  # 前端传入的记忆数据

@app.get("/memory")
async def api_get_memory():
    """获取当前记忆"""
    memory = load_memory()
    return {"memory": memory}

@app.post("/memory")
async def api_update_memory(update: MemoryUpdate):
    """更新记忆（覆盖写入）"""
    try:
        save_memory(update.data)
        return {"status": "saved", "memory": update.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Base.metadata.create_all(bind=engine)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500, description="用户输入的消息")

import asyncio

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    request_id = str(uuid.uuid4())[:8]  # 取前8位短ID
    start_time = time.time()
    # 记录请求（截断长消息）
    logger.info(f"[{request_id}] 收到请求: {request.message[:50]}...") # 截断长消息

    try:
        # 设置 30 秒超时
        result = await asyncio.wait_for(
            asyncio.to_thread(
                agent.invoke,
                {"messages": [{"role": "user", "content": request.message}]}
            ),
            timeout=90.0
        )
        reply = result["messages"][-1].content
        elapsed = time.time() - start_time
        logger.info(f"[{request_id}] 回复成功，耗时: {elapsed:.2f}s")
        return {"reply": reply}
    except asyncio.TimeoutError:
        logger.warning(f"[{request_id}] 请求超时: {request.message[:30]}...")
        return {"error": "请求超时，请稍后再试"}
    except Exception as e:
        logger.error(f"[{request_id}] 处理请求失败: {e}")
        return {"error": str(e)}

@app.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    request_id = str(uuid.uuid4())[:8]
    logger.info(f"[{request_id}] 收到流式请求: {request.message[:50]}...")

    async def generate():
        try:
            async for event in agent.astream_events(
                {"messages": [{"role": "user", "content": request.message}]},
                version="v2"
            ):
                if event["event"] == "on_chat_model_stream":
                    chunk = event["data"]["chunk"]
                    if chunk.content:
                        yield f"data: {chunk.content}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"[{request_id}] 流式处理失败: {e}")
            yield f"data: 处理失败: {str(e)}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
  
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

