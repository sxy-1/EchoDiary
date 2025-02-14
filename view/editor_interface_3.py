import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, Qt
from qfluentwidgets import PrimaryPushButton, setTheme, Theme, FluentTranslator
from datetime import datetime

from qframelesswindow.webengine import FramelessWebEngineView

# Vditor HTML代码
html = """
<html>
    <head>
        <title>Vditor Editor</title>
        <link rel="stylesheet" href="https://unpkg.com/vditor/dist/index.css" />
        <script src="https://unpkg.com/vditor/dist/index.min.js"></script>
    </head>    
    <body>
        <div id="content"></div>
        <script>
            var vditor = null;
            window.onload = function() {
                vditor = new Vditor(document.getElementById('content'), {
                    cache: {
                        enable: false
                    },
                    "mode": "ir",
                    "preview": {
                        "mode": "both"
                    }
                });
            }
            function saveContent() {
                var content = vditor.getValue();
                // 在此处添加保存逻辑,例如将内容写入文件
                console.log(content);
            }
        </script>
    </body>
</html>
"""

class EditorInterface3(QWidget):
    def __init__(self,parent=None):
        super().__init__()
        self.setObjectName("EditorInterface3")

        # self.setWindowTitle("Vditor Editor")

        # Create central widget and layout
        # central_widget = QWidget()
        main_layout = QVBoxLayout()
        # central_widget.setLayout(main_layout)
        # self.setCentralWidget(central_widget)

        # Top layout for buttons
        top_layout = QHBoxLayout()
        save_button = PrimaryPushButton(text="Save")
        save_button.clicked.connect(self.save_content)
        date_button = PrimaryPushButton(text=datetime.now().strftime("%Y-%m-%d"))
        top_layout.addWidget(save_button)
        top_layout.addWidget(date_button)
        # main_layout.addLayout(top_layout)

        # Create QWebEngineView and load Vditor
        self.browser = FramelessWebEngineView(self)
        self.browser.setHtml(html)
        # top_layout.addWidget(self.browser)

        self.setLayout(main_layout)
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.browser)

    def save_content(self):
        self.browser.page().runJavaScript("saveContent();")

    def update_preview(self, html):
        self.browser.setHtml(html)

if __name__ == '__main__':
    setTheme(Theme.DARK)

    app = QApplication(sys.argv)

    # Install translator
    translator = FluentTranslator()
    app.installTranslator(translator)

    w = EditorInterface3()
    w.show()
    app.exec()