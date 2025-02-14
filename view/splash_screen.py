# splash_screen.py
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton

from view.main_window import Main_Window


class SplashScreen(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: white;")

        # 设置背景图片
        self.label = QLabel()
        pixmap = QPixmap("./resource/images/logo.png")  # 替换为您自己的背景图片路径
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
        # 在这里检查输入的密码是否正确
        password = self.password_input.text()
        if password == "123456":  # 替换为您自己的密码
            self.close()
        else:
            self.password_input.clear()



    def closeEvent(self, event):
        # 关闭闪屏后,显示主界面
        self.main_window = Main_Window()
        self.main_window.show()
        pass