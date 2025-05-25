from pydantic import BaseModel  # 新增


class Config(BaseModel):  # 新增
    key_path: str = "./data/keys/"
    password: str = ""
    diary_path: str = "./data/diary/"
