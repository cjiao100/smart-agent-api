# Smart Agent API

一个基于 FastAPI 的智能多任务问答助手，实现了工具路由、会话状态管理与历史查询功能。

## 目标与范围

- 输入：用户自然语言问题，支持多轮对话与上下文追问。
- 输出：结构化的自然语言答案，并明确本次使用的工具（如天气/新闻）。
- 能力点：
  - 判断是否调用工具
  - 防止无限递归/死循环
  - 记录并读取对话状态
  - 支持 JSON 或文本输出

## 系统架构

### 1. 接口层（FastAPI）
- 负责接收请求、返回结果。
- 输入参数包含：`session_id`、`message`、`output_format`。
- 输出包含：`answer`、`tool_used`、`state`。

### 2. 对话编排层（Agent/Router）
- 负责“要不要调用工具、调用哪个工具、如何回答”。
- 两条路线：
  - 规则路由：关键词/意图判断（无 LLM 时兜底）。
  - LLM 路由：提示词输出结构化 JSON（use_tool/tool_name/tool_args）。

### 3. 工具层（Tools）
- 设计工具注册表（天气、新闻等）。
- 工具接口统一：输入参数 → 返回结构化结果。
- 初期可用 stub 数据，后续替换为真实 API。

### 4. 会话状态层（State）
- 会话信息按 `session_id` 存储，包含历史消息、上次工具结果。
- 支持 Redis（生产）或内存（本地开发）。

### 5. 安全与限制
- 工具调用次数限制（`MAX_TOOL_CALLS`），避免无限递归。
- 对工具结果进行检查，失败时 fallback。

## 目录结构

```
smart-agent-api/
  agents/
    route.py
  api/
    main.py
  config/
    settings.py
  schemas/
    chat.py
  state/
    store.py
  tools/
    registry.py
  utils/
    logger.py
  main.py
  requirements.txt
  .gitignore
```

## 运行方式

```bash
python main.py
```

## 接口说明

### POST /chat
请求体示例：
```json
{
  "session_id": "demo-1",
  "message": "北京天气怎么样",
  "output_format": "text"
}
```

返回示例（字段结构固定）：
```json
{
  "session_id": "demo-1",
  "answer": "北京的天气是25°C，晴朗。",
  "tool_used": {"tool_name": "weather", "parameters": {"city": "北京"}},
  "state": {"messages": [], "last_tool": {}, "tool_calls": 1}
}
```

### GET /history/{session_id}
返回示例：
```json
{
  "session_id": "demo-1",
  "messages": [
    {"role": "user", "content": "科技新闻"},
    {"role": "assistant", "content": "最新的科技新闻：..."}
  ]
}
```

## 实现步骤（建议顺序）

1. 需求拆解与字段定义
   - 明确请求/响应结构。
   - 定义最小可用字段（session_id/message/output_format）。

2. 设计工程结构
   - 目录建议：
     - api/main.py（FastAPI 入口）
     - agents/route.py（路由与回答）
     - tools/registry.py（工具注册与实现）
     - state/store.py（状态存储）
     - schemas/chat.py（请求/响应模型）

3. 实现状态存储
   - 先做内存存储（dict + TTL）。
   - 再接 Redis（URL 读取 + setex）。

4. 工具层实现
   - 建立工具注册表（name/description/parameters/handler）。
   - 先用固定数据 stub，保证流程可跑。

5. 路由逻辑
   - 规则路由：关键词判定 weather/news。
   - LLM 路由：提示词输出 JSON，解析失败时 fallback 到规则。

6. 生成回答
   - 若调用工具：将工具结果转为自然语言回答。
   - 未调用工具：LLM 直答或提示“可回答天气/新闻”。

7. 上下文追问
   - 保存上次工具结果到 session。
   - 当用户问“那条新闻是谁发布的”时从 state 取回。

8. 接口串联
   - FastAPI 接口调用 agent。
   - 返回结构化响应。

9. 本地验证
   - 用 curl/HTTP 客户端测试：
     - 天气问答
     - 新闻问答
     - 追问上下文
     - 工具调用上限

10. 可选扩展
    - 接入真实 API、增加工具类型。
    - 加入日志追踪与监控。
    - Docker 化部署。

## 风险点与注意事项

- LLM 输出 JSON 可能不稳定，要有解析失败兜底。
- 工具调用需设置上限，避免自循环。
- 会话存储要有过期机制，防止内存膨胀。

---

如果你希望我进一步细化某一步的实现逻辑（例如路由提示词、状态结构设计、API 定义），告诉我具体要哪一部分，我只提供思路，不落地代码。
