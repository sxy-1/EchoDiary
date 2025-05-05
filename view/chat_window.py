import socket
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
    QTextEdit,
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QThread, Signal
from rag.llm_chat_with_history import LlmChatWithHistory
from PySide6.QtGui import QTextOption


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
        message_label = QTextEdit(message)
        message_label.setReadOnly(True)  # 设置为只读
        message_label.setStyleSheet(
            """
            background-color: #f0f0f0;
            border-radius: 10px;
            padding: 8px;
            margin: 0px;
            """
        )
        message_label.setWordWrapMode(
            QTextOption.WrapAtWordBoundaryOrAnywhere
        )  # 启用自动换行
        message_label.setFocusPolicy(Qt.NoFocus)  # 禁用焦点
        message_label.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 隐藏滚动条
        message_label.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 隐藏滚动条

        # 动态调整高度
        message_label.document().setTextWidth(message_label.viewport().width())
        document_height = message_label.document().size().height()
        message_label.setFixedHeight(document_height + 10)  # 添加额外的高度以适应边距

        message_layout.addWidget(username_label)
        message_layout.addWidget(message_label)
        message_widget.setLayout(message_layout)
        return message_widget


class SocketThread(QThread):
    """用于后台处理Socket通信的线程"""

    message_received = Signal(str)

    def __init__(self, host="127.0.0.1", port=5000):
        super().__init__()
        self.host = host
        self.port = port
        self.running = True

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            try:
                client_socket.connect((self.host, self.port))
                print(f"Connected to server at {self.host}:{self.port}")
                while self.running:
                    data = client_socket.recv(1024)  # 接收数据
                    if not data:
                        break
                    print(f"Received data: {data.decode('utf-8')}")

                    decoded_message = data.decode("utf-8")
                    if "转写" in decoded_message or "林黛玉" in decoded_message:
                        continue
                    print(f"Received message: {decoded_message}")
                    self.message_received.emit(decoded_message)
            except ConnectionRefusedError:
                print("Failed to connect to the server. Is it running?")
            except Exception as e:
                print(f"Socket error: {e}")

    def stop(self):
        """停止线程"""
        self.running = False
        self.quit()
        self.wait()


class ChatWindow(QMainWindow):
    def __init__(self, llm_generator):
        super().__init__()
        self.setWindowTitle("AI聊天界面")
        self.setGeometry(100, 100, 500, 700)
        # 设置深色背景
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #2b2b2b;  /* 深灰色背景 */
                color: #ffffff;  /* 默认字体颜色为白色 */
            }
            QListWidget {
                background-color: #3c3c3c;  /* 聊天记录区域背景 */
                color: #ffffff;  /* 聊天记录字体颜色 */
            }
            QLineEdit {
                background-color: #444444;  /* 输入框背景 */
                color: #ffffff;  /* 输入框字体颜色 */
                border: 1px solid #555555;  /* 边框颜色 */
                border-radius: 5px;  /* 圆角 */
            }
            QPushButton {
                background-color: #555555;  /* 按钮背景 */
                color: #ffffff;  /* 按钮字体颜色 */
                border: none;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #666666;  /* 按钮悬停背景 */
            }
            QPushButton:pressed {
                background-color: #777777;  /* 按钮按下背景 */
            }
            """
        )
        # 初始化LLM相关组件
        self.chat_manager = LlmChatWithHistory(llm_generator)
        self.llm_thread = None
        self.socket_thread = None

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

        # 语音按钮
        self.voice_button = QPushButton("语音")
        self.voice_button.setCheckable(True)
        self.voice_button.clicked.connect(self.toggle_voice_mode)
        input_layout.addWidget(self.voice_button)

        main_layout.addLayout(input_layout)

        # 欢迎消息
        self.add_message(
            "AI助手",
            "ai_avatar.png",
            "你好！我是AI助手，有什么可以帮您的吗？",
            alignment=Qt.AlignLeft,
        )

        # 启动Socket线程
        self.start_socket_thread()

    def toggle_voice_mode(self):
        """切换语音模式"""
        if self.voice_button.isChecked():
            self.voice_button.setStyleSheet("background-color: #87CEEB;")  # 高亮
        else:
            self.voice_button.setStyleSheet("")  # 恢复默认样式

    def start_socket_thread(self):
        """启动Socket通信线程"""
        self.socket_thread = SocketThread()
        self.socket_thread.message_received.connect(self.send_message)
        self.socket_thread.start()

    def add_message(self, username, avatar_path, message, alignment=Qt.AlignLeft):
        """添加一条消息到聊天记录"""
        message_widget = ChatMessageWidget(username, avatar_path, message, alignment)
        list_item = QListWidgetItem()
        list_item.setSizeHint(message_widget.sizeHint())
        self.chat_list.addItem(list_item)
        self.chat_list.setItemWidget(list_item, message_widget)
        self.chat_list.scrollToBottom()

    def send_message(self, message):
        """发送消息并获取AI回复"""
        print(f"发送消息: {message}")
        print(f"语音模式: {self.voice_button.isChecked()}")
        if message and not self.voice_button.isChecked():
            # 非语音模式下不处理消息
            return

        if not message:
            message = self.input_field.text().strip()
            if message:
                self.input_field.clear()
            else:
                return
        # 显示用户消息
        self.add_message("你", "user_avatar.png", message, alignment=Qt.AlignRight)

        # 显示用户消息
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

    def closeEvent(self, event):
        """关闭窗口时停止Socket线程"""
        if self.socket_thread:
            self.socket_thread.stop()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication([])
    from rag.llm_generator import LLMGenerator

    llm = LLMGenerator()
    window = ChatWindow(llm)
    window.show()
    app.exec()
