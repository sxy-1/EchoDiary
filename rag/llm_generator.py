from langchain_openai import ChatOpenAI


class LLMGenerator:
    """
    LLM 生成器类，用于根据上下文生成回答。
    """

    def __init__(self, model_name="gpt-4"):
        """
        初始化 LLM 生成器。
        :param model_name: 使用的 LLM 模型名称。
        """
        self.llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",  # 或您使用的其他聊天模型
            temperature=0.7,
            # 其他参数...
        )

    def generate(self, query, docs):
        """
        根据上下文和查询生成回答。
        :param query: 用户查询。
        :param docs: 检索到的文档列表。
        :return: LLM 生成的回答。
        """
        # 拼接检索到的文档内容作为上下文
        context = "\n".join([doc.page_content for doc in docs])
        prompt = f"""
        你是一个知识丰富的助手。根据以下上下文回答问题：
        上下文: {context}
        问题: {query}
        答案:
        """
        print("prompt:\n", prompt)
        response = self.llm.invoke(prompt)
        return response
