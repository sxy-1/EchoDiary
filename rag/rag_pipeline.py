class RAGPipeline:
    """
    RAG 流水线类，整合检索和生成功能。
    """

    def __init__(self, retriever, generator):
        """
        初始化 RAG 流水线。
        :param retriever: RAGRetriever 实例。
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
        answer = self.generator.generate(query, docs)
        return answer
