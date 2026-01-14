from typing import Any, Dict, Literal, Optional
from pydantic import BaseModel, Field

# 定义工具调用的Pydantic模型
class ToolCall(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]

# 定义聊天请求的Pydantic模型
class ChatRequest(BaseModel):
    session_id: str
    message: str
    output_format: Literal["text", "json"] = Field(default="text", description="指定输出格式，可以是'text'或'json'.")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="附加的元数据，用于提供上下文信息.")

# 定义聊天响应的Pydantic模型
class ChatResponse(BaseModel):
    session_id: str
    answer: str
    tool_used: Optional[ToolCall] = Field(default=None, description="如果使用了工具，返回工具的名称和参数.")
    state: Dict[str, Any] = Field(default_factory=dict, description="会话的当前状态信息.")

# 定义历史记录响应的Pydantic模型
class HistoryResponse(BaseModel):
    session_id: str
    messages: list[Dict[str, Any]]

