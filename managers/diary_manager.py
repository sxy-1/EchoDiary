import os
import pickle
from typing import Optional, List
from abc import ABC, abstractmethod

from managers.crypto_manager import CryptoManager
from managers.config_manager import ConfigManager
from models import Diary


class IDiaryStorage(ABC):
    """日记存储接口，定义了日记存储的基本操作"""

    @abstractmethod
    def save_diary(self, diary: Diary) -> bool:
        """保存日记"""
        pass

    @abstractmethod
    def load_diary(self, date_str: str) -> Optional[Diary]:
        """加载日记"""
        pass

    @abstractmethod
    def delete_diary(self, date_str: str) -> bool:
        """删除日记"""
        pass

    @abstractmethod
    def get_all_dates(self) -> List[str]:
        """获取所有日记日期"""
        pass


class DiaryManager(IDiaryStorage):
    """
    日记文件管理器

    负责日记文件的存储、读取、删除等操作，并处理加密和解密逻辑。
    """

    def __init__(self):
        """
        初始化日记文件管理器

        Args:
            crypto_manager: 加密管理器
            config_manager: 配置管理器
        """
        self.crypto_manager = CryptoManager()
        self.config_manager = ConfigManager()

        # 确保日记存储目录存在
        self._ensure_diary_directory_exists()

    def _ensure_diary_directory_exists(self) -> None:
        """确保日记存储目录存在，不存在则创建"""
        diary_path = self.config_manager.get_config_value("diary_path")
        if not os.path.exists(diary_path):
            try:
                os.makedirs(diary_path)
                print(f"创建日记存储目录: {diary_path}")
            except Exception as e:
                print(f"创建日记目录失败: {e}")

    def _get_diary_path_from_date(self, date_str: str) -> str:
        """
        根据日期字符串获取日记文件路径

        Args:
            date_str: 日期字符串，格式为 YYYY-MM-DD，如果为 None 则使用当前日期

        Returns:
            日记文件的完整路径
        """
        date_str = date_str
        # 确保只取日期部分，不包含时间
        date_str = date_str.split()[0]
        diary_path_dir = self.config_manager.get_config_value("diary_path")
        return os.path.join(diary_path_dir, f"{date_str}.enc")

    def save_diary(self, diary: Diary) -> bool:
        """
        保存日记到文件

        Args:
            diary: 日记条目对象

        Returns:
            保存成功返回True，否则返回False
        """
        try:
            # 序列化和加密数据
            serialized_data = pickle.dumps(diary.model_dump())
            encrypted_data = self.crypto_manager.encrypt_data(serialized_data)

            # 确定文件路径
            file_path = self._get_diary_path_from_date(diary.date)

            # 写入文件
            with open(file_path, "wb") as f:
                f.write(encrypted_data)

            print(f"日记已保存: {file_path}")
            return True
        except Exception as e:
            print(f"保存日记失败: {e}")
            return False

    def load_diary(self, date_str: str) -> Optional[Diary]:
        """
        加载指定日期的日记

        Args:
            date_str: 日期字符串，格式为 YYYY-MM-DD，如果为 None 则使用当前日期

        Returns:
            成功返回日记条目对象，失败返回 None
        """
        try:
            file_path = self._get_diary_path_from_date(date_str)

            if not os.path.exists(file_path):
                print(f"日记文件不存在: {file_path}")
                return None

            with open(file_path, "rb") as f:
                encrypted_data = f.read()

            decrypted_data = self.crypto_manager.decrypt_data(encrypted_data)
            diary_data = pickle.loads(decrypted_data)

            return Diary(**diary_data)
        except Exception as e:
            print(f"加载日记失败: {e}")
            return None

    def get_all_dates(self) -> List[str]:
        """
        获取所有可用的日记日期列表

        Returns:
            日期字符串列表，按时间倒序排列
        """
        try:
            diary_path = self.config_manager.get_config_value("diary_path")
            if not os.path.exists(diary_path):
                return []

            files = [f for f in os.listdir(diary_path) if f.endswith(".enc")]
            dates = [f.replace(".enc", "") for f in files]
            return sorted(dates, reverse=True)
        except Exception as e:
            print(f"获取日记日期列表失败: {e}")
            return []

    def delete_diary(self, date_str: str) -> bool:
        """
        删除指定日期的日记

        Args:
            date_str: 要删除的日记日期

        Returns:
            删除成功返回True，否则返回False
        """
        try:
            file_path = self._get_diary_path_from_date(date_str)

            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"已删除日记: {date_str}")
                return True
            else:
                print(f"要删除的日记不存在: {date_str}")
                return False

        except Exception as e:
            print(f"删除日记失败: {e}")
            return False

    def get_all_diaries_str(self) -> List[str]:
        """
        获取所有日记条目

        Returns:
            日记条目对象列表
        """
        diaries = []
        for date_str in self.get_all_dates():
            diary = self.load_diary(date_str)
            if diary:
                diaries.append(str(diary))
        return diaries
