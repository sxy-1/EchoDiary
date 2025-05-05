from concurrent.futures import ThreadPoolExecutor
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
from qfluentwidgets import StateToolTip
from PySide6.QtCore import QTimer, Qt
import markdown
from qfluentwidgets import (
    FluentTranslator,
    TextEdit,
    CommandBar,
    Action,
)
from qfluentwidgets import FluentIcon as FIF
from managers import DiaryManager
from models.diary import Diary
from rag.llm_generator import LLMGenerator
from common import signalBus
from view.chat_window import ChatWindow, LlmThread

from PySide6.QtWidgets import QPushButton
from rag import RagRetriever


class EditorInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.executor = ThreadPoolExecutor(max_workers=1)  # 创建线程池
        self.rag_retriever = None
        self.setObjectName("EditorInterface")
        self.diary_manager = DiaryManager()
        self.llm_generator = LLMGenerator()
        self.html = None

        self.initUI()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_preview)
        self.timer.start(300)  # Update preview every 300 milliseconds

        self.diary = None
        # 自动加载当日日记
        self.load_diary_to_text_edit()

    def initUI(self):
        self.stateTooltip = None
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
                Action(FIF.PENCIL_INK, self.tr("AI 扩写")),
                Action(FIF.SHARE, self.tr("Share")),
                Action(FIF.SAVE, self.tr("Save"), shortcut="Ctrl+S"),
            ]
        )

        # 绑定 Save 按钮到 self.save_file 方法
        save_action = bar.actions()[-1]  # Assuming Save is the last added action
        save_action.triggered.connect(self.save_file)

        # Share action
        share_action = bar.actions()[-2]
        share_action.triggered.connect(self.share_file)

        # AI 扩写
        diary_generate_action = bar.actions()[-3]
        diary_generate_action.triggered.connect(self.diary_generate)

        bar.addHiddenActions(
            [
                Action(FIF.SETTING, self.tr("Settings"), shortcut="Ctrl+I"),
            ]
        )
        top_layout.addWidget(bar)

        # 添加展开按钮到 top_layout 的右侧
        self.chat_toggle_button = QPushButton("◀")  # 左三角按钮
        self.chat_toggle_button.setFixedSize(20, 20)
        self.chat_toggle_button.clicked.connect(self.toggle_chat_window)
        top_layout.addWidget(self.chat_toggle_button, alignment=Qt.AlignRight)

        # Layout for text editor, preview, and chat window
        editor_layout = QHBoxLayout()
        self.text_edit = TextEdit()
        self.text_edit.setTabStopDistance(30)  # Set tab stop width
        editor_layout.addWidget(self.text_edit)

        self.preview = TextEdit()
        self.preview.setReadOnly(True)
        editor_layout.addWidget(self.preview)

        # 创建聊天窗口
        self.chat_window = ChatWindow(llm_generator=self.llm_generator)
        self.chat_window.setVisible(False)  # 默认隐藏
        editor_layout.addWidget(self.chat_window)  # 添加到 editor_layout

        main_layout.addLayout(top_layout)
        main_layout.addLayout(editor_layout)
        self.setLayout(main_layout)
        self.chat_window.send_message = self.send_message

    # # 重写 chat_window 的 send_message 方法
    # def send_message(self):
    #     """发送消息并获取AI回复"""
    #     message = self.chat_window.input_field.text().strip()
    #     if not message:
    #         return
    #     # llm tools
    #     tools = [
    #         Tool(
    #             name="GetCurrentDiary",
    #             func=self.get_current_diary,
    #             description="获取当前用户编辑框里的日记",
    #         ),
    #         # Tool(
    #         #     name="SetCurrentDiary",
    #         #     func=self.set_current_diary,
    #         #     description="设置当前用户编辑框里的日记",
    #         # ),
    #         # Tool(name="RetrieveSimilarDiaries", func=retrieve_similar_diaries_tool, description="找回最相关的k个日记"),
    #         # Tool(name="ExpandDiary", func=expand_diary_tool, description="扩写日记"),
    #     ]
    #     llm = self.llm_generator.llm
    #     common_prompt = PromptTemplate(
    #         input_variables=["user_query", "tool_result", "chat_history"],
    #         template=DIARY_COMMON_PROMPT,
    #     )
    #     agent = initialize_agent(
    #         tools=tools,
    #         llm=llm,
    #         agent="zero-shot-react-description",
    #         verbose=True,
    #         agent_executor_kwargs={"prompt": common_prompt},
    #         handle_parsing_errors=True,
    #     )
    #     print(self.chat_window.chat_manager.get_recent_messages())
    #     result = agent.invoke(
    #         {
    #             "input": message,  # 将 user_query 改为 input
    #             "tool_result": "",  # 首次为空，后续可传上一步结果
    #             "chat_history": self.chat_window.chat_manager.get_recent_messages(),
    #         }
    #     )

    #     # 显示用户消息
    #     self.chat_window.add_message(
    #         "你", "user_avatar.png", message, alignment=Qt.AlignRight
    #     )
    #     self.chat_window.input_field.clear()

    #     # 禁用输入区域并显示进度条
    #     self.chat_window.input_field.setEnabled(False)
    #     self.chat_window.send_button.setEnabled(False)
    #     self.chat_window.progress_bar.show()

    #     # # 在后台线程中处理LLM请求
    #     # self.llm_thread = LlmThread(self.chat_window.chat_manager, result)
    #     # self.llm_thread.response_ready.connect(self.chat_window.handle_ai_response)
    #     # self.llm_thread.start()
    #     self.chat_window.handle_ai_response(result["output"])
    # 重写 chat_window 的 send_message 方法
    def send_message(self):
        message = self.chat_window.input_field.text().strip()
        if not message:
            return

        # 显示用户消息
        self.chat_window.add_message(
            "你", "user_avatar.png", message, alignment=Qt.AlignRight
        )
        self.chat_window.input_field.clear()

        # 禁用输入区域并显示进度条
        self.chat_window.input_field.setEnabled(False)
        self.chat_window.send_button.setEnabled(False)
        self.chat_window.progress_bar.show()
        context = self.diary_manager.get_all_diaries_str()
        self.rag_retriever = RagRetriever(context)
        context = self.rag_retriever.retrieve(message, k=3)
        print("context", context)
        # 在后台线程中处理LLM请求
        self.llm_thread = LlmThread(
            self.chat_window.chat_manager,
            input=message,
            diary_content=self.text_edit.toPlainText(),
            context=context,
        )
        self.llm_thread.response_ready.connect(self.chat_window.handle_ai_response)
        self.llm_thread.start()

    def get_current_diary(self, tool_input=None):
        """获取当前用户编辑框里的日记"""
        return self.text_edit.toPlainText()

    def set_current_diary(self, diary: str):
        """设置当前用户编辑框里的日记"""
        self.text_edit.setPlainText(diary)

    def toggle_chat_window(self):
        """展开或折叠聊天窗口"""
        if self.chat_window.isVisible():
            self.chat_window.setVisible(False)
            self.chat_toggle_button.setText("◀")  # 左三角按钮
        else:
            self.chat_window.setVisible(True)
            self.chat_toggle_button.setText("▶")  # 右三角按钮

    def update_preview(self):
        text = self.text_edit.toPlainText()

        self.html = markdown.markdown(
            text, extensions=["extra", "markdown.extensions.toc"]
        )
        self.preview.setHtml(self.html)

        # Alternative method
        # self.preview.setMarkdown(text)

    def save_file(self):
        print("保存文件")

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        update_data = {
            "content": self.text_edit.toPlainText(),
            "update_time": current_time,
            "create_time": self.diary.create_time or current_time,
        }

        self.diary = self.diary.copy(update=update_data)
        res = self.diary_manager.save_diary(self.diary)
        print("保存结果", res)

    def load_diary_to_text_edit(self, date=None):
        print("load_diary_to_text_edit" + str(date))
        date = date or str(datetime.now().date())
        self.diary = self.diary_manager.load_diary(date)
        if not self.diary:
            self.diary = Diary(
                date=date,
            )
        self.text_edit.setPlainText(self.diary.content)

    def share_file(self):
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

    def diary_generate(self):
        try:
            signalBus.editor_interface_generate_finished_signal.connect(
                self.update_ui_with_response
            )
            self.stateTooltip = StateToolTip("AI正在生成", "客官请耐心等待哦~~", self)
            # 移动到perview右下角
            preview_geometry = self.preview.geometry()
            tooltip_x = (
                preview_geometry.x()
                + preview_geometry.width()
                - self.stateTooltip.width()
            )
            tooltip_y = (
                preview_geometry.y()
                + preview_geometry.height()
                - self.stateTooltip.height()
            )
            self.stateTooltip.move(tooltip_x, tooltip_y)
            self.stateTooltip.show()

            self.text_edit.setEnabled(False)

            # 提交生成任务到线程池
            future = self.executor.submit(
                self.llm_generator.diary_generate_predict, self.text_edit.toPlainText()
            )
            future.add_done_callback(self.on_generate_finished)
        except Exception as e:
            print("生成失败", e)
            self.stateTooltip.setContent("生成失败")
            self.stateTooltip.setState(True)
            self.stateTooltip = None

    def on_generate_finished(self, future):
        # 在主线程中更新 UI
        try:
            response = future.result()
            print("生成结果", response)
            signalBus.editor_interface_generate_finished_signal.emit(response)
        except Exception as e:
            print("生成失败", e)
            signalBus.editor_interface_generate_finished_signal.emit("")

    def update_ui_with_response(self, response):
        try:
            print(
                "开始更新UI", response[:30] + "..." if len(response) > 30 else response
            )
            if len(response) > 0:
                self.text_edit.setPlainText(response)
            self.text_edit.setEnabled(True)
            if self.stateTooltip:
                self.stateTooltip.setContent("生成完成啦 😆")
                self.stateTooltip.setState(True)
                self.stateTooltip = None

            print("UI更新完成")
        except Exception as e:
            print("UI更新失败:", str(e))


if __name__ == "__main__":
    # setTheme(Theme.DARK)

    app = QApplication(sys.argv)

    # Install translator
    translator = FluentTranslator()
    app.installTranslator(translator)

    w = EditorInterface()
    w.show()
    app.exec()
