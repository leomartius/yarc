from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass

from game.combat import Armor, Weapon
from game.constants import Glyph
from game.consumable import (
    AggravateMonsters,
    Consumable,
    EnchantArmor,
    EnchantWeapon,
    Food,
    GainStrength,
    Healing,
    HoldMonster,
    Identify,
    MagicMapping,
    NoEffect,
    Poison,
    RaiseLevel,
    RemoveCurse,
    RestoreStrength,
)
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
    ItemType(
        5, Glyph.POTION, "potion of extra healing", Healing(die=8, extra=True, message="You begin to feel much better.")
    ),
    ItemType(2, Glyph.POTION, "potion of raise level", RaiseLevel()),
    ItemType(8, Glyph.POTION, "potion of poison", Poison()),
    ItemType(15, Glyph.POTION, "potion of gain strength", GainStrength()),
    ItemType(14, Glyph.POTION, "potion of restore strength", RestoreStrength()),
]

scroll_types = [
    ItemType(1, Glyph.SCROLL, "scroll of blank paper", NoEffect(message="This scroll seems to be blank.")),
    ItemType(3, Glyph.SCROLL, "scroll of hold monster", HoldMonster()),
    ItemType(8, Glyph.SCROLL, "scroll of enchant armor", EnchantArmor()),
    ItemType(10, Glyph.SCROLL, "scroll of enchant weapon", EnchantWeapon()),
    ItemType(8, Glyph.SCROLL, "scroll of remove curse", RemoveCurse()),
    ItemType(4, Glyph.SCROLL, "scroll of aggravate monsters", AggravateMonsters()),
    ItemType(5, Glyph.SCROLL, "scroll of magic mapping", MagicMapping()),
    ItemType(27, Glyph.SCROLL, "scroll of identify", Identify()),
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

food_types = [
    ItemType(9, Glyph.FOOD, "ration of food", Food(spoilable=True)),
    ItemType(1, Glyph.FOOD, "slime mold", Food(spoilable=False)),
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
    ItemCategory(30, scroll_types),
    ItemCategory(8, armor_types),
    ItemCategory(8, weapon_types),
    ItemCategory(17, food_types),
]


def get_item_categories() -> tuple[list[ItemCategory], list[int]]:
    weights = [category.weight for category in item_categories]
    return item_categories[:], weights
