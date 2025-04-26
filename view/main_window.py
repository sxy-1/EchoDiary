# coding:utf-8
import sys

from PySide6.QtCore import QUrl
from PySide6.QtGui import QIcon, QDesktopServices
from PySide6.QtWidgets import QApplication
from qfluentwidgets import (
    NavigationItemPosition,
    MessageBox,
    NavigationAvatarWidget,
    FluentTranslator,
    FluentWindow,
)
from qfluentwidgets import FluentIcon as FIF

# from test import MarkedCalendar
from view.calendar_interface import CalendarInterface
from view.editor_interface import EditorInterface
from view.editor_interface_2 import EditorInterface2
from view.editor_interface_3 import EditorInterface3
from view.setting_interface import SettingInterface  # 导入 SettingInterface
from dotenv import load_dotenv


class Main_Window(FluentWindow):
    def __init__(self):
        super().__init__()

        # create sub interface

        self.editorInterface = EditorInterface(self)
        self.editorInterface2 = EditorInterface2(self)
        self.editorInterface3 = EditorInterface3(self)
        self.calendarInterface = CalendarInterface(self)
        self.settingInterface = SettingInterface(self)  # 实例化 SettingInterface

        self.calendarInterface.calendar_switchTo_editor_signal.connect(
            self.calendar_switchTo_editor
        )
        self.initNavigation()
        self.initWindow()
        self.check()

    def calendar_switchTo_editor(self, date):
        print(date)
        print("cao")
        # todo: 保存原editor

        self.editorInterface.load_diary_to_text_edit(date=date)
        self.switchTo(self.editorInterface)

    def check(self):
        load_dotenv(".env/.env")

    def initNavigation(self):
        # add sub interface
        # self.addSubInterface(self.focusInterface, FIF.RINGER, '专注时段')
        self.addSubInterface(
            self.editorInterface, FIF.STOP_WATCH, "写日记editorInterface"
        )
        self.addSubInterface(
            self.editorInterface2, FIF.STOP_WATCH, "写日记editorInterface2"
        )
        self.addSubInterface(
            self.editorInterface3, FIF.STOP_WATCH, "写日记editorInterface3"
        )
        self.addSubInterface(
            self.calendarInterface, FIF.STOP_WATCH, "写日记editorInterface"
        )
        self.addSubInterface(self.settingInterface, FIF.SETTING, "设置")  # 添加设置界面

        self.navigationInterface.addWidget(
            routeKey="avatar",
            widget=NavigationAvatarWidget("zhiyiYo", "resource/images/shoko.png"),
            onClick=self.showMessageBox,
            position=NavigationItemPosition.BOTTOM,
        )
        self.navigationInterface.addItem(
            routeKey="settingInterface",
            icon=FIF.SETTING,
            text="设置",
            position=NavigationItemPosition.BOTTOM,
        )

        self.navigationInterface.setExpandWidth(280)

    def initWindow(self):
        self.resize(900, 700)
        self.setWindowIcon(QIcon(":/qfluentwidgets/images/logo.png"))
        self.setWindowTitle("PyQt-Fluent-Widgets")

        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

    def showMessageBox(self):
        w = MessageBox(
            "支持作者🥰",
            "个人开发不易，如果这个项目帮助到了您，可以考虑请作者喝一瓶快乐水🥤。您的支持就是作者开发和维护项目的动力🚀",
            self,
        )
        w.yesButton.setText("来啦老弟")
        w.cancelButton.setText("下次一定")

        if w.exec():
            QDesktopServices.openUrl(QUrl("https://afdian.net/a/zhiyiYo"))


if __name__ == "__main__":
    # setTheme(Theme.DARK)
    app = QApplication(sys.argv)

    # install translator
    translator = FluentTranslator()
    app.installTranslator(translator)

    w = Main_Window()
    w.show()
    app.exec()
