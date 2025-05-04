from rag.rag_retriever import RagRetriever
from rag.llm_generator import LLMGenerator


class RagPipeline:
    """
    RAG 流水线类，整合检索和生成功能。
    """

    def __init__(self, retriever: RagRetriever, generator: LLMGenerator):
        """
        初始化 RAG 流水线。
        :param retriever: RagRetriever 实例。
        :param generator: LLMGenerator 实例。
        """
        self.retriever = retriever
        self.generator = generator

    def run(self, query, k=5):
        """
        执行 RAG 流程。
        :param query: 用户查询。
        :param k: 检索的文档数量。
        :return: 最终生成的回答。
        """
        # 检索相关文档
        docs = self.retriever.retrieve(query, k)
        # 生成回答
        context = "\n".join([doc.page_content for doc in docs])
        answer = self.generator.qa_context_predict(query, context)
        return answer
