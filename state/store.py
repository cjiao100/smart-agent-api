import json
import time
from typing import Any, Dict, Optional, cast

try:
    import redis
except Exception:
    redis = None


class InMemoryStore:
    def __init__(self) -> None:
        self._store: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Dict[str, Any]:
        value = self._store.get(key, {})
        return value

    def set(self, key: str, value: Dict[str, Any], ttl_seconds: int) -> None:
        # 复制一份，避免外部引用同一 dict 导致副作用
        value = dict(value)
        # 记录过期时间戳，便于后续清理
        value["_expires_at"] = int(time.time()) + ttl_seconds
        self._store[key] = value


class RedisStore:
    def __init__(self, redis_url: str) -> None:
        if not redis:
            raise RuntimeError("redis not installed")
        self._client = redis.Redis.from_url(redis_url, decode_responses=True)

    def get(self, key: str) -> Dict[str, Any]:
        # redis.get 返回类型标注不稳定，这里做类型断言
        raw = cast(Optional[str], self._client.get(key))
        if not raw:
            return {}
        return json.loads(raw)

    def set(self, key: str, value: Dict[str, Any], ttl_seconds: int) -> None:
        # 统一序列化存储为 JSON 字符串
        raw = json.dumps(value)
        self._client.setex(key, ttl_seconds, raw)


class StateStore:
    def __init__(self, redis_url: str = "", ttl_seconds: int = 3600) -> None:
        self.ttl_seconds = ttl_seconds
        if redis_url:
            try:
                self._store = RedisStore(redis_url)
            except Exception:
                # Redis 连接失败时回退到内存存储
                self._store = InMemoryStore()
        else:
            self._store = InMemoryStore()

    def get_state(self, session_id: str) -> Dict[str, Any]:
        return self._store.get(session_id)

    def set_state(self, session_id: str, state: Dict[str, Any]) -> None:
        # 复制后更新，避免外部继续修改同一份状态
        state = dict(state)
        state["updated_at"] = int(time.time())
        self._store.set(session_id, state, self.ttl_seconds)
