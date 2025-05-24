# coding:utf-8
from qfluentwidgets import (
    SettingCardGroup,
    SwitchSettingCard,
    OptionsSettingCard,
    HyperlinkCard,
    PrimaryPushSettingCard,
    ScrollArea,
    ComboBoxSettingCard,
    ExpandLayout,
    CustomColorSettingCard,
    setTheme,
    setThemeColor,
    RangeSettingCard,
)
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import InfoBar, SearchLineEdit
from PySide6.QtWidgets import QCompleter
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QWidget, QLabel, QFileDialog, QLineEdit

from common.config import cfg, HELP_URL, FEEDBACK_URL, AUTHOR, VERSION, YEAR, isWin11
from common.signal_bus import signalBus
from common.style_sheet import StyleSheet
import sys
from PySide6.QtWidgets import QApplication
from qfluentwidgets import Theme
from PySide6.QtWidgets import QInputDialog

from managers.config_manager import ConfigManager


class SettingInterface(ScrollArea):
    """设置界面"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # 设置标签
        self.settingLabel = QLabel("设置", self)
        # 添加配置管理器
        self.configManager = ConfigManager()
        self.configGroup = SettingCardGroup("基础配置", self.scrollWidget)
        self.__initConfigSettings()
        self.expandLayout.addWidget(self.configGroup)

        # region  天气

        # line edit with completer
        self.weatherCard = SearchLineEdit(self)
        self.weatherCard.setPlaceholderText("输入城市名")
        self.weatherCard.setClearButtonEnabled(True)
        self.weatherCard.setFixedWidth(230)
        stands = [
            "Star Platinum",
            "Hierophant Green",
            "Made in Haven",
            "King Crimson",
            "Silver Chariot",
            "Crazy diamond",
            "Metallica",
            "Another One Bites The Dust",
            "Heaven's Door",
            "Killer Queen",
            "The Grateful Dead",
            "Stone Free",
            "The World",
            "Sticky Fingers",
            "Ozone Baby",
            "Love Love Deluxe",
            "Hermit Purple",
            "Gold Experience",
            "King Nothing",
            "Paper Moon King",
            "Scary Monster",
            "Mandom",
            "20th Century Boy",
            "Tusk Act 4",
            "Ball Breaker",
            "Sex Pistols",
            "D4C • Love Train",
            "Born This Way",
            "SOFT & WET",
            "Paisley Park",
            "Wonder of U",
            "Walking Heart",
            "Cream Starter",
            "November Rain",
            "Smooth Operators",
            "The Matte Kudasai",
        ]
        completer = QCompleter(stands, self.weatherCard)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setMaxVisibleItems(10)
        self.weatherCard.setCompleter(completer)

        # 创建天气设置组
        self.weatherGroup = SettingCardGroup("天气设置", self.scrollWidget)

        self.weatherGroup.addSettingCard(self.weatherCard)
        # endregion

        # 个性化
        self.personalGroup = SettingCardGroup("个性化", self.scrollWidget)
        self.micaCard = SwitchSettingCard(
            FIF.TRANSPARENT,
            "Mica特效",
            "为窗口和表面应用半透明效果",
            cfg.micaEnabled,
            self.personalGroup,
        )
        self.themeCard = OptionsSettingCard(
            cfg.themeMode,
            FIF.BRUSH,
            "应用主题",
            "更改应用程序的外观",
            texts=["浅色", "深色", "跟随系统设置"],
            parent=self.personalGroup,
        )
        self.themeColorCard = CustomColorSettingCard(
            cfg.themeColor,
            FIF.PALETTE,
            "主题色",
            "更改应用程序的主题色",
            self.personalGroup,
        )
        self.zoomCard = OptionsSettingCard(
            cfg.dpiScale,
            FIF.ZOOM,
            "界面缩放",
            "更改控件和字体的大小",
            texts=[
                "100%",
                "125%",
                "150%",
                "175%",
                "200%",
                "跟随系统设置",
            ],
            parent=self.personalGroup,
        )
        self.languageCard = ComboBoxSettingCard(
            cfg.language,
            FIF.LANGUAGE,
            "语言",
            "设置界面显示语言",
            texts=["简体中文", "繁體中文", "English", "跟随系统设置"],
            parent=self.personalGroup,
        )

        # 材质
        self.materialGroup = SettingCardGroup("材质", self.scrollWidget)
        self.blurRadiusCard = RangeSettingCard(
            cfg.blurRadius,
            FIF.ALBUM,
            "亚克力模糊半径",
            "半径越大，图像越模糊",
            self.materialGroup,
        )

        # 软件更新
        self.updateSoftwareGroup = SettingCardGroup("软件更新", self.scrollWidget)
        self.updateOnStartUpCard = SwitchSettingCard(
            FIF.UPDATE,
            "启动时检查更新",
            "新版本将更加稳定并拥有更多功能",
            configItem=cfg.checkUpdateAtStartUp,
            parent=self.updateSoftwareGroup,
        )

        # 关于
        self.aboutGroup = SettingCardGroup("关于", self.scrollWidget)
        self.helpCard = HyperlinkCard(
            HELP_URL,
            "打开帮助页面",
            FIF.HELP,
            "帮助",
            "发现新功能并学习Echo Diary的使用技巧",
            self.aboutGroup,
        )
        self.feedbackCard = PrimaryPushSettingCard(
            "提供反馈",
            FIF.FEEDBACK,
            "提供反馈",
            "通过反馈帮助我们改进Echo Diary",
            self.aboutGroup,
        )
        self.aboutCard = PrimaryPushSettingCard(
            "检查更新",
            FIF.INFO,
            "关于",
            "© " + "版权" + f" {YEAR}, {AUTHOR}. " + "版本" + " " + VERSION,
            self.aboutGroup,
        )

        self.__initWidget()

    def __initWidget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 80, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName("settingInterface")

        # 初始化样式表
        self.scrollWidget.setObjectName("scrollWidget")
        self.settingLabel.setObjectName("settingLabel")
        StyleSheet.SETTING_INTERFACE.apply(self)

        self.micaCard.setEnabled(isWin11())

        # 初始化布局
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initConfigSettings(self):
        """初始化配置设置"""

        # 环境路径
        self.envPathCard = PrimaryPushSettingCard(
            "环境路径",
            FIF.FOLDER,
            "设置环境路径",
            self.configManager.get_config_value("env_path", "./"),
            self.configGroup,
        )
        self.envPathCard.clicked.connect(
            lambda: self.__onPathCardClicked("env_path", self.envPathCard)
        )

        # 日记路径
        self.diaryPathCard = PrimaryPushSettingCard(
            "日记路径",
            FIF.FOLDER,
            "设置日记路径",
            self.configManager.get_config_value("diary_path", "./data/diary/"),
            self.configGroup,
        )
        self.diaryPathCard.clicked.connect(
            lambda: self.__onPathCardClicked("diary_path", self.diaryPathCard)
        )

        # 密钥路径
        self.keyPathCard = PrimaryPushSettingCard(
            "密钥路径",
            FIF.FOLDER,
            "设置密钥路径",
            self.configManager.get_config_value("key_path", "./data/keys/"),
            self.configGroup,
        )
        self.keyPathCard.clicked.connect(
            lambda: self.__onPathCardClicked("key_path", self.keyPathCard)
        )

        # 密码
        self.passwordCard = PrimaryPushSettingCard(
            "密码",
            FIF.FOLDER,
            "设置密码",
            "******" if self.configManager.get_config_value("password") else "未设置",
            self.configGroup,
        )
        self.passwordCard.clicked.connect(self.__onPasswordCardClicked)

        # 添加卡片到组
        self.configGroup.addSettingCard(self.envPathCard)
        self.configGroup.addSettingCard(self.diaryPathCard)
        self.configGroup.addSettingCard(self.keyPathCard)
        self.configGroup.addSettingCard(self.passwordCard)

    def __onPathCardClicked(self, config_key, card):
        """处理路径选择"""
        folder = QFileDialog.getExistingDirectory(self, "选择目录", "./")
        if folder:
            self.configManager.set_config_value(config_key, folder)
            card.setContent(folder)
            InfoBar.success(
                "配置已更新",
                f"{config_key} 已更新",
                duration=1500,
                parent=self,
            )

    def __onPasswordCardClicked(self):
        """处理密码设置"""
        password, ok = QInputDialog.getText(
            self,
            "设置密码",
            "输入新密码:",
            QLineEdit.Password,
        )
        if ok and password:
            self.configManager.set_config_value("password", password)
            self.passwordCard.setContent("******")
            InfoBar.success(
                "密码已更新",
                "密码已成功更新",
                duration=1500,
                parent=self,
            )

    def __initLayout(self):
        self.settingLabel.move(36, 30)

        # 添加卡片到组
        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.micaCard)
        self.personalGroup.addSettingCard(self.themeColorCard)
        self.personalGroup.addSettingCard(self.zoomCard)
        self.personalGroup.addSettingCard(self.languageCard)

        self.materialGroup.addSettingCard(self.blurRadiusCard)

        self.updateSoftwareGroup.addSettingCard(self.updateOnStartUpCard)

        self.aboutGroup.addSettingCard(self.helpCard)
        self.aboutGroup.addSettingCard(self.feedbackCard)
        self.aboutGroup.addSettingCard(self.aboutCard)

        # 添加设置卡片组到布局
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)

        self.expandLayout.addWidget(self.weatherGroup)
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.materialGroup)
        self.expandLayout.addWidget(self.updateSoftwareGroup)
        self.expandLayout.addWidget(self.aboutGroup)

    def __showRestartTooltip(self):
        """显示重启提示"""
        InfoBar.success(
            "更新成功",
            "配置将在重启后生效",
            duration=1500,
            parent=self,
        )

    def __onDownloadFolderCardClicked(self):
        """下载文件夹卡片点击槽"""
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹", "./")
        if not folder or cfg.get(cfg.downloadFolder) == folder:
            return

        cfg.set(cfg.downloadFolder, folder)
        self.downloadFolderCard.setContent(folder)

    def __connectSignalToSlot(self):
        """连接信号与槽"""
        cfg.appRestartSig.connect(self.__showRestartTooltip)

        # 个性化
        self.themeCard.optionChanged.connect(lambda ci: setTheme(cfg.get(ci)))
        self.themeColorCard.colorChanged.connect(setThemeColor)
        self.micaCard.checkedChanged.connect(signalBus.micaEnableChanged)

        # 关于
        self.feedbackCard.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(FEEDBACK_URL))
        )


if __name__ == "__main__":
    setTheme(Theme.DARK)
    app = QApplication(sys.argv)
    window = SettingInterface()
    window.show()
    sys.exit(app.exec())
