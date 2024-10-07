from __future__ import annotations

from dataclasses import InitVar, dataclass, field

from game.dice import parse_dice, roll
from game.entity import Actor, Player
from game.level import Level
from game.messages import MessageLog


@dataclass(slots=True)
class Stats:
    # current hit points
    hp: int = field(init=False)
    # maximum hit points
    max_hp: int
    # (natural) armor class
    ac: int
    # hit dice (character level)
    hd: int
    # damage die (unarmed strike)
    dmg: int
    # xp value (current experience)
    xp: int
    # strength
    strength: int = 10

    def __post_init__(self) -> None:
        self.hp = self.max_hp


@dataclass(eq=False, slots=True, kw_only=True)
class Armor:
    # base armor class
    base_ac: int
    # armor class bonus
    plus_ac: int = 0

    @property
    def ac(self) -> int:
        return self.base_ac - self.plus_ac


@dataclass(eq=False, slots=True, kw_only=True)
class Weapon:
    # weapon damage dice
    base_dmg: tuple[int, int] = field(init=False)
    # to hit bonus
    plus_hit: int = 0
    # damage bonus
    plus_dmg: int = 0

    # damage dice expression
    dmg_dice: InitVar[str]

    def __post_init__(self, dmg_dice: str) -> None:
        self.base_dmg = parse_dice(dmg_dice)


def melee_attack(attacker: Actor, defender: Actor, level: Level, log: MessageLog) -> None:
    assert isinstance(attacker, Player) != isinstance(defender, Player)
    to_hit_bonus, damage_bonus = strength_bonuses(attacker)
    if isinstance(attacker, Player) and attacker.inventory.weapon_slot:
        to_hit_bonus += attacker.inventory.weapon_slot.weapon.plus_hit
        damage_bonus += attacker.inventory.weapon_slot.weapon.plus_dmg
    armor_class = defender.stats.ac
    if isinstance(defender, Player) and defender.inventory.armor_slot:
        armor_class = defender.inventory.armor_slot.armor.ac
    if defender.ai:
        defender.ai.on_attacked(defender)
    thac0 = 21 - attacker.stats.hd
    hit = roll(1, d=20) + to_hit_bonus >= thac0 - armor_class
    if hit:
        damage_dice = 1, attacker.stats.dmg
        if isinstance(attacker, Player) and attacker.inventory.weapon_slot:
            damage_dice = attacker.inventory.weapon_slot.weapon.base_dmg
        damage = roll(*damage_dice) + damage_bonus
        damage = max(0, damage)
        defender.stats.hp = max(0, defender.stats.hp - damage)
        log.append(f"You hit the {defender.name}." if isinstance(attacker, Player)
                   else f"The {attacker.name} hits you.")
        if defender.stats.hp == 0:
            level.entities.remove(defender)
            if isinstance(attacker, Player):
                log.append(f"You have defeated the {defender.name}.")
                attacker.stats.xp += defender.stats.xp
                level_up(attacker, log)
            else:
                assert isinstance(defender, Player)
                defender.cause_of_death = attacker.name
                log.append("You die...")
    else:
        log.append(f"You miss the {defender.name}." if isinstance(attacker, Player)
                   else f"The {attacker.name} misses you.")


def strength_bonuses(actor: Actor) -> tuple[int, int]:
    if actor.stats.strength == 16:
        assert isinstance(actor, Player)
        return 0, 1
    else:
        assert not isinstance(actor, Player) and actor.stats.strength == 10
        return 0, 0


def level_up(player: Actor, log: MessageLog) -> None:
    level = 1
    threshold = 10
    while player.stats.xp >= threshold:
        level += 1
        threshold *= 2
    if level > player.stats.hd:
        log.append(f"Welcome to level {level}!")
        hp_gain = roll(level - player.stats.hd, d=10)
        player.stats.max_hp += hp_gain
        player.stats.hp += hp_gain
        player.stats.hd = level
