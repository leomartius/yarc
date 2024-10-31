from __future__ import annotations

import random
from dataclasses import InitVar, dataclass, field

from game.dice import parse_dice, roll
from game.entity import Actor, Player
from game.level import Level
from game.messages import MessageLog


@dataclass(eq=False, slots=True, kw_only=True)
class Stats:
    # current hit points
    hp: int = field(init=False)
    # maximum hit points
    max_hp: int
    # (natural) armor class
    ac: int
    # hit dice (character level)
    hd: int
    # damage dice (unarmed strike)
    base_dmg: list[tuple[int, int]] = field(init=False)
    # xp value (current experience)
    xp: int
    # strength
    strength: int = 10
    # maximum strength
    max_strength: int = field(init=False)

    # damage dice expression
    dmg_dice: InitVar[str]

    def __post_init__(self, dmg_dice: str) -> None:
        self.hp = self.max_hp
        self.base_dmg = parse_dice(dmg_dice)
        self.max_strength = self.strength


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
    base_dmg: list[tuple[int, int]] = field(init=False)
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
    damage_dice = attacker.stats.base_dmg
    to_hit_bonus, damage_bonus = strength_bonuses(attacker)
    if isinstance(attacker, Player) and attacker.inventory.weapon_slot:
        damage_dice = attacker.inventory.weapon_slot.weapon.base_dmg
        to_hit_bonus += attacker.inventory.weapon_slot.weapon.plus_hit
        damage_bonus += attacker.inventory.weapon_slot.weapon.plus_dmg
    if defender.ai and defender.ai.is_helpless():
        to_hit_bonus += 4
    armor_class = defender.stats.ac
    if isinstance(defender, Player) and defender.inventory.armor_slot:
        armor_class = defender.inventory.armor_slot.armor.ac
    if defender.ai:
        defender.ai.on_attacked(defender)
    action_hit = False
    action_dmg = 0
    for n, d in damage_dice:
        thac0 = 21 - attacker.stats.hd
        attack_hit = roll(1, d=20) + to_hit_bonus >= thac0 - armor_class
        if attack_hit:
            attack_dmg = roll(n, d) + damage_bonus
            action_dmg += max(0, attack_dmg)
            action_hit = True
    if action_hit:
        defender.stats.hp = max(0, defender.stats.hp - action_dmg)
        log.append(hit_message(attacker, defender))
        if defender.stats.hp == 0:
            level.entities.remove(defender)
            if isinstance(attacker, Player):
                log.append(f"You defeat the {defender.name}.")
                attacker.stats.xp += defender.stats.xp
                level_up(attacker, log)
            else:
                assert isinstance(defender, Player)
                defender.cause_of_death = attacker.name
                log.append("You die...")
        elif attacker.special_attack:
            attacker.special_attack.apply(attacker, defender, level, log)
    else:
        log.append(miss_message(attacker, defender))


def hit_message(attacker: Actor, defender: Actor) -> str:
    if isinstance(attacker, Player):
        return random.choice(you_hit).format(defender.name)
    else:
        return random.choice(it_hits).format(attacker.name)


def miss_message(attacker: Actor, defender: Actor) -> str:
    if isinstance(attacker, Player):
        return random.choice(you_miss).format(defender.name)
    else:
        return random.choice(it_misses).format(attacker.name)


def strength_bonuses(actor: Actor) -> tuple[int, int]:
    assert 3 <= actor.stats.strength <= 31
    match actor.stats.strength:
        case 31:
            return +3, +6
        case x if 22 <= x <= 30:
            return +2, +5
        case 21:
            return +2, +4
        case 20:
            return +2, +3
        case 19:
            return +1, +3
        case 18:
            return +1, +2
        case 17:
            return +1, +1
        case 16:
            return 0, +1
        case x if 7 <= x <= 15:
            return 0, 0
        case x:
            assert 3 <= x <= 6
            return x - 7, x - 7


def save_vs_poison(actor: Actor) -> bool:
    target = 14 - actor.stats.hd // 2
    return roll(1, d=20) >= target


def save_vs_magic(actor: Actor) -> bool:
    target = 17 - actor.stats.hd // 2
    return roll(1, d=20) >= target


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


you_hit = [
    "You hit the {}.",
    "You swing and hit the {}.",
    "You score an excellent hit on the {}.",
    "You injure the {}.",
]

it_hits = [
    "The {} hits you.",
    "The {} swings and hits you.",
    "The {} scores an excellent hit on you.",
    "The {} injures you.",
]

you_miss = [
    "You miss the {}.",
    "You swing and miss the {}.",
    "You barely miss the {}.",
    "You don't hit the {}.",
]

it_misses = [
    "The {} misses you.",
    "The {} swings and misses you.",
    "The {} barely misses you.",
    "The {} doesn't hit you.",
]
