import os
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator, ValidationInfo

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# API Keys and Base URLs
QWEATHER_API_KEY = os.getenv("QWEATHER_API_KEY", "")
QWEATHER_BASE_URL = os.getenv("QWEATHER_BASE_URL", "")

class APISettings(BaseSettings):
    """第三方 API 配置"""

    # 和风天气 API 配置
    qweather_api_key: str = Field(default_factory=lambda: os.getenv("QWEATHER_API_KEY", ""), description="和风天气 API Key")
    qweather_base_url: str = Field(default_factory=lambda: os.getenv("QWEATHER_BASE_URL", ""), description="和风天气 API 基础 URL")

    # 天行数据 API 配置
    tian_api_key: str = Field(default_factory=lambda: os.getenv("TIAN_API_KEY", ""), description="天行数据 API Key")
    tian_api_base_url: str = Field(default_factory=lambda: os.getenv("TIAN_API_BASE_URL", "https://api.tianapi.com"), description="天行数据 API 基础 URL")

    # OpenRouter API 配置
    openrouter_api_key: str = Field(default_factory=lambda: os.getenv("OPENROUTER_API_KEY", ""), description="OpenRouter API Key")
    openrouter_base_url: str = Field(default_factory=lambda: os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"), description="OpenRouter API 基础 URL")

    @field_validator("qweather_api_key", "qweather_base_url", "tian_api_key", "tian_api_base_url", "openrouter_api_key", "openrouter_base_url")
    @classmethod
    def validate_not_empty(cls, v: str, info: ValidationInfo) -> str:
        if not v:
            raise ValueError(f"字段 {info.field_name} 不能为空")
        return v.strip()

    class Config:
        env_prefix = ""
        case_sensitive = False

class AppSettings(BaseSettings):
    """应用程序配置"""

    app_name: str = Field(default="MultiTaskQAAssistant", description="应用名称")
    app_version: str = Field(default="1.0.0", description="应用版本")
    log_level: str = Field(default="INFO", description="日志级别")
    max_conversation_history: int = Field(default=50, description="最大对话历史记录数")
    cache_ttl: int = Field(default=3600, description="缓存过期时间(秒)")

    @field_validator('log_level')
    def validate_log_level(cls, v):
        """验证日志级别"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"日志级别必须是以下之一: {valid_levels}")
        return v.upper()

    @field_validator('max_conversation_history', 'cache_ttl')
    def validate_positive_int(cls, v):
        """验证正整数"""
        if v <= 0:
            raise ValueError("值必须大于0")
        return v

    class Config:
        env_prefix = ""
        case_sensitive = False


class Settings:
    """
    全局配置管理器

    采用单例模式，确保配置的一致性和性能
    提供统一的配置访问接口
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            try:
                self.api = APISettings()
                self.app = AppSettings()
                self._initialized = True
            except Exception as e:
                raise RuntimeError(f"配置初始化失败: {str(e)}")

    def validate_all(self) -> bool:
        """验证所有配置"""
        try:
            # 检查必需的API密钥
            if not self.api.qweather_api_key:
                print("❌ 和风天气 API密钥未配置")
                return False

            if not self.api.tian_api_key:
                print("❌ 天行数据 API密钥未配置")
                return False

            if not self.api.openrouter_api_key:
                print("❌ OpenRouter API密钥未配置")
                return False

            print("✅ 配置验证通过")
            return True

        except Exception as e:
            print(f"❌ 配置验证失败: {str(e)}")
            return False


# 全局配置实例
settings = Settings()