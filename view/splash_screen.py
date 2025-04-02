from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
)

from managers import ConfigManager
from view.main_window import Main_Window


class SplashScreen(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.password_verified = False  # 添加标志变量，初始为 False
        self.main_window_shown = False  # 新增标志变量，防止重复显示主界面

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: white;")

        # 初始化配置
        ConfigManager.initialize_config()
        self.config_manager = ConfigManager()
        # 检查是否需要密码
        if self.config_manager.get_config_value("password") == "":
            self.password_verified = True  # 如果不需要密码，直接标记为已验证
            self.closeEvent(None)
            return

        # 设置背景图片
        self.label = QLabel()
        pixmap = QPixmap(":/images/logo.png")
        self.label.setPixmap(pixmap)

        # 密码输入框
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入密码...")
        self.password_input.setEchoMode(QLineEdit.Password)

        # 确认按钮
        self.confirm_button = QPushButton("确认")
        self.confirm_button.clicked.connect(self.check_password)

        # 布局
        layout = QVBoxLayout()
        layout.addWidget(self.label, alignment=Qt.AlignCenter)

        password_layout = QHBoxLayout()
        password_layout.addWidget(self.password_input)
        password_layout.addWidget(self.confirm_button)

        layout.addLayout(password_layout)
        self.setLayout(layout)

    def check_password(self):
        """验证密码是否正确。"""
        input_password = self.password_input.text()
        saved_password = self.config_manager.get_config_value("password")
        if input_password == saved_password:
            self.password_verified = True  # 标记密码验证成功
            self.closeEvent(None)
        else:
            self.password_input.clear()

    def show_main_window(self):
        """显示主界面并关闭闪屏。"""
        self.main_window = Main_Window()
        self.main_window.show()
        self.close()

    def closeEvent(self, event):
        """仅在密码验证成功时显示主界面。"""
        if self.password_verified and not self.main_window_shown:
            self.main_window_shown = True  # 标记主界面已显示
            self.show_main_window()
        else:
            event.accept()  # 允许关闭窗口，但不显示主界面
