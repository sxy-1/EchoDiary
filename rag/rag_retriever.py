from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS


class RAGRetriever:
    """
    RAG 检索器类，用于管理文档嵌入和检索。
    """

    def __init__(self, texts, embedding_model=None):
        """
        初始化 RAG 检索器。
        :param texts: 文本列表，每个文本为一个文档。
        :param embedding_model: 嵌入模型，默认为 OpenAIEmbeddings。
        """
        self.embedding_model = embedding_model or OpenAIEmbeddings()
        self.vectorstore = FAISS.from_texts(texts, self.embedding_model)

    def retrieve(self, query, k=5):
        """
        根据查询检索最相关的文档。
        :param query: 用户查询。
        :param k: 检索的文档数量。
        :return: 检索到的文档列表。
        """
        retriever = self.vectorstore.as_retriever(
            search_type="similarity", search_kwargs={"k": k}
        )
        docs = retriever.invoke(query)
        return docs
