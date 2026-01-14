from pydantic import BaseModel, Field

# 定义天气工具输入输出的 Schema
class WeatherInput(BaseModel):
    city: str = Field(..., description="城市名称")
    date: str = Field(default="今天", description="查询日期，默认为今天")

class WeatherOutput(BaseModel):
    city: str = Field(..., description="城市名称")
    date: str = Field(..., description="查询日期")
    temperature: str = Field(..., description="温度信息")
    condition: str = Field(..., description="天气状况")

# 定义新闻工具输入输出的 Schema
class NewsInput(BaseModel):
    topic: str = Field(..., description="新闻主题")
    source: str = Field(default="", description="新闻来源，默认为随机抽取")

class NewsOutput(BaseModel):
    topic: str = Field(..., description="新闻主题")
    source: str = Field(..., description="新闻来源")
    items: list[dict] = Field(..., description="新闻列表，每条新闻包含标题、来源和日期等信息")
