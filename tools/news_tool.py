"""
天行数据新闻工具相关功能

1. 综合新闻数据
文档：https://www.tianapi.com/apiview/87
入参示例：
{
    "key": "API密钥",
    "num": 10,
    "page": 0,
    "rand": 0, // 是否随机返回数据，0-否，1-是
    "word": "关键词"
    "source": "网易明星" // 指定来源，可选
}

响应示例：
{
  "msg": "success",
  "code": 200,
  "result": {
    "newslist": [
      {
        "id": "92e5f080884dce68cbf751378a779e90",
        "url": "http://k.sina.com.cn/article_7452972885_1bc3b575500100uc40.html",
        "ctime": "2021-02-04 19:22",
        "title": "河北三河国家农业科技园区建设农业联合体科技示范基地授牌仪式",
        "picUrl": "http://n.sinaimg.cn/sinakd202124s/161/w550h411/20210204/fce0-kirmait9302150.jpg",
        "source": "农业新闻",
        "description": "河北三河国家农业科技园区举行建设三河市香丰肥业农业联合体科技示范基地授牌仪式2月4日上午，河北三河国家农业科技园区建设三河市香丰肥业农业联合体科技示范基地授..."
      },
      {
        "id": "f732f5db5bc872794e693e2f038b35e4",
        "url": "http://finance.sina.com.cn/stock/relnews/dongmiqa/2021-02-04/doc-ikftpnny4511586.shtml",
        "ctime": "2021-02-04 00:00",
        "title": "投资者提问：2021年2月3日各大媒体报道了益海嘉里金龙鱼农业订单模式让...",
        "picUrl": "http://n.sinaimg.cn/sinakd202124s/162/w550h412/20210204/6706-kirmait9301473.jpg",
        "source": "农业新闻",
        "description": "投资者提问：2021年2月3日各大媒体报道了益海嘉里金龙鱼农业订单模式让农户腰包鼓了日子富了。农民交粮给金龙鱼，粮款24小时到账，比卖给粮食中介还增收了很..."
      },
      {
        "id": "62ac899e8fcf654a74479b4239b4651f",
        "url": "http://finance.sina.com.cn/7x24/2021-02-04/doc-ikftpnny4511923.shtml",
        "ctime": "2021-02-04 00:00",
        "title": "近日，国务院正式批复设立陕西杨凌综合保税区，全国唯一农业特色的综合保税区正...",
        "picUrl": "http://n.sinaimg.cn/sinakd20210204ac/182/w640h342/20210204/991d-kirmait9407892.jpg",
        "source": "农业新闻",
        "description": "近日，国务院正式批复设立陕西杨凌综合保税区，全国唯一农业特色的综合保税区正式落户杨凌。"
      }
    ],
    "allnum": 3690,
    "curpage": 1
  }
}

"""

import requests
from typing import Dict, Any, Optional
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

class NewsTool:
    """天行数据新闻工具类"""

    def __init__(self) -> None:
        self.api_key = settings.api.tian_api_key
        self.base_url = settings.api.tian_api_base_url
        logger.info(f"初始化天行数据新闻工具, base_url: {self.base_url}")

    def request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """发送请求到天行数据新闻 API"""
        url = f"{self.base_url}/{endpoint}"
        params["key"] = self.api_key

        try:
            logger.info(f"请求天行数据新闻 API，URL：{url}，参数：{params}")

            response = requests.get(url, params=params)
            data = response.json()
            logger.info(f"天行数据新闻 API 响应：{data}")
            if data.get("code") == 200:
                return {
                    "success": True,
                    "data": data,
                }
            else:
                return {
                    "success": False,
                    "error": f"获取信息失败: {data.get('code')} - {data.get('msg')}",
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

    def get_news(self, topic: str, source: str = "", num: int = 5, page: int = 1, rand: int = 0) -> Optional[Dict[str, Any]]:
        """获取新闻信息"""
        params = {
            "word": topic,
            "source": source,
            "num": num,
            "page": page,
            "rand": rand,
        }
        response = self.request("generalnews/index", params)
        logger.info(f"获取新闻信息响应：{response}")
        if response["success"]:
            data = response["data"]
            news_list = data.get("result", {}).get("newslist", [])
            return {
                "topic": topic,
                "source": source,
                "items": news_list,
            }

        return None