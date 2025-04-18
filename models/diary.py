from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Diary(BaseModel):
    """日记条目数据模型，使用Pydantic进行数据验证"""

    date: str = Field(default_factory=lambda: str(datetime.now().date()))
    time: str = Field(default_factory=lambda: str(datetime.now().time()))
    content: str = ""
    weather: Optional[str] = None
    note: Optional[str] = None
    last_rrmodified: str = Field(default_factory=lambda: str(datetime.now()))

    class Config:
        """模型配置"""

        arbitrary_types_allowed = True

    def __str__(self) -> str:
        """返回日记的字符串表示"""
        return f"DiaryEntry({self.date}: {self.content[:30]}{'...' if len(self.content) > 30 else ''})"
