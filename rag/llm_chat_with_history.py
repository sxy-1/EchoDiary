from rag.llm_generator import LLMGenerator
from prompts import CHAT_SYSTEM_PROMPT, CHAT_SUMMARIZATION_PROMPT
from dotenv import load_dotenv

load_dotenv(".env/.env")


class LlmChatWithHistory:
    """
    聊天管理类，封装聊天逻辑、历史管理和自动摘要功能。
    """

    def __init__(self, llm_generator, summary_interval=10):
        self.llm_generator = llm_generator
        self.chat_history = []  # 无限增长的聊天记录列表
        self.summaries = []  # 存储摘要的列表
        self.summary_interval = summary_interval  # 每隔多少条消息触发一次摘要

    def add_user_message(self, message):
        self.chat_history.append({"role": "user", "content": message})

    def add_ai_message(self, message):
        self.chat_history.append({"role": "ai", "content": message})

    def get_recent_messages(self, count=10):
        """
        获取最近的 count 条消息。
        """
        return self.chat_history[-count:]

    def get_last_summary(self):
        """
        获取最近的一条摘要。
        """
        return self.summaries[-1] if self.summaries else None

    def _summarize_recent_messages(self):
        """
        摘要最近的 summary_interval 条消息。
        """
        if (
            len(self.chat_history) % self.summary_interval == 0
            and len(self.chat_history) > 0
        ):
            # 获取最近的 summary_interval 条消息
            recent_messages = self.get_recent_messages(self.summary_interval)
            # 格式化摘要提示
            prompt = CHAT_SUMMARIZATION_PROMPT.format(chat_history=recent_messages)
            # 调用 LLM 生成摘要
            summary_message = self.llm_generator.prompt_predict(prompt)
            # 将摘要存储到 summaries 列表中
            self.summaries.append({"role": "summary", "content": summary_message})

    def process_input(self, user_input, session_id="default"):
        """
        处理用户输入，返回 AI 响应。
        """
        # 自动摘要最近的消息（在添加用户消息之前）
        self._summarize_recent_messages()

        # 准备聊天系统提示，包含最近 10 条消息和最近一条摘要
        recent_messages = self.get_recent_messages(10)  # 不包含当前用户输入
        last_summary = self.get_last_summary()
        prompt_context = recent_messages
        if last_summary:
            prompt_context = [last_summary] + recent_messages

        # 格式化聊天系统提示（不包含当前用户输入）
        prompt = CHAT_SYSTEM_PROMPT.format(
            chat_history=prompt_context, input=user_input
        )
        # 调用 LLM 生成响应
        response = self.llm_generator.prompt_predict(prompt)

        # 添加用户消息和 AI 消息到历史记录
        self.add_user_message(user_input)
        self.add_ai_message(response)

        return response


if __name__ == "__main__":
    # 初始化 LLM 生成器
    llm_generator = LLMGenerator(model_name="gpt-3.5-turbo")

    # 初始化聊天管理器
    chat_manager = LlmChatWithHistory(llm_generator)

    while True:
        # 获取用户输入
        user_input = input("请输入你的消息 (输入 'exit' 退出): ")
        if user_input.lower() == "exit":
            print("聊天结束。")
            break
        # 处理用户输入
        response = chat_manager.process_input(user_input)
        print("AI Response:", response)

        # 查看完整历史记录和摘要
        print("Full History:", chat_manager.chat_history)
        print("Summaries:", chat_manager.summaries)
