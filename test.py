import os
import pickle
import sys
from datetime import datetime

from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication, QHBoxLayout, QTextBrowser

from PySide6.QtCore import QTimer
import markdown
from qfluentwidgets import setTheme, Theme, FluentTranslator, PushButton, PrimaryPushButton,TextEdit
import utils.config
from utils import crypter
from utils.crypter import decrypt_data


class EditorInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("EditorInterface")
        self.initUI()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_preview)
        self.timer.start(300)  # Update preview every 300 milliseconds

        # 自动加载当日日记
        self.load_file()

    def initUI(self):
        main_layout = QVBoxLayout()

        # Top layout for buttons
        top_layout = QHBoxLayout()
        save_button = PrimaryPushButton(text = "Save")
        save_button.clicked.connect(self.save_file)

        date_button = PrimaryPushButton(text = datetime.now().strftime("%Y-%m-%d"))
        top_layout.addWidget(save_button)
        top_layout.addWidget(date_button)

        # Layout for text editor and preview
        editor_layout = QHBoxLayout()
        self.text_edit = TextEdit()
        self.text_edit.setTabStopDistance(30)  # Set tab stop width
        editor_layout.addWidget(self.text_edit)

        self.preview = TextEdit()
        self.preview.setReadOnly(True)

        # Alternative method
        # self.preview = QTextBrowser()

        editor_layout.addWidget(self.preview)

        main_layout.addLayout(top_layout)
        main_layout.addLayout(editor_layout)
        self.setLayout(main_layout)

    def update_preview(self):
        text = self.text_edit.toPlainText()

        html = markdown.markdown(text, extensions=['extra', 'markdown.extensions.toc'])
        self.preview.setHtml(html)

        # Alternative method
        # self.preview.setMarkdown(text)

    def save_file(self):
        # 获取文件保存位置
        # file_path, _ = QFileDialog.getSaveFileName(self, "Save File", os.path.expanduser("~"), "Text Files (*.txt)")

        data = {
            "date": str(datetime.now().date()),
            "time": str(datetime.now().time()),
            "note": "这是一个示例备注",
            "weather": "晴天",
            "content": self.text_edit.toPlainText()
        }
        # 加密数据
        ciphertext = crypter.encrypt_data(pickle.dumps(data))

        file_path = os.path.join("./data/diary_data", str(datetime.now().strftime("%Y-%m-%d"))+".enc")
        # 如果文件路径不为空,则保存文件
        if file_path:
            try:
                with open(file_path, "wb") as f:
                    f.write(ciphertext)
            except Exception as e:
                print(f"Error saving file: {e}")

    def load_file(self,date=None):
        # 获取文件打开位置
        # file_path, _ = QFileDialog.getOpenFileName(self, "Open File", os.path.expanduser("~"), "Text Files (*.txt)")
        date = date or str(datetime.now().date().strftime("%Y-%m-%d"))
        file_path = os.path.join("./data/diary_data", date+".enc")
        # 如果文件路径不为空,则加载文件
        if file_path:
            try:
                with open(file_path, "rb") as f:
                    ciphertext = f.read()
                    data = pickle.loads(crypter.decrypt_data(ciphertext))
                    self.text_edit.setPlainText(data['content'])
            except Exception as e:
                print(f"Error loading file: {e}")

if __name__ == '__main__':
    # setTheme(Theme.DARK)

    app = QApplication(sys.argv)

    # Install translator
    translator = FluentTranslator()
    app.installTranslator(translator)

    w = EditorInterface()
    w.show()
    app.exec()