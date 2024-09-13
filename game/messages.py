from __future__ import annotations

from collections import deque


class MessageLog:
    def __init__(self, max_size: int = 25):
        self._messages: deque[str] = deque(maxlen=max_size)
        self._unread = 0

    def append(self, message: str) -> None:
        self._messages.append(message)
        self._unread = min(self._unread + 1, len(self._messages))

    def get_latest(self, n: int) -> list[str]:
        return list(self._messages)[-n:]

    @property
    def unread(self) -> int:
        return self._unread

    def get_unread(self, n: int) -> list[str]:
        if self._unread == 0:
            return []
        unread_messages = list(self._messages)[-self._unread :]
        self._unread = max(self._unread - n, 0)
        return unread_messages[:n]
