from __future__ import annotations

from dataclasses import dataclass

from game.actor_ai import IdleAI
from game.combat import level_up
from game.dice import roll
from game.entity import Actor
from game.level import Level
from game.messages import MessageLog


class Consumable:
    def use(self, actor: Actor, level: Level, log: MessageLog) -> None:
        raise NotImplementedError()


@dataclass(frozen=True, slots=True)
class NoEffect(Consumable):
    message: str

    def use(self, actor: Actor, level: Level, log: MessageLog) -> None:
        log.append(self.message)


@dataclass(frozen=True, slots=True, kw_only=True)
class Healing(Consumable):
    die: int
    extra: bool = False
    message: str

    def use(self, actor: Actor, level: Level, log: MessageLog) -> None:
        heal = roll(actor.stats.hd, self.die)
        actor.stats.hp += heal
        if actor.stats.hp > actor.stats.max_hp:
            if self.extra and actor.stats.hp > actor.stats.max_hp + actor.stats.hd + 1:
                actor.stats.max_hp += 1
            actor.stats.max_hp += 1
            actor.stats.hp = actor.stats.max_hp
        log.append(self.message)


@dataclass(frozen=True, slots=True)
class RaiseLevel(Consumable):
    def use(self, actor: Actor, level: Level, log: MessageLog) -> None:
        actor.stats.xp = 5 * 2**actor.stats.hd + 1
        log.append("You suddenly feel much more skillful.")
        level_up(actor, log)


@dataclass(frozen=True, slots=True)
class HoldMonster(Consumable):
    def use(self, actor: Actor, level: Level, log: MessageLog) -> None:
        targets_in_area = {target for target in level.actors
                           if actor.x - 2 <= target.x <= actor.x + 2 and actor.y - 2 <= target.y <= actor.y + 2}
        for target in targets_in_area:
            if target != actor:
                target.ai = IdleAI()
