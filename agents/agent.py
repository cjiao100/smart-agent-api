from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from config.settings import settings
from pydantic import SecretStr
from tools.lc_tools import weather_tool, news_tool

def build_agent():
    llm = ChatOpenAI(
        model="qwen/qwen-2.5-72b-instruct",
        temperature=0,
        base_url=settings.api.openrouter_base_url,
        api_key=SecretStr(settings.api.openrouter_api_key),
    )

    tools = [
        weather_tool,
        news_tool,
    ]

    agent = create_agent(
        model=llm,
        tools=tools,
    )
    return agent

def build_llm_with_tools():
    llm = ChatOpenAI(
        model="google/gemini-2.5-flash",
        temperature=0,
        base_url=settings.api.openrouter_base_url,
        api_key=SecretStr(settings.api.openrouter_api_key),
    )

    return llm.bind_tools([
        weather_tool,
        news_tool,
    ])