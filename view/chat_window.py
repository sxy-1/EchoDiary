from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QPushButton,
    QLabel,
    QProgressBar,
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QThread, Signal
from rag.llm_chat_with_history import LlmChatWithHistory


class LlmThread(QThread):
    """用于后台处理LLM请求的线程"""

    response_ready = Signal(str)

    def __init__(self, chat_manager, input="", diary_content="", context=""):
        """初始化线程，设置聊天管理器、输入和上下文"""

        super().__init__()
        self.chat_manager = chat_manager
        self.input = input
        self.diary_content = diary_content
        self.context = context

    def run(self):
        response = self.chat_manager.process_input(
            input=self.input, diary_content=self.diary_content, context=self.context
        )
        self.response_ready.emit(response)


class ChatMessageWidget(QWidget):
    """自定义聊天消息组件"""

    def __init__(self, username, avatar_path, message, alignment=Qt.AlignLeft):
        super().__init__()
        layout = QHBoxLayout()
        layout.setSpacing(10)

        # 根据对齐方式调整布局
        if alignment == Qt.AlignLeft:
            layout.addWidget(self.create_avatar_label(avatar_path))
            layout.addWidget(self.create_message_label(username, message))
            layout.addStretch()
        else:
            layout.addStretch()
            layout.addWidget(self.create_message_label(username, message))
            layout.addWidget(self.create_avatar_label(avatar_path))

        self.setLayout(layout)

    def create_avatar_label(self, avatar_path):
        """创建头像标签"""
        avatar_label = QLabel()
        try:
            avatar_pixmap = QPixmap(avatar_path).scaled(
                40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            avatar_label.setPixmap(avatar_pixmap)
        except Exception as e:  # 捕获通用异常并记录错误信息
            print(f"加载头像失败: {e}")
            # 如果图片加载失败，显示占位符
            avatar_label.setText("头像")
            avatar_label.setStyleSheet(
                "background-color: #ddd; border-radius: 20px; padding: 8px;"
            )
        return avatar_label

    def create_message_label(self, username, message):
        """创建消息标签"""
        message_widget = QWidget()
        message_layout = QVBoxLayout()
        message_layout.setContentsMargins(0, 0, 0, 0)

        username_label = QLabel(username)
        username_label.setStyleSheet("font-weight: bold; color: #555;")
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet(
            "background-color: #f0f0f0; border-radius: 10px; padding: 8px;"
        )

        message_layout.addWidget(username_label)
        message_layout.addWidget(message_label)
        message_widget.setLayout(message_layout)
        return message_widget


class ChatWindow(QMainWindow):
    def __init__(self, llm_generator):
        super().__init__()
        self.setWindowTitle("AI聊天界面")
        self.setGeometry(100, 100, 500, 700)

        # 初始化LLM相关组件
        self.chat_manager = LlmChatWithHistory(llm_generator)
        self.llm_thread = None

        # 主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)

        # 聊天记录区域
        self.chat_list = QListWidget()
        self.chat_list.setSpacing(10)
        main_layout.addWidget(self.chat_list)

        # 进度条（处理中状态指示）
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 0)  # 设置为不确定模式
        self.progress_bar.hide()
        main_layout.addWidget(self.progress_bar)

        # 输入区域布局
        input_layout = QHBoxLayout()

        # 文本输入框
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("输入消息...")
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)

        # 发送按钮
        self.send_button = QPushButton("发送")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        main_layout.addLayout(input_layout)

        # 欢迎消息
        self.add_message(
            "AI助手",
            "ai_avatar.png",
            "你好！我是AI助手，有什么可以帮您的吗？",
            alignment=Qt.AlignLeft,
        )

    def add_message(self, username, avatar_path, message, alignment=Qt.AlignLeft):
        """添加一条消息到聊天记录"""
        message_widget = ChatMessageWidget(username, avatar_path, message, alignment)
        list_item = QListWidgetItem()
        list_item.setSizeHint(message_widget.sizeHint())
        self.chat_list.addItem(list_item)
        self.chat_list.setItemWidget(list_item, message_widget)
        self.chat_list.scrollToBottom()

    def send_message(self):
        """发送消息并获取AI回复"""
        message = self.input_field.text().strip()
        if not message:
            return

        # 显示用户消息
        self.add_message("你", "user_avatar.png", message, alignment=Qt.AlignRight)
        self.input_field.clear()

        # 禁用输入区域并显示进度条
        self.input_field.setEnabled(False)
        self.send_button.setEnabled(False)
        self.progress_bar.show()

        # 在后台线程中处理LLM请求
        self.llm_thread = LlmThread(self.chat_manager, message)
        self.llm_thread.response_ready.connect(self.handle_ai_response)
        self.llm_thread.start()

    def handle_ai_response(self, response):
        """处理AI回复"""
        # 隐藏进度条并启用输入区域
        self.progress_bar.hide()
        self.input_field.setEnabled(True)
        self.send_button.setEnabled(True)

        # 显示AI回复
        self.add_message("AI助手", "ai_avatar.png", response, alignment=Qt.AlignLeft)


if __name__ == "__main__":
    app = QApplication([])
    window = ChatWindow()
    window.show()
    app.exec()
