import sys
from datetime import datetime

from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QApplication,
    QHBoxLayout,
    QFileDialog,
)

from PySide6.QtCore import QTimer, Qt
import markdown
from qfluentwidgets import (
    FluentTranslator,
    PrimaryPushButton,
    TextEdit,
    CommandBar,
    Action,
)

from qfluentwidgets import FluentIcon as FIF
from managers import DiaryManager
from models.diary import Diary


class EditorInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("EditorInterface")
        self.diary_manager = DiaryManager()
        self.html = None

        self.initUI()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_preview)
        self.timer.start(300)  # Update preview every 300 milliseconds

        # 自动加载当日日记
        self.load_diary_to_text_edit()

    def initUI(self):
        main_layout = QVBoxLayout()

        # Top layout for buttons
        top_layout = QHBoxLayout()
        bar = CommandBar()
        bar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        bar.addActions(
            [
                Action(FIF.ADD, self.tr("Add")),
                Action(FIF.ROTATE, self.tr("Rotate")),
                Action(FIF.ZOOM_IN, self.tr("Zoom in")),
                Action(FIF.ZOOM_OUT, self.tr("Zoom out")),
            ]
        )
        bar.addSeparator()
        bar.addActions(
            [
                Action(FIF.EDIT, self.tr("Edit"), checkable=True),
                Action(FIF.INFO, self.tr("Info")),
                Action(FIF.DELETE, self.tr("Delete")),
                Action(FIF.SHARE, self.tr("Share")),
                Action(FIF.SAVE, self.tr("Save")),
            ]
        )

        # 绑定 Save 按钮到 self.save_file 方法
        save_action = bar.actions()[-1]  # Assuming Save is the last added action
        save_action.triggered.connect(self.save_file)

        share_action = bar.actions()[-2]
        share_action.triggered.connect(self.share_file)

        bar.addHiddenActions(
            [
                Action(FIF.SETTING, self.tr("Settings"), shortcut="Ctrl+I"),
            ]
        )
        top_layout.addWidget(bar)
        save_button = PrimaryPushButton(text="Save")
        save_button.clicked.connect(self.save_file)

        # date_button = PrimaryPushButton(text=datetime.now().strftime("%Y-%m-%d"))
        # top_layout.addWidget(save_button)
        # top_layout.addWidget(date_button)

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

        self.html = markdown.markdown(
            text, extensions=["extra", "markdown.extensions.toc"]
        )
        self.preview.setHtml(self.html)

        # Alternative method
        # self.preview.setMarkdown(text)

    def save_file(self):
        # 获取文件保存位
        # file_path, _ = QFileDialog.getSaveFileName(self, "Save File", os.path.expanduser("~"), "Text Files (*.txt)")
        print("保存文件")
        diary_dict = {
            "date": str(datetime.now().date()),
            "time": str(datetime.now().time()),
            "note": "这是一个示例备注",
            "weather": "晴天",
            "content": self.text_edit.toPlainText(),
        }
        diary = Diary(**diary_dict)
        res = self.diary_manager.save_diary(diary)
        print("保存结果", res)

    def load_diary_to_text_edit(self):
        date = str(datetime.now().date())
        diary = self.diary_manager.load_diary(date)
        if not diary:
            print("没有找到日记")
        else:
            self.text_edit.setPlainText(diary.content)

    def share_file(self):
        # img = html_to_image(self.html)
        # save_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Files (*.png);;All Files (*)")
        # if save_path:
        #     img.save(save_path)
        # Create a QWebEngineView to render the HTML
        self.webview = QWebEngineView()
        self.webview.setHtml(self.html)

        # Wait until the HTML is fully loaded, then take a screenshot
        QTimer.singleShot(1000, self.capture_screenshot)

    def capture_screenshot(self):
        # Set the size of the webview to the desired image size
        self.webview.resize(800, 600)
        self.webview.show()

        # Capture the screenshot and save it to a file
        # self.webview.grab().save('screenshot.png')

        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save Image", "", "PNG Files (*.png);;All Files (*)"
        )
        if save_path:
            self.webview.grab().save(save_path)


if __name__ == "__main__":
    # setTheme(Theme.DARK)

    app = QApplication(sys.argv)

    # Install translator
    translator = FluentTranslator()
    app.installTranslator(translator)

    w = EditorInterface()
    w.show()
    app.exec()
