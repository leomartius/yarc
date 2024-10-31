from __future__ import annotations

from dataclasses import dataclass

from game.combat import save_vs_magic, save_vs_poison
from game.dice import roll
from game.entity import Actor, Player
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


@dataclass(frozen=True, slots=True)
class StealGold(Attack):
    def apply(self, actor: Actor, target: Actor, level: Level, log: MessageLog) -> None:
        assert isinstance(target, Player)
        if target.gold > 0:
            multiplier = 1 if save_vs_magic(target) else 5
            stolen_gold = roll(multiplier, 50 + 10 * level.depth) + multiplier
            target.gold = max(0, target.gold - stolen_gold)
            log.append("Your purse feels lighter.")
        level.entities.remove(actor)
