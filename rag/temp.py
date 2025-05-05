from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, Tool
from dotenv import load_dotenv
import re

load_dotenv(".env/.env")


def add_numbers(inputs: str) -> str:
    """加法工具：接收两个数字，返回它们的和"""
    try:
        # 支持逗号或空格分隔
        numbers = list(map(float, re.split(r"[,\s]+", inputs.strip())))
        return str(sum(numbers))
    except Exception as e:
        return f"Error: {str(e)}"


def subtract_numbers(inputs: str) -> str:
    """减法工具：接收两个数字，返回它们的差"""
    try:
        numbers = list(map(float, re.split(r"[,\s]+", inputs.strip())))
        if len(numbers) != 2:
            return "Error: Please provide exactly two numbers."
        return str(numbers[0] - numbers[1])
    except Exception as e:
        return f"Error: {str(e)}"


# 2. 初始化工具
tools = [
    Tool(name="Add", func=add_numbers, description="用于计算两个数字的和"),
    Tool(name="Subtract", func=subtract_numbers, description="用于计算两个数字的差"),
]

# 3. 自定义 Prompt 模板
custom_prompt = PromptTemplate(
    input_variables=["input", "previous_result"],
    template=(
        "你是一个只能通过调用工具来完成任务的智能助手。\n"
        "用户的问题是：{input}\n"
        "之前的计算结果是：{previous_result}\n"
        "如果用户的问题需要用到之前的结果，请直接将“之前的计算结果”作为数字参与计算，不要重复提问。\n"
        "请严格按照工具调用格式输出，不要输出与工具调用无关的内容。\n"
        "最终请返回最终答案。"
    ),
)

# 4. 初始化 LLM
llm = ChatOpenAI(model="gpt-4", temperature=0)

# 5. 自定义 Agent
# 使用自定义的 Prompt 模板
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True,
    agent_executor_kwargs={"prompt": custom_prompt},
    handle_parsing_errors=True,
)
print("Agent initialized.")
# 6. 动态插入上下文并运行
# 第一次计算
first_query = "请帮我计算 2+3。"
first_result = agent.invoke({"input": first_query, "previous_result": ""})
print("Agent initialized2.")
# 第二次计算，带入第一次的结果
second_query = "请用上次的结果减去 4。"
second_result = agent.invoke(
    {"input": second_query, "previous_result": first_result["output"]}
)

print("第一次计算结果:", first_result)
print("第二次计算结果:", second_result)
