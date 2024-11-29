from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

import numpy as np

from game.actor_ai import aggravate, pacify
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
class Poison(Consumable):
    def use(self, actor: Actor, level: Level, log: MessageLog) -> None:
        strength_damage = roll(1, d=3)
        actor.stats.strength = max(3, actor.stats.strength - strength_damage)
        log.append("You feel very sick now.")


@dataclass(frozen=True, slots=True)
class GainStrength(Consumable):
    def use(self, actor: Actor, level: Level, log: MessageLog) -> None:
        actor.stats.strength = min(31, actor.stats.strength + 1)
        if actor.stats.strength >= actor.stats.max_strength:
            actor.stats.max_strength = actor.stats.strength
        log.append("You feel stronger now. What bulging muscles!")


@dataclass(frozen=True, slots=True)
class RestoreStrength(Consumable):
    def use(self, actor: Actor, level: Level, log: MessageLog) -> None:
        if actor.stats.strength < actor.stats.max_strength:
            actor.stats.strength = actor.stats.max_strength
        log.append("Hey, this tastes great. It makes you feel warm all over.")


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
            pacify(target)
        match len(targets_in_area):
            case 0:
                log.append("You feel a strange sense of loss.")
            case 1:
                log.append("The monster freezes.")
            case _:
                log.append("The monsters around you freeze.")


@dataclass(frozen=True, slots=True)
class AggravateMonsters(Consumable):
    def use(self, actor: Actor, level: Level, log: MessageLog) -> None:
        for target in level.actors:
            if target != actor:
                aggravate(target)
        log.append("You hear a high-pitched humming noise.")


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


@dataclass(frozen=True, slots=True)
class RemoveCurse(Consumable):
    def use(self, actor: Actor, level: Level, log: MessageLog) -> None:
        assert isinstance(actor, Player)
        if armor := actor.inventory.armor_slot:
            armor.cursed = False
        if weapon := actor.inventory.weapon_slot:
            weapon.cursed = False
        log.append("You feel as if somebody is watching over you.")


@dataclass(frozen=True, slots=True)
class MagicMapping(Consumable):
    revealed: ClassVar = np.array(
        [
            False,  # rock
            True,  # top left corner
            True,  # top right corner
            True,  # bottom left corner
            True,  # bottom right corner
            True,  # horizontal wall
            True,  # vertical wall
            False,  # floor
            True,  # passage
            True,  # stairs
            True,  # trap
            True,  # door
        ],
        dtype=bool,
    )

    def use(self, actor: Actor, level: Level, log: MessageLog) -> None:
        level.explored[:] |= MagicMapping.revealed[level.tiles]
        log.append("Oh, now this scroll has a map on it.")


@dataclass(frozen=True, slots=True)
class Identify(Consumable):
    def use(self, actor: Actor, level: Level, log: MessageLog) -> None:
        # This consumable is special-cased in UseAction. The actual logic is in IdentifyAction.
        log.append("This is an identify scroll.")


@dataclass(frozen=True, slots=True, kw_only=True)
class Food(Consumable):
    spoilable: bool

    def use(self, actor: Actor, level: Level, log: MessageLog) -> None:
        assert isinstance(actor, Player)
        actor.hunger_clock = max(actor.hunger_clock, 0)
        actor.hunger_clock += 1099 + roll(1, d=400)
        actor.hunger_clock = min(actor.hunger_clock, 2000)
        if self.spoilable:
            if percent(70):
                log.append("Yum, that tasted good.")
            else:
                actor.stats.xp += 1
                log.append("Yuk, this food tastes awful.")
                level_up(actor, log)
        else:
            log.append("My, that was a yummy slime mold.")
