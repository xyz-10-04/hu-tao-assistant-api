from database import SessionLocal
from models import Memory


def load_memory():
    db = SessionLocal()
    try:
        records = db.query(Memory).all()
        return {record.key: record.value for record in records}
    except Exception as e:
        print(f"读取记忆失败: {e}")
        return {}
    finally:
        db.close()


def save_memory(data):
    db = SessionLocal()
    try:
        for key, value in data.items():
            # 先查找是否存在
            existing = db.query(Memory).filter(Memory.key == key).first()
            if existing:
                # 存在则更新
                existing.value = value
            else:
                # 不存在则新增
                db.add(Memory(key=key, value=value))
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"保存记忆失败: {e}")
        return False
    finally:
        db.close()
