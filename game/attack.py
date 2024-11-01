from __future__ import annotations

import random
from dataclasses import dataclass

from game.combat import save_vs_magic, save_vs_poison
from game.dice import roll
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
