from __future__ import annotations

from collections import deque


class MessageLog:
    def __init__(self, max_len: int = 22):
        self.messages: deque[str] = deque(maxlen=max_len)

    def __len__(self) -> int:
        return len(self.messages)

    def append(self, message: str) -> None:
        self.messages.append(message)

    def get(self, n: int = 1) -> list[str]:
        selected = []
        for i in range(max(len(self.messages) - n, 0), len(self.messages)):
            selected.append(self.messages[i])
        return selected
