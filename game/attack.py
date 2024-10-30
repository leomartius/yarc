from __future__ import annotations

from dataclasses import dataclass

from game.combat import save_vs_poison
from game.entity import Actor
from game.level import Level
from game.messages import MessageLog


class Attack:
    def apply(self, actor: Actor, target: Actor, level: Level, log: MessageLog) -> None:
        raise NotImplementedError()


@dataclass(frozen=True, slots=True)
class Poison(Attack):
    def apply(self, actor: Actor, target: Actor, level: Level, log: MessageLog) -> None:
        if not save_vs_poison(target):
            target.stats.strength = max(3, target.stats.strength - 1)
            log.append("You feel a sting in your arm and now feel weaker.")
