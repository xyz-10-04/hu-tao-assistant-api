from fastapi import FastAPI, Query, HTTPException
from tools import roll_dice, get_current_time, calculate, save_note, read_notes
from memory import load_memory, save_memory
from pydantic import BaseModel
from fastapi import FastAPI

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

@app.get("/notes")
async def api_read_notes():
    notes = read_notes()
    return {"notes": notes}

@app.post("/note")
async def api_save_note(content: str):
    result = save_note(content)
    return {"status": "saved" if result else "failed"}

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