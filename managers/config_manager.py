import json
import os


class ConfigManager:
    CONFIG_FILE = "./data/config/config.json"
    DEFAULT_CONFIG = {
        "key_path": "./data/keys/",
        "password": "",  # 默认无密码
        "diary_path": "./data/diary/",
    }

    def __init__(self, file_path=None):
        """初始化配置管理器实例，加载配置文件。"""
        self.file_path = file_path or self.CONFIG_FILE
        self.config = self._load_config()

    @classmethod
    def _load_config(cls, file_path=None):
        """加载配置文件，如果不存在则创建默认配置。"""
        file_path = file_path or cls.CONFIG_FILE
        if not os.path.exists(file_path):
            cls._save_config(cls.DEFAULT_CONFIG, file_path)
            return cls.DEFAULT_CONFIG
        with open(file_path, "r") as f:
            return json.load(f)

    @classmethod
    def _save_config(cls, config, file_path=None):
        """保存配置到文件。"""
        file_path = file_path or cls.CONFIG_FILE
        with open(file_path, "w") as f:
            json.dump(config, f, indent=4)

    def get_config_value(self, key, default=None):
        """获取配置值。"""
        return self.config.get(key, default)

    def set_config_value(self, key, value):
        """设置配置值并保存。"""
        self.config[key] = value
        self._save_config(self.config, self.file_path)

    def delete_config_value(self, key):
        """删除配置项并保存。"""
        if key in self.config:
            del self.config[key]
            self._save_config(self.config, self.file_path)
            return True
        return False

    def list_all_config_values(self):
        """列出所有配置项。"""
        return self.config

    @classmethod
    def initialize_config(cls, file_path=None):
        """初始化配置文件（类方法）。"""
        file_path = file_path or cls.CONFIG_FILE
        if not os.path.exists(file_path):
            print("未检测到配置文件，正在创建默认配置...")
            cls._save_config(cls.DEFAULT_CONFIG, file_path)
            print("默认配置已创建。")
        else:
            print("配置文件已存在，正在检查缺失项...")
            config = cls._load_config(file_path)
            updated = False
            for key, default_value in cls.DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = default_value
                    updated = True
            if updated:
                cls._save_config(config, file_path)
                print("配置文件已更新，缺失的配置项已补充。")
            else:
                print("配置文件完整，无需更新。")
