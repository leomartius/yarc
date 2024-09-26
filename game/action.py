from __future__ import annotations

from game.combat import melee_attack
from game.constants import Glyph
from game.entity import Actor, ArmorItem, Item, Player, WeaponItem
from game.level import Level
from game.messages import MessageLog
from game.turn import end_turn


class Action:
    # return True if this action ends the actor's turn
    def perform(self, actor: Actor, level: Level, log: MessageLog) -> bool:
        raise NotImplementedError()


class MoveAction(Action):
    def __init__(self, dx: int, dy: int):
        self.dx, self.dy = dx, dy

    def perform(self, actor: Actor, level: Level, log: MessageLog) -> bool:
        assert level.in_bounds(actor.x + self.dx, actor.y + self.dy)
        new_x, new_y = actor.x + self.dx, actor.y + self.dy
        if not level.is_walkable(new_x, new_y):
            return False
        if not level.is_connected(actor.x, actor.y, new_x, new_y):
            return False
        actor.x, actor.y = new_x, new_y
        if isinstance(actor, Player):
            self._auto_pickup(actor, level, log)
        return True

    @staticmethod
    def _auto_pickup(actor: Player, level: Level, log: MessageLog) -> None:
        item_on_floor = level.get_item_at(actor.x, actor.y)
        if not item_on_floor:
            return
        if item_on_floor.gold:
            level.entities.remove(item_on_floor)
            actor.gold += item_on_floor.gold
            log.append(f"You find {item_on_floor.gold} gold pieces.")
        else:
            if actor.inventory.add_item(item_on_floor):
                level.entities.remove(item_on_floor)
                log.append(f"You now have {item_on_floor}.")
            else:
                log.append("There's no room in your pack.")


class MeleeAction(Action):
    def __init__(self, target: Actor):
        self.target = target

    def perform(self, actor: Actor, level: Level, log: MessageLog) -> bool:
        assert level.in_bounds(self.target.x, self.target.y)
        assert level.is_walkable(self.target.x, self.target.y)
        if not level.is_connected(actor.x, actor.y, self.target.x, self.target.y):
            return False
        melee_attack(actor, self.target, level, log)
        if self.target.ai:
            self.target.ai.attacked(self.target, level)
        return True


class BumpAction(Action):
    def __init__(self, dx: int, dy: int):
        self.dx, self.dy = dx, dy

    def perform(self, actor: Actor, level: Level, log: MessageLog) -> bool:
        action: Action
        dest_x, dest_y = actor.x + self.dx, actor.y + self.dy
        if not level.in_bounds(dest_x, dest_y):
            return False
        target = level.get_actor_at(dest_x, dest_y)
        if target:
            action = MeleeAction(target)
        else:
            action = MoveAction(self.dx, self.dy)
        return action.perform(actor, level, log)


class WaitAction(Action):
    def perform(self, actor: Actor, level: Level, log: MessageLog) -> bool:
        return True


class StairsAction(Action):
    def perform(self, actor: Actor, level: Level, log: MessageLog) -> bool:
        assert isinstance(actor, Player)
        if (actor.x, actor.y) == (level.stairs_x, level.stairs_y):
            level.completed = True
            log.append("You descend the staircase.")
        else:
            log.append("You see no way down.")
        return False


class DropAction(Action):
    def __init__(self, item: Item):
        self.item = item

    def perform(self, actor: Actor, level: Level, log: MessageLog) -> bool:
        assert isinstance(actor, Player)
        if level.get_item_at(actor.x, actor.y):
            log.append("There is something there already.")
            return False
        if self.item.cursed and actor.inventory.is_equipped(self.item):
            log.append("You can't. It appears to be cursed.")
            return False
        if self.item is actor.inventory.armor_slot:
            end_turn(actor, level, log)
            if actor.stats.hp == 0:
                return False
        actor.inventory.remove_item(self.item)
        self.item.x, self.item.y = actor.x, actor.y
        level.entities.add(self.item)
        log.append(f"You drop {self.item}.")
        return True


class ConsumeAction(Action):
    def __init__(self, item: Item):
        self.item = item

    def perform(self, actor: Actor, level: Level, log: MessageLog) -> bool:
        assert isinstance(actor, Player)
        assert self.item.consumable
        actor.inventory.remove_item(self.item)
        self.item.consumable.use(actor, level, log)
        return True


class WieldAction(Action):
    def __init__(self, item: Item):
        assert isinstance(item, WeaponItem)
        self.item = item

    def perform(self, actor: Actor, level: Level, log: MessageLog) -> bool:
        assert isinstance(actor, Player)
        if self.item == actor.inventory.weapon_slot:
            log.append("That's already in use.")
            return False
        actor.inventory.weapon_slot = self.item
        log.append(f"You are now wielding {self.item}.")
        return True


class WearAction(Action):
    def __init__(self, item: Item):
        assert isinstance(item, ArmorItem)
        self.item = item

    def perform(self, actor: Actor, level: Level, log: MessageLog) -> bool:
        assert isinstance(actor, Player)
        end_turn(actor, level, log)
        if actor.stats.hp == 0:
            return False
        actor.inventory.armor_slot = self.item
        self.item.identified = True
        log.append(f"You are now wearing {self.item}.")
        return True


class UseAction(Action):
    def __init__(self, item: Item):
        self.item = item

    def perform(self, actor: Actor, level: Level, log: MessageLog) -> bool:
        action: Action
        if self.item.glyph == Glyph.WEAPON:
            action = WieldAction(self.item)
        elif self.item.glyph == Glyph.ARMOR:
            action = WearAction(self.item)
        elif self.item.glyph == Glyph.SCROLL:
            action = ConsumeAction(self.item)
        else:
            assert self.item.glyph == Glyph.POTION
            action = ConsumeAction(self.item)
        return action.perform(actor, level, log)


class TakeOffAction(Action):
    def perform(self, actor: Actor, level: Level, log: MessageLog) -> bool:
        assert isinstance(actor, Player)
        if armor := actor.inventory.armor_slot:
            if armor.cursed:
                log.append("You can't. It appears to be cursed.")
                return False
            end_turn(actor, level, log)
            if actor.stats.hp == 0:
                return False
            actor.inventory.armor_slot = None
            log.append(f"You used to be wearing {armor}.")
            return True
        else:
            log.append("You aren't wearing any armor.")
            return False
