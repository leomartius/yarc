from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.actor_ai import ActorAI
    from game.combat import Armor, Stats, Weapon
    from game.constants import Glyph
    from game.consumable import Consumable
    from game.inventory import Inventory


@dataclass(eq=False, slots=True, kw_only=True)
class Entity:
    x: int
    y: int
    glyph: Glyph
    name: str


@dataclass(eq=False, slots=True, kw_only=True)
class Actor(Entity):
    char: str | None = None
    stats: Stats
    ai: ActorAI | None = None


@dataclass(eq=False, slots=True, kw_only=True)
class Player(Actor):
    gold: int
    inventory: Inventory
    cause_of_death: str | None = None


@dataclass(eq=False, slots=True, kw_only=True)
class Item(Entity):
    gold: int | None = None
    consumable: Consumable | None = None

    def __str__(self) -> str:
        return f"{article(self.name)} {self.name}"


@dataclass(eq=False, slots=True, kw_only=True)
class ArmorItem(Item):
    armor: Armor


@dataclass(eq=False, slots=True, kw_only=True)
class WeaponItem(Item):
    weapon: Weapon


def article(noun: str) -> str:
    return "an" if noun[0] in 'aeiou' else "a"
