"""
和风天气工具相关功能

1. 城市搜索接口
文档：https://dev.qweather.com/docs/api/geoapi/city-lookup/
入参示例：
{
    "location":"北京",
    "range":"cn"
}
响应示例：
{
    "code":"200",
    "location":[
        {
            "name":"北京",
            "id":"101010100",
            "lat":"39.90499",
            "lon":"116.40529",
            "adm2":"北京",
            "adm1":"北京市",
            "country":"中国",
            "tz":"Asia/Shanghai",
            "utcOffset":"+08:00",
            "isDst":"0",
            "type":"city",
            "rank":"10",
            "fxLink":"https://www.qweather.com/weather/beijing-101010100.html"
        }
    ],
    "refer":{
        "sources":[
            "QWeather"
        ],
        "license":[
            "QWeather Developers License"
        ]
    }
}

2. 天气实况接口
文档：https://dev.qweather.com/docs/api/weather/weather-now/
入参示例：
{
    "location":"101010100"
}
响应示例：
{
    "code":"200",
    "now":{
        "obsTime":"2024-06-10T14:00+08:00",
        "temp":"28",
        "feelsLike":"30",
        "icon":"101",
        "text":"多云",
        "wind360":"180",
        "windDir":"南风",
        "windScale":"2",
        "windSpeed":"10",
        "humidity":"60",
        "precip":"0.0",
        "pressure":"1010",
        "vis":"16",
        "cloud":"50",
        "dew":"20"
    },
    "refer":{
        "sources":[
            "QWeather"
        ],
        "license":[
            "QWeather Developers License"
        ]
    }
}
"""
import requests
from typing import Dict, Any, Optional
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

class WeathorTool:
    """和风天气工具类"""

    def __init__(self):
        self.api_key = settings.api.qweather_api_key
        self.base_url = settings.api.qweather_base_url
        logger.info("初始化和风天气工具, base_url: %s", self.base_url)

    # 定义一个统一的请求方法，可以统一处理和风天气的异常情况
    def request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """发送请求到和风天气 API"""
        url = f"{self.base_url}/{endpoint}"
        params["key"] = self.api_key
        try:
            logger.info(f"请求和风天气 API，URL：{url}，参数：{params}")

            response = requests.get(url, params=params)
            data = response.json()
            logger.info(f"和风天气 API 响应：{data}")
            if data.get("code") == "200":
                return {
                    "success": True,
                    "data": data,
                }
            else:
                return {
                    "success": False,
                    "error": f"获取信息失败: {data.get('code')} - {data.get('message')}",
                }
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "请求超时，请稍后重试"
            }
        except requests.exceptions.RequestException:
            return {
                "success": False,
                "error": "网络请求失败"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"获取信息失败: {str(e)}",
            }


    def search_city(self, location: str, location_range: str = "cn") -> Optional[Dict[str, Any]]:
        """根据城市名称搜索城市信息"""
        logger.info(f"搜索城市：{location}，范围：{location_range}")
        params = {
            "location": location,
            "range": location_range,
        }
        response = self.request("geo/v2/city/lookup", params)
        logger.info(f"城市搜索响应：{response}")
        if response["success"]:
            locations = response["data"].get("location", [])
            if locations:
                return locations[0]  # 返回第一个匹配的城市
        return None

    def get_current_weather(self, location_id: str) -> Optional[Dict[str, Any]]:
        """获取指定城市的当前天气实况"""
        logger.info(f"获取城市ID为 {location_id} 的当前天气实况")
        params = {
            "location": location_id,
        }
        response = self.request("v7/weather/now", params)
        if response["success"]:
            data = response["data"]
            if data.get("code") == "200" and data.get("now"):
                return data["now"]
        return None