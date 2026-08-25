from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# 创建数据库引擎（使用 SQLite）
DATABASE_URL = "sqlite:///./hutao.db"  # 会在项目根目录生成 hutao.db 文件
engine = create_engine(DATABASE_URL, echo=True)  # echo=True 会打印执行的 SQL，方便调试

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 依赖注入用：每次请求获取一个会话
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()