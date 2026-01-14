from dataclasses import dataclass
from typing import Dict, Callable, Any, Optional
from utils.logger import get_logger
from tools.weathor_tool import WeathorTool
from tools.news_tool import NewsTool

logger = get_logger(__name__)
weather = WeathorTool()
news = NewsTool()

# 定义工具的数据结构
@dataclass
class Tool:
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: Callable[..., Dict[str, Any]]


def weather_stub(city: str, date: str = "今天") -> Dict[str, Any]:
    logger.info(f"调用天气查询函数，城市：{city}，日期：{date}")
    # 这是一个模拟的天气查询函数
    # return {"city": city, "date": date, "temperature": "25°C", "condition": "晴朗"}

    # 使用 WeathorTool 获取实际天气信息
    city_info = weather.search_city(city)
    if not city_info:
        return {"error": "未找到该城市的信息"}

    location_id = city_info["id"]
    weather_info = weather.get_current_weather(location_id)
    if not weather_info:
        return {"error": "无法获取天气信息"}

    return {
        "city": city,
        "date": date,
        "temperature": weather_info["temp"] + "°C",
        "condition": weather_info["text"],
    }


def news_stub(topic: str, source: str = "") -> Dict[str, Any]:
    logger.info(f"调用新闻查询函数，主题：{topic}，来源：{source}")
    # 这是一个模拟的新闻查询函数
    # return {
    #     "topic": topic,
    #     "source": source,
    #     "items": [
    #         {
    #             "title": "AI 助手加速企业自动化",
    #             "source": "科技日报",
    #             "date": "2024-05-10",
    #         }
    #     ],
    # }

    # 使用 NewsTool 获取实际新闻信息
    news_info = news.get_news(topic, source=source)
    logger.info(f"新闻查询结果：{news_info}")
    if not news_info:
        return {"error": "无法获取相关新闻"}
    return {
        "topic": topic,
        "source": news_info.get("source", ""),
        "items": news_info.get("items", []),
    }


# 注册可用工具
TOOLS: Dict[str, Tool] = {
    "weather": Tool(
        name="weather",
        description="查询指定城市的天气信息。",
        parameters={
            "city": {"type": "string", "description": "城市名称"},
            "date": {"type": "string", "description": "查询日期，默认为今天"},
        },
        handler=weather_stub,
    ),
    "news": Tool(
        name="news",
        description="获取指定主题的最新新闻。",
        parameters={
            "topic": {"type": "string", "description": "新闻主题"},
            "source": {"type": "string", "description": "新闻来源，默认为随机抽取"},
        },
        handler=news_stub,
    ),
}


# 提供工具访问接口
def get_tool(name: str) -> Optional[Tool]:
    return TOOLS.get(name)


# 列出所有可用工具
def list_tools() -> Dict[str, Tool]:
    return TOOLS
