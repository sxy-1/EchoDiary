# coding:utf-8

import sys
from enum import Enum
from managers import WeatherManager
from PySide6.QtCore import QLocale
from qfluentwidgets import (
    qconfig,
    QConfig,
    ConfigItem,
    OptionsConfigItem,
    BoolValidator,
    OptionsValidator,
    RangeConfigItem,
    RangeValidator,
    FolderListValidator,
    Theme,
    FolderValidator,
    ConfigSerializer,
    __version__,
)


class Language(Enum):
    """Language enumeration"""

    CHINESE_SIMPLIFIED = QLocale(QLocale.Language.Chinese, QLocale.Country.China)
    CHINESE_TRADITIONAL = QLocale(QLocale.Language.Chinese, QLocale.Country.HongKong)
    ENGLISH = QLocale(QLocale.Language.English)
    AUTO = QLocale()


class LanguageSerializer(ConfigSerializer):
    """Language serializer"""

    def serialize(self, language):
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO


def isWin11():
    return sys.platform == "win32" and sys.getwindowsversion().build >= 22000


class Config(QConfig):
    """Config of application"""

    # folders
    musicFolders = ConfigItem("Folders", "LocalMusic", [], FolderListValidator())
    downloadFolder = ConfigItem(
        "Folders", "Download", "app/download", FolderValidator()
    )

    # main window
    micaEnabled = ConfigItem("MainWindow", "MicaEnabled", isWin11(), BoolValidator())
    dpiScale = OptionsConfigItem(
        "MainWindow",
        "DpiScale",
        "Auto",
        OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]),
        restart=True,
    )
    language = OptionsConfigItem(
        "MainWindow",
        "Language",
        Language.AUTO,
        OptionsValidator(Language),
        LanguageSerializer(),
        restart=True,
    )

    # Material
    blurRadius = RangeConfigItem(
        "Material", "AcrylicBlurRadius", 15, RangeValidator(0, 40)
    )

    # software update
    checkUpdateAtStartUp = ConfigItem(
        "Update", "CheckUpdateAtStartUp", True, BoolValidator()
    )

    weatherCity = ConfigItem(
        "Weather", "City", "上海", OptionsValidator(WeatherManager().get_all_cities())
    )


YEAR = 2025
AUTHOR = "dullspear"
VERSION = __version__
HELP_URL = "https://github.com/sxy-1/EchoDiary"
REPO_URL = "https://github.com/sxy-1/EchoDiary"
FEEDBACK_URL = "https://github.com/sxy-1/EchoDiary/issues"
RELEASE_URL = "https://github.com/sxy-1/EchoDiary/releases/latest"


cfg = Config()
cfg.themeMode.value = Theme.AUTO
qconfig.load("app/config/config.json", cfg)
