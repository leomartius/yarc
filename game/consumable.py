from __future__ import annotations

from dataclasses import dataclass

from game.actor_ai import IdleAI
from game.combat import level_up
from game.dice import percent, roll
from game.entity import Actor, Player
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
        targets_in_area = {
            target
            for target in level.actors
            if target != actor and actor.x - 2 <= target.x <= actor.x + 2 and actor.y - 2 <= target.y <= actor.y + 2
        }
        for target in targets_in_area:
            target.ai = IdleAI()
        match len(targets_in_area):
            case 0:
                log.append("You feel a strange sense of loss.")
            case 1:
                log.append("The monster freezes.")
            case _:
                log.append("The monsters around you freeze.")


@dataclass(frozen=True, slots=True)
class EnchantArmor(Consumable):
    def use(self, actor: Actor, level: Level, log: MessageLog) -> None:
        assert isinstance(actor, Player)
        if armor := actor.inventory.armor_slot:
            armor.armor.plus_ac += 1
            armor.cursed = False
            log.append("Your armor glows faintly for a moment.")
        else:
            log.append("You feel a strange sense of loss.")


@dataclass(frozen=True, slots=True)
class EnchantWeapon(Consumable):
    def use(self, actor: Actor, level: Level, log: MessageLog) -> None:
        assert isinstance(actor, Player)
        if weapon := actor.inventory.weapon_slot:
            if percent(50):
                weapon.weapon.plus_hit += 1
            else:
                weapon.weapon.plus_dmg += 1
            weapon.cursed = False
            log.append(f"Your {weapon.name} glows blue for a moment.")
        else:
            log.append("You feel a strange sense of loss.")
