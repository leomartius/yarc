from __future__ import annotations

import random
from dataclasses import dataclass

from game.combat import save_vs_magic, save_vs_poison
from game.dice import percent, roll
from game.entity import Actor, Player, is_magic
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


@dataclass(frozen=True, slots=True)
class Corrode(Attack):
    def apply(self, actor: Actor, target: Actor, level: Level, log: MessageLog) -> None:
        assert isinstance(target, Player)
        worn_armor = target.inventory.armor_slot
        if worn_armor and worn_armor.armor.ac < 9 and worn_armor.armor.base_ac < 8:
            worn_armor.armor.plus_ac -= 1
            log.append("Your armor appears to be weaker now. Oh, my!")


@dataclass(frozen=True, slots=True)
class StealItem(Attack):
    def apply(self, actor: Actor, target: Actor, level: Level, log: MessageLog) -> None:
        assert isinstance(target, Player)
        items = [item for item in target.inventory.items if not target.inventory.is_equipped(item) and is_magic(item)]
        if items:
            item = random.choice(items)
            target.inventory.remove_item(item)
            log.append(f"She stole {item}!")
            level.entities.remove(actor)


@dataclass(frozen=True, slots=True)
class DrainHealth(Attack):
    def apply(self, actor: Actor, target: Actor, level: Level, log: MessageLog) -> None:
        if percent(30):
            hp_drain = roll(1, d=5)
            _do_drain(hp_drain, actor, target, log)


@dataclass(frozen=True, slots=True)
class DrainLevel(Attack):
    def apply(self, actor: Actor, target: Actor, level: Level, log: MessageLog) -> None:
        if percent(15):
            if target.stats.xp == 0:
                target.stats.max_hp = 0
            elif target.stats.hd == 1:
                target.stats.xp = 0
            elif target.stats.hd == 2:
                target.stats.hd = 1
                target.stats.xp = 1
            else:
                target.stats.hd -= 1
                target.stats.xp = 2 ** (target.stats.hd - 2) * 10 + 1
            hp_drain = roll(1, d=10)
            _do_drain(hp_drain, actor, target, log)


def _do_drain(hp_drain: int, actor: Actor, target: Actor, log: MessageLog) -> None:
    assert isinstance(target, Player)
    target.stats.max_hp -= hp_drain
    target.stats.hp -= hp_drain
    if target.stats.max_hp < 1:
        target.stats.max_hp = 0
        target.stats.hp = 0
        target.cause_of_death = actor.name
    elif target.stats.hp < 1:
        target.stats.hp = 1
    log.append("You suddenly feel weaker.")
