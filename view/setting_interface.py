# coding:utf-8
from qfluentwidgets import (
    SettingCardGroup,
    SwitchSettingCard,
    FolderListSettingCard,
    OptionsSettingCard,
    PushSettingCard,
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
from PySide6.QtCore import Qt, QUrl, QStandardPaths
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
    """Setting interface"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # setting label
        self.settingLabel = QLabel(self.tr("Settings"), self)
        # 添加配置管理器
        self.configManager = ConfigManager()
        self.configGroup = SettingCardGroup(self.tr("Configuration"), self.scrollWidget)
        self.__initConfigSettings()
        self.expandLayout.addWidget(self.configGroup)

        # region  天气

        # line edit with completer
        self.weatherCard = SearchLineEdit(self)
        self.weatherCard.setPlaceholderText("Type a stand name")
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
        self.weatherGroup = SettingCardGroup("Weather Settings", self.scrollWidget)

        self.weatherGroup.addSettingCard(self.weatherCard)
        # endregion

        # music folders
        self.musicInThisPCGroup = SettingCardGroup(
            self.tr("Music on this PC"), self.scrollWidget
        )
        self.musicFolderCard = FolderListSettingCard(
            cfg.musicFolders,
            self.tr("Local music library"),
            directory=QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.MusicLocation
            ),
            parent=self.musicInThisPCGroup,
        )
        self.downloadFolderCard = PushSettingCard(
            self.tr("Choose folder"),
            FIF.DOWNLOAD,
            self.tr("Download directory"),
            cfg.get(cfg.downloadFolder),
            self.musicInThisPCGroup,
        )

        # personalization
        self.personalGroup = SettingCardGroup(
            self.tr("Personalization"), self.scrollWidget
        )
        self.micaCard = SwitchSettingCard(
            FIF.TRANSPARENT,
            self.tr("Mica effect"),
            self.tr("Apply semi transparent to windows and surfaces"),
            cfg.micaEnabled,
            self.personalGroup,
        )
        self.themeCard = OptionsSettingCard(
            cfg.themeMode,
            FIF.BRUSH,
            self.tr("Application theme"),
            self.tr("Change the appearance of your application"),
            texts=[self.tr("Light"), self.tr("Dark"), self.tr("Use system setting")],
            parent=self.personalGroup,
        )
        self.themeColorCard = CustomColorSettingCard(
            cfg.themeColor,
            FIF.PALETTE,
            self.tr("Theme color"),
            self.tr("Change the theme color of you application"),
            self.personalGroup,
        )
        self.zoomCard = OptionsSettingCard(
            cfg.dpiScale,
            FIF.ZOOM,
            self.tr("Interface zoom"),
            self.tr("Change the size of widgets and fonts"),
            texts=[
                "100%",
                "125%",
                "150%",
                "175%",
                "200%",
                self.tr("Use system setting"),
            ],
            parent=self.personalGroup,
        )
        self.languageCard = ComboBoxSettingCard(
            cfg.language,
            FIF.LANGUAGE,
            self.tr("Language"),
            self.tr("Set your preferred language for UI"),
            texts=["简体中文", "繁體中文", "English", self.tr("Use system setting")],
            parent=self.personalGroup,
        )

        # material
        self.materialGroup = SettingCardGroup(self.tr("Material"), self.scrollWidget)
        self.blurRadiusCard = RangeSettingCard(
            cfg.blurRadius,
            FIF.ALBUM,
            self.tr("Acrylic blur radius"),
            self.tr("The greater the radius, the more blurred the image"),
            self.materialGroup,
        )

        # update software53
        self.updateSoftwareGroup = SettingCardGroup(
            self.tr("Software update"), self.scrollWidget
        )
        self.updateOnStartUpCard = SwitchSettingCard(
            FIF.UPDATE,
            self.tr("Check for updates when the application starts"),
            self.tr("The new version will be more stable and have more features"),
            configItem=cfg.checkUpdateAtStartUp,
            parent=self.updateSoftwareGroup,
        )

        # application
        self.aboutGroup = SettingCardGroup(self.tr("About"), self.scrollWidget)
        self.helpCard = HyperlinkCard(
            HELP_URL,
            self.tr("Open help page"),
            FIF.HELP,
            self.tr("Help"),
            self.tr(
                "Discover new features and learn useful tips about PyQt-Fluent-Widgets"
            ),
            self.aboutGroup,
        )
        self.feedbackCard = PrimaryPushSettingCard(
            self.tr("Provide feedback"),
            FIF.FEEDBACK,
            self.tr("Provide feedback"),
            self.tr("Help us improve PyQt-Fluent-Widgets by providing feedback"),
            self.aboutGroup,
        )
        self.aboutCard = PrimaryPushSettingCard(
            self.tr("Check update"),
            FIF.INFO,
            self.tr("About"),
            "© "
            + self.tr("Copyright")
            + f" {YEAR}, {AUTHOR}. "
            + self.tr("Version")
            + " "
            + VERSION,
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

        # initialize style sheet
        self.scrollWidget.setObjectName("scrollWidget")
        self.settingLabel.setObjectName("settingLabel")
        StyleSheet.SETTING_INTERFACE.apply(self)

        self.micaCard.setEnabled(isWin11())

        # initialize layout
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initConfigSettings(self):
        """初始化配置设置"""

        # 环境路径
        self.envPathCard = PrimaryPushSettingCard(
            self.tr("环境路径"),
            FIF.FOLDER,
            self.tr("设置环境路径"),
            self.configManager.get_config_value("env_path", "./"),
            self.configGroup,
        )
        self.envPathCard.clicked.connect(
            lambda: self.__onPathCardClicked("env_path", self.envPathCard)
        )

        # 日记路径
        self.diaryPathCard = PrimaryPushSettingCard(
            self.tr("日记路径"),
            FIF.FOLDER,
            self.tr("设置日记路径"),
            self.configManager.get_config_value("diary_path", "./data/diary/"),
            self.configGroup,
        )
        self.diaryPathCard.clicked.connect(
            lambda: self.__onPathCardClicked("diary_path", self.diaryPathCard)
        )

        # 密钥路径
        self.keyPathCard = PrimaryPushSettingCard(
            self.tr("密钥路径"),
            FIF.FOLDER,
            self.tr("设置密钥路径"),
            self.configManager.get_config_value("key_path", "./data/keys/"),
            self.configGroup,
        )
        self.keyPathCard.clicked.connect(
            lambda: self.__onPathCardClicked("key_path", self.keyPathCard)
        )

        # 密码
        self.passwordCard = PrimaryPushSettingCard(
            self.tr("密码"),
            FIF.FOLDER,
            self.tr("设置密码"),
            "******"
            if self.configManager.get_config_value("password")
            else self.tr("未设置"),
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
        folder = QFileDialog.getExistingDirectory(self, self.tr("选择目录"), "./")
        if folder:
            self.configManager.set_config_value(config_key, folder)
            card.setContent(folder)
            InfoBar.success(
                self.tr("配置已更新"),
                self.tr(f"{config_key} 已更新"),
                duration=1500,
                parent=self,
            )

    def __onPasswordCardClicked(self):
        """处理密码设置"""
        password, ok = QInputDialog.getText(
            self,
            self.tr("设置密码"),
            self.tr("输入新密码:"),
            QLineEdit.Password,
        )
        if ok and password:
            self.configManager.set_config_value("password", password)
            self.passwordCard.setContent("******")
            InfoBar.success(
                self.tr("密码已更新"),
                self.tr("密码已成功更新"),
                duration=1500,
                parent=self,
            )

    def __initLayout(self):
        self.settingLabel.move(36, 30)

        # add cards to group
        self.musicInThisPCGroup.addSettingCard(self.musicFolderCard)
        self.musicInThisPCGroup.addSettingCard(self.downloadFolderCard)

        self.personalGroup.addSettingCard(self.micaCard)
        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.themeColorCard)
        self.personalGroup.addSettingCard(self.zoomCard)
        self.personalGroup.addSettingCard(self.languageCard)

        self.materialGroup.addSettingCard(self.blurRadiusCard)

        self.updateSoftwareGroup.addSettingCard(self.updateOnStartUpCard)

        self.aboutGroup.addSettingCard(self.helpCard)
        self.aboutGroup.addSettingCard(self.feedbackCard)
        self.aboutGroup.addSettingCard(self.aboutCard)

        # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)
        self.expandLayout.addWidget(self.musicInThisPCGroup)
        self.expandLayout.addWidget(self.weatherGroup)
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.materialGroup)
        self.expandLayout.addWidget(self.updateSoftwareGroup)
        self.expandLayout.addWidget(self.aboutGroup)

    def __showRestartTooltip(self):
        """show restart tooltip"""
        InfoBar.success(
            self.tr("Updated successfully"),
            self.tr("Configuration takes effect after restart"),
            duration=1500,
            parent=self,
        )

    def __onDownloadFolderCardClicked(self):
        """download folder card clicked slot"""
        folder = QFileDialog.getExistingDirectory(self, self.tr("Choose folder"), "./")
        if not folder or cfg.get(cfg.downloadFolder) == folder:
            return

        cfg.set(cfg.downloadFolder, folder)
        self.downloadFolderCard.setContent(folder)

    def __connectSignalToSlot(self):
        """connect signal to slot"""
        cfg.appRestartSig.connect(self.__showRestartTooltip)

        # music in the pc
        self.downloadFolderCard.clicked.connect(self.__onDownloadFolderCardClicked)

        # personalization
        self.themeCard.optionChanged.connect(lambda ci: setTheme(cfg.get(ci)))
        self.themeColorCard.colorChanged.connect(setThemeColor)
        self.micaCard.checkedChanged.connect(signalBus.micaEnableChanged)

        # about
        self.feedbackCard.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(FEEDBACK_URL))
        )


if __name__ == "__main__":
    setTheme(Theme.DARK)
    app = QApplication(sys.argv)
    window = SettingInterface()
    window.show()
    sys.exit(app.exec())
