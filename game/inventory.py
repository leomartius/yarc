from __future__ import annotations

from game.entity import ArmorItem, Item, WeaponItem


class Inventory:
    def __init__(self, max_items: int = 22):
        self.items: list[Item] = []
        self.max_items = max_items
        self._armor: ArmorItem | None = None
        self._weapon: WeaponItem | None = None

    @property
    def armor_slot(self) -> ArmorItem | None:
        assert (self._armor is None) or (self._armor in self.items)
        return self._armor

    @armor_slot.setter
    def armor_slot(self, item: ArmorItem | None) -> None:
        assert (item is None) or (item in self.items)
        self._armor = item

    @property
    def weapon_slot(self) -> WeaponItem | None:
        assert (self._weapon is None) or (self._weapon in self.items)
        return self._weapon

    @weapon_slot.setter
    def weapon_slot(self, item: WeaponItem | None) -> None:
        assert (item is None) or (item in self.items)
        self._weapon = item

    def add_item(self, item: Item) -> bool:
        if len(self.items) >= self.max_items:
            return False
        self.items.append(item)
        return True

    def remove_item(self, item: Item) -> None:
        assert item in self.items
        if item is self.armor_slot:
            self.armor_slot = None
        if item is self.weapon_slot:
            self.weapon_slot = None
        self.items.remove(item)
