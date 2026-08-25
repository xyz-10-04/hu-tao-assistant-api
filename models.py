from typing import Optional
from datetime import datetime
from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text)  # 笔记内容
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def __repr__(self) -> str:
        return f"Note(id={self.id}, content={self.content[:20]}...)"


class Memory(Base):
    __tablename__ = "memory"  # ← 表名，你可以自己定

    key: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)  # ← 主键，存 "name"、"hobby" 等
    value: Mapped[str] = mapped_column(Text)  # ← 存具体内容，如 "刻晴"
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)  # ← 自动记录更新时间

    def __repr__(self) -> str:
        return f"Memory(key={self.key}, value={self.value[:20]}...)"