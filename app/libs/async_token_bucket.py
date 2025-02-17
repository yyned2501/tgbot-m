import asyncio
import time
from asyncio import Lock


class AsyncTokenBucket:
    def __init__(self, capacity: int, fill_rate: float):
        """
        异步令牌桶初始化
        :param capacity: 桶的最大容量
        :param fill_rate: 每秒填充的令牌数量（需>0）
        """
        assert fill_rate > 0, "Fill rate must be greater than 0"

        self.capacity = float(capacity)
        self._tokens = float(capacity)
        self.fill_rate = fill_rate
        self.last_time = time.monotonic()  # 使用物理时间计算
        self.lock = Lock()

    def _add_tokens(self):
        """令牌填充逻辑"""
        now = time.monotonic()
        elapsed = now - self.last_time
        new_tokens = elapsed * self.fill_rate

        if new_tokens > 0:
            self._tokens = min(self.capacity, self._tokens + new_tokens)
            self.last_time = now

    async def consume(self, tokens=1):
        """
        消费令牌（协程方法）
        当令牌不足时会自动等待直到足够
        """
        while True:
            async with self.lock:
                self._add_tokens()

                # 如果令牌足够则直接消费
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return

                # 计算需要等待的时间
                deficit = tokens - self._tokens
                required_time = deficit / self.fill_rate

            # 异步等待所需时间（期间释放锁允许其他操作）
            await asyncio.sleep(required_time)
