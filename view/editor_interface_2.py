import sys
from datetime import datetime

from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication, QHBoxLayout, QTextBrowser

from PySide6.QtCore import QTimer
import markdown
from qfluentwidgets import setTheme, Theme, FluentTranslator, PushButton, PrimaryPushButton,TextEdit


class EditorInterface2(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("EditorInterface2")
        self.initUI()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_preview)
        self.timer.start(300)  # Update preview every 300 milliseconds

    def initUI(self):
        main_layout = QVBoxLayout()

        # Top layout for buttons
        top_layout = QHBoxLayout()
        save_button = PrimaryPushButton(text = "Save")
        date_button = PrimaryPushButton(text = datetime.now().strftime("%Y-%m-%d"))
        top_layout.addWidget(save_button)
        top_layout.addWidget(date_button)

        # Layout for text editor and preview
        editor_layout = QHBoxLayout()
        self.text_edit = TextEdit()
        self.text_edit.setTabStopDistance(30)  # Set tab stop width
        editor_layout.addWidget(self.text_edit)

        # self.preview = TextEdit()
        # self.preview.setReadOnly(True)

        # Alternative method
        self.preview = QTextBrowser()

        editor_layout.addWidget(self.preview)

        main_layout.addLayout(top_layout)
        main_layout.addLayout(editor_layout)
        self.setLayout(main_layout)

    def update_preview(self):
        text = self.text_edit.toPlainText()

        # html = markdown.markdown(text, extensions=['extra', 'markdown.extensions.toc'])
        # self.preview.setHtml(html)
        #
        # Alternative method
        self.preview.setMarkdown(text)


if __name__ == '__main__':
    # setTheme(Theme.DARK)

    app = QApplication(sys.argv)

    # Install translator
    translator = FluentTranslator()
    app.installTranslator(translator)

    w = EditorInterface2()
    w.show()
    app.exec()