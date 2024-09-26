from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass

from game.combat import Armor, Weapon
from game.constants import Glyph
from game.consumable import Consumable, Healing, HoldMonster, NoEffect
from game.entity import ArmorItem, Item, WeaponItem


@dataclass(frozen=True, slots=True)
class ItemType:
    weight: int
    glyph: Glyph
    name: str
    component: Armor | Consumable | Weapon

    def spawn(self, x: int, y: int) -> Item:
        component = deepcopy(self.component)
        if isinstance(component, Armor):
            return ArmorItem(x=x, y=y, glyph=self.glyph, name=self.name, armor=component)
        elif isinstance(component, Weapon):
            return WeaponItem(x=x, y=y, glyph=self.glyph, name=self.name, weapon=component)
        else:
            return Item(x=x, y=y, glyph=self.glyph, name=self.name, consumable=component)


potion_types = [
    ItemType(1, Glyph.POTION, "potion of thirst quenching", NoEffect(message="This potion tastes extremely dull.")),
    ItemType(15, Glyph.POTION, "potion of healing", Healing(die=4, message="You begin to feel better.")),
    ItemType(5, Glyph.POTION, "potion of extra healing", Healing(die=8, message="You begin to feel much better.")),
]

scroll_types = [
    ItemType(1, Glyph.SCROLL, "scroll of blank paper", NoEffect(message="This scroll seems to be blank.")),
    ItemType(2, Glyph.SCROLL, "scroll of hold monster", HoldMonster()),
]

armor_types = [
    ItemType(20, Glyph.ARMOR, "leather armor", Armor(base_ac=8)),
    ItemType(15, Glyph.ARMOR, "ring mail", Armor(base_ac=7)),
    ItemType(15, Glyph.ARMOR, "studded leather armor", Armor(base_ac=7)),
    ItemType(13, Glyph.ARMOR, "scale mail", Armor(base_ac=6)),
    ItemType(12, Glyph.ARMOR, "chain mail", Armor(base_ac=5)),
    ItemType(10, Glyph.ARMOR, "splint mail", Armor(base_ac=4)),
    ItemType(10, Glyph.ARMOR, "banded mail", Armor(base_ac=4)),
    ItemType(5, Glyph.ARMOR, "plate mail", Armor(base_ac=3)),
]

weapon_types = [
    ItemType(1, Glyph.WEAPON, "mace", Weapon(dmg_dice='2d4')),
    ItemType(1, Glyph.WEAPON, "longsword", Weapon(dmg_dice='3d4')),
    ItemType(1, Glyph.WEAPON, "dagger", Weapon(dmg_dice='1d6')),
    ItemType(1, Glyph.WEAPON, "two-handed sword", Weapon(dmg_dice='4d4')),
    ItemType(1, Glyph.WEAPON, "spear", Weapon(dmg_dice='2d3')),
]


@dataclass(frozen=True, slots=True)
class ItemCategory:
    weight: int
    item_types: list[ItemType]

    def get_item_types(self) -> tuple[list[ItemType], list[int]]:
        weights = [item_type.weight for item_type in self.item_types]
        return self.item_types[:], weights


item_categories = [
    ItemCategory(27, potion_types),
    ItemCategory(27, scroll_types),
    ItemCategory(8, armor_types),
    ItemCategory(8, weapon_types),
]


def get_item_categories() -> tuple[list[ItemCategory], list[int]]:
    weights = [category.weight for category in item_categories]
    return item_categories[:], weights
