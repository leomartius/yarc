from __future__ import annotations

from game.entity import Actor
from game.level import Level
from game.messages import MessageLog


class Attack:
    def apply(self, actor: Actor, target: Actor, level: Level, log: MessageLog) -> None:
        raise NotImplementedError()
