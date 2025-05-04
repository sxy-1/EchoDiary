# 假设你有一个包含 100 个文本的列表
from rag.llm_generator import LLMGenerator
from rag.rag_pipeline import RagPipeline
from rag.rag_retriever import RagRetriever
from tests.mock_data.test_diary.diarys import diary_content_list


from dotenv import load_dotenv

load_dotenv(".env/.env")
texts = diary_content_list
# 初始化 RAG 检索器和 LLM 生成器
retriever = RagRetriever(texts)
generator = LLMGenerator(model_name="model_name")

# 初始化 RAG 流水线
rag_pipeline = RagPipeline(retriever, generator)

# 测试流程
query = "张总叫我进办公室干什么？"
k = 1  # 检索最相关的 3 个文档
answer = rag_pipeline.run(query, k)

# 输出答案
print("答案:", answer)
