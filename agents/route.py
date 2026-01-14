from typing import Dict, Any
from langchain.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from state.store import StateStore
from schemas.chat import ChatResponse, ToolCall
from tools.registry import list_tools
from utils.logger import get_logger
# from agents.agent import build_agent
from agents.agent import build_llm_with_tools
import json
import re

_default_store = StateStore()
MAX_HISTORY = 20
logger = get_logger(__name__)


# def extract_city(text: str) -> str:
#     # 清理常见口语词，保留城市
#     text = re.sub(r"(天气|怎么样|如何|气温|温度|查询|一下)", "", text)
#     text = text.replace("在", "").replace("的", "").strip()
#     return text

# def extract_topic(text: str) -> str:
#     # 清理常见口语词，保留主题
#     text = re.sub(r"(新闻|最新|一下|关于|有关)", "", text)
#     text = text.replace("的", "").strip()
#     return text

# def handle_weather_tool(message: str, tools: Dict[str, Any], tool_calls: int) -> tuple[str, Dict[str, Any]]:
#     tool = tools["weather"]
#     city = extract_city(message)
#     if not city:
#         return "请提供城市名称以查询天气。", {}
#     tool_response = tool.handler(city=city, date="今天")
#     answer = f"{city}的天气是{tool_response['temperature']}，{tool_response['condition']}。"
#     last_tool = {
#         "name": "weather",
#         "parameters": {"city": city},
#         "response": tool_response,
#     }
#     tool_calls += 1
#     return answer, last_tool

# def handle_news_tool(message: str, tools: Dict[str, Any], tool_calls: int) -> tuple[str, Dict[str, Any]]:
#     tool = tools["news"]
#     topic = extract_topic(message)
#     if not topic:
#         return "请提供新闻主题以获取新闻。", {}

#     tool_response = tool.handler(topic=topic)
#     items = tool_response.get("items", [])
#     if not items:
#         return "暂时没有找到相关新闻。", {}

#     news_item = tool_response["items"][0]
#     answer = f"最新的{topic}新闻：{news_item['title']}，来源：{news_item['source']}，日期：{news_item['ctime']}。"
#     last_tool = {
#         "name": "news",
#         "parameters": {"topic": topic},
#         "response": tool_response,
#     }
#     tool_calls += 1
#     return answer, last_tool

# ROUTES =  [
#     ("天气", "weather", handle_weather_tool),
#     ("新闻", "news", handle_news_tool),
# ]

def handle_message(
    session_id: str, message: str, output_format: str = "text", state_store=_default_store
) -> ChatResponse:
    logger.info(f"开始处理会话 {session_id} 的消息：{message}")
    # 获取当前会话状态
    state = state_store.get_state(session_id)

    # 消息记录
    messages = state.get("messages", [])
    # 工具调用次数计数
    # tool_calls = state.get("tool_calls", 0)

    # 可用工具列表
    tools = list_tools()

    answer = ""
    last_tool = {}

    # 路由匹配：命中即处理，否则走兜底
    # for route_keyword, tool_name, handler in ROUTES:
    #     if route_keyword in message and tool_name in tools:
    #         answer, last_tool = handler(message, tools, tool_calls)
    #         logger.info(f"会话 {session_id} 将消息路由到工具 {tool_name}，消息内容为：{message}，回答为：{answer}")
    #         break
    # else:
    #     answer = "抱歉，我无法处理您的请求。"

    # 路由匹配：使用 Agent 处理
    # lc_messages = []
    # # 转换为 LangChain 消息格式
    # for msg in messages:
    #     if msg["role"] == "user":
    #         lc_messages.append(HumanMessage(content=msg["content"]))
    #     elif msg["role"] == "assistant":
    #         lc_messages.append(AIMessage(content=msg["content"]))

    # # 将用户新消息添加到消息列表
    # lc_messages.append(HumanMessage(content=message))
    # # 构建并调用 Agent
    # agent = build_agent()
    # result = agent.invoke({"messages": lc_messages})
    # answer = result["messages"][-1].content

    # # 提取使用的工具信息
    # for msg in reversed(result["messages"]):
    #   tool_calls = getattr(msg, "tool_calls", None)
    #   if tool_calls:
    #       last = tool_calls[-1]
    #       last_tool = {
    #           "name": last.get("name", ""),
    #           "parameters": last.get("args", {}),
    #       }
    #       break

    # 使用 LLM 结合工具处理
    llm = build_llm_with_tools()

    # 系统消息，设定助手角色
    system_message = SystemMessage(content=(
        "你是中文问答助手。涉及天气或新闻查询时必须调用对应工具获取结果，"
        "不要凭空编造。其他问题直接回答。"
    ))

    lc_messages = []
    lc_messages.append(system_message)
    # 转换为 LangChain 消息格式
    for msg in messages:
        if msg["role"] == "user":
            lc_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            lc_messages.append(AIMessage(content=msg["content"]))

    # 将用户新消息添加到消息列表
    lc_messages.append(HumanMessage(content=message))
    # 调用 LLM 处理
    result = llm.invoke(lc_messages)
    tool_calls = getattr(result, "tool_calls", None)
    if not tool_calls:
        logger.info(f"会话 {session_id} LLM 无需调用工具，直接回答。")
        answer = result.content
        last_tool = {}
    else:
        # 提取本次对话需要用的工具
        call = tool_calls[0]
        tool_name =  call["name"]
        tool_args = call["args"]
        tool_result = tools[tool_name].handler(**tool_args)
        logger.info(f"会话 {session_id} LLM 调用工具 {tool_name}，参数：{tool_args}，结果：{tool_result}")

        # 把工具结果传给 LLM 生成最终回答
        lc_messages.append(AIMessage(content=result.content))
        lc_messages.append(ToolMessage(
            tool_name=tool_name,
            content=json.dumps(tool_result),
            tool_call_id=call["id"],
        ))

        final_result = llm.invoke(lc_messages)
        answer = final_result.content
        last_tool = {
            "name": tool_name,
            "parameters": tool_args,
        }

    # 确保 answer 是字符串类型
    if not isinstance(answer, str):
        answer = str(answer)

    # 更新消息记录
    messages.append({"role": "user", "content": message})
    messages.append({"role": "assistant", "content": answer})
    logger.info(f"会话 {session_id} 更新消息记录：{messages[-2:]}")

    # 保持消息记录在最大限制内
    messages = messages[-MAX_HISTORY:]

    # 更新状态
    new_state = {
        "messages": messages,
        "last_tool": last_tool,
        # "tool_calls": tool_calls,
    }
    state_store.set_state(session_id, new_state)
    logger.info(f"会话 {session_id} 更新状态：{new_state}")

    if output_format == "json":
        answer = json.dumps({"text": answer, "state": new_state})

    # 构建响应
    response = ChatResponse(
        session_id=session_id,
        answer=answer,
        tool_used=ToolCall(
            tool_name=last_tool["name"], parameters=last_tool["parameters"]
        ) if last_tool else None,
        state=new_state,
    )

    return response
