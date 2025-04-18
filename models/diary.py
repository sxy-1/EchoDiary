from pydantic import BaseModel
from typing import Optional


class Diary(BaseModel):
    """日记条目数据模型，使用Pydantic进行数据验证"""

    date: Optional[str] = None
    content: Optional[str] = None
    weather: Optional[str] = None
    note: Optional[str] = None
    create_time: Optional[str] = None
    update_time: Optional[str] = None

    class Config:
        """模型配置"""

        frozen = False
        arbitrary_types_allowed = True

    def __str__(self) -> str:
        """返回日记的字符串表示"""
        return f"DiaryEntry({self.date}: {self.content[:30]}{'...' if len(self.content) > 30 else ''})"
