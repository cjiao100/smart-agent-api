from fastapi import FastAPI
from typing import Dict, Any
from state.store import StateStore
from agents.route import handle_message
from schemas.chat import ChatResponse, ChatRequest, HistoryResponse
from utils.logger import get_logger

state_store = StateStore()
logger = get_logger(__name__)

app = FastAPI(
    title="AI 助手 API",
    description="这是一个基于 FastAPI 的 AI 助手服务，支持聊天和工具调用。",
    version="1.0.0",
)

@app.get("/")
async def read_root():
    logger.info("健康检查请求")
    return {"Hello": "World"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    logger.info("收到聊天请求")
    session_id = request.session_id
    message = request.message
    output_format = request.output_format or "text"
    response = handle_message(session_id, message, output_format, state_store)
    return response

@app.get("/history/{session_id}", response_model=HistoryResponse)
async def get_history(session_id: str) -> HistoryResponse:
    logger.info("收到历史记录请求")
    state = state_store.get_state(session_id)
    messages = state.get("messages", [])
    return HistoryResponse(session_id=session_id, messages=messages)
