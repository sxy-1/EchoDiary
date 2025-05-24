from langchain_openai import ChatOpenAI
from prompts import QA_CONTEXT_PROMPT, DIARY_GENERATE_PROMPT


class LLMGenerator:
    """
    LLM 生成器类，用于根据上下文生成回答。
    """

    def __init__(self, model_name="gpt-4-turbo-preview"):
        """
        初始化 LLM 生成器。
        :param model_name: 使用的 LLM 模型名称。
        """
        print("LLMGenerator init")
        self.llm = ChatOpenAI(
            model_name=model_name,  # 或您使用的其他聊天模型
            temperature=0,
            # 其他参数...
        )
        print("LLMGenerator init done")

    def prompt_predict(self, prompt):
        print("prompt:\n", prompt)
        response = self.llm.invoke(prompt)
        print("response:\n", response)
        return response.content

    def qa_context_predict(self, query, context):
        """
        根据上下文和查询生成回答。
        :param query: 用户查询。
        :param docs: 检索到的文档列表。
        :return: LLM 生成的回答。
        """
        # 使用提示模板变量生成提示
        prompt = QA_CONTEXT_PROMPT.format(query=query, context=context)

        # 调用 LLM 并返回响应
        response = self.prompt_predict(prompt)
        return response

    def diary_generate_predict(self, input_text):
        """
        根据上下文和查询生成回答。
        :param query: 用户查询。
        :param docs: 检索到的文档列表。
        :return: LLM 生成的回答。
        """
        # 使用提示模板变量生成提示
        prompt = DIARY_GENERATE_PROMPT.format(input_text=input_text)

        # 调用 LLM 并返回响应
        response = self.prompt_predict(prompt)
        return response
