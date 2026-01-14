from langchain.tools import tool
from schemas.tool import WeatherInput, WeatherOutput, NewsInput, NewsOutput
from tools.registry import weather_stub, news_stub

@tool("weather", args_schema=WeatherInput, description="查询指定城市的天气信息。")
def weather_tool(city: str, date: str = "今天") -> dict:
    """查询指定城市的天气信息"""
    weather_info = weather_stub(city, date)
    if not weather_info or "error" in weather_info:
        return {"error": weather_info.get("error", "无法获取天气信息")}
    return WeatherOutput(
        city=city,
        date=date,
        temperature=weather_info["temperature"],
        condition=weather_info["condition"],
    ).model_dump()

@tool("news", args_schema=NewsInput, description="获取指定主题的最新新闻。")
def news_tool(topic: str, source: str = "") -> dict:
    """获取指定主题的最新新闻"""
    news_info = news_stub(topic, source)
    if not news_info or "error" in news_info:
        return {"error": news_info.get("error", "无法获取相关新闻")}
    return NewsOutput(
        topic=topic,
        source=news_info.get("source", ""),
        items=news_info.get("items", []),
    ).model_dump()

