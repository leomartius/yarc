from __future__ import annotations

from copy import deepcopy
from dataclasses import KW_ONLY, InitVar, dataclass, field

from game.actor_ai import ActorAI, GreedyAI, IdleAI, MeanAI
from game.attack import Attack
from game.combat import Stats
from game.constants import Glyph
from game.dice import roll
from game.entity import Actor


@dataclass(frozen=True, slots=True)
class MonsterType:
    ch: str
    name: str
    _: KW_ONLY
    stats: Stats = field(init=False)
    erratic: int | None = None
    invis: bool = False
    special: Attack | None = None
    ai: type[ActorAI] = MeanAI
    generate: bool = True

    hd: InitVar[int]
    ac: InitVar[int]
    dmg_dice: InitVar[str]
    xp_value: InitVar[int]

    def __post_init__(self, hd: int, ac: int, dmg_dice: str, xp_value: int) -> None:
        object.__setattr__(self, 'stats', Stats(max_hp=0, hd=hd, ac=ac, dmg_dice=dmg_dice, xp=xp_value))

    def spawn(self, x: int, y: int, extra_hd: int) -> Actor:
        stats = deepcopy(self.stats)
        stats.hd += extra_hd
        stats.ac -= extra_hd
        stats.hp = stats.max_hp = roll(stats.hd, d=8)
        if stats.hd > 9:
            bonus_xp = (stats.max_hp // 6) * 20
        elif stats.hd > 6:
            bonus_xp = (stats.max_hp // 6) * 4
        elif stats.hd > 1:
            bonus_xp = stats.max_hp // 6
        else:
            bonus_xp = stats.max_hp // 8
        stats.xp += bonus_xp + extra_hd * 10
        return Actor(
            x=x,
            y=y,
            glyph=Glyph.MONSTER,
            char=self.ch,
            name=self.name,
            stats=stats,
            erratic=self.erratic,
            invisible=self.invis,
            special_attack=self.special,
            ai=self.ai(),
        )


monsters: list[MonsterType] = [
    MonsterType('K', "kobold", hd=1, ac=7, dmg_dice='1d4', xp_value=1),
    MonsterType('J', "jackal", hd=1, ac=7, dmg_dice='1d2', xp_value=2),
    MonsterType('B', "bat", hd=1, ac=3, dmg_dice='1d2', xp_value=1, erratic=50, ai=IdleAI),
    MonsterType('S', "snake", hd=1, ac=5, dmg_dice='1d3', xp_value=2),
    MonsterType('H', "hobgoblin", hd=1, ac=5, dmg_dice='1d8', xp_value=3),
    MonsterType('E', "floating eye", hd=1, ac=9, dmg_dice='0d0', xp_value=5, ai=IdleAI, generate=False),
    MonsterType('A', "giant ant", hd=2, ac=3, dmg_dice='1d6', xp_value=9),
    MonsterType('O', "orc", hd=1, ac=6, dmg_dice='1d8', xp_value=5, ai=GreedyAI),
    MonsterType('Z', "zombie", hd=2, ac=8, dmg_dice='1d8', xp_value=6),
    MonsterType('G', "gnome", hd=1, ac=5, dmg_dice='1d6', xp_value=7, ai=IdleAI),
    MonsterType('L', "leprechaun", hd=3, ac=8, dmg_dice='1d1', xp_value=10, ai=IdleAI, generate=False),
    MonsterType('C', "centaur", hd=4, ac=4, dmg_dice='1d6/1d6', xp_value=15, ai=IdleAI),
    MonsterType('R', "rust monster", hd=5, ac=2, dmg_dice='0d0/0d0', xp_value=20, generate=False),
    MonsterType('Q', "quasit", hd=3, ac=2, dmg_dice='1d2/1d2/1d4', xp_value=32),
    MonsterType('N', "nymph", hd=3, ac=9, dmg_dice='0d0', xp_value=37, ai=IdleAI, generate=False),
    MonsterType('Y', "yeti", hd=4, ac=6, dmg_dice='1d6/1d6', xp_value=50, ai=IdleAI),
    MonsterType('T', "troll", hd=6, ac=4, dmg_dice='1d8/1d8/2d6', xp_value=120),
    MonsterType('W', "wraith", hd=5, ac=4, dmg_dice='1d6', xp_value=55, ai=IdleAI),
    MonsterType('F', "violet fungi", hd=8, ac=3, dmg_dice='0d0', xp_value=80, generate=False),
    MonsterType('I', "invisible stalker", hd=8, ac=3, dmg_dice='4d4', xp_value=120, erratic=20, invis=True, ai=IdleAI),
    MonsterType('X', "xorn", hd=7, ac=-2, dmg_dice='1d3/1d3/1d3/4d6', xp_value=190),
    MonsterType('U', "umber hulk", hd=8, ac=2, dmg_dice='3d4/3d4/2d5', xp_value=200),
    MonsterType('M', "mimic", hd=7, ac=7, dmg_dice='3d4', xp_value=100, ai=IdleAI, generate=False),
    MonsterType('V', "vampire", hd=8, ac=1, dmg_dice='1d10', xp_value=350),
    MonsterType('P', "purple worm", hd=15, ac=6, dmg_dice='2d12/2d4', xp_value=4000, ai=IdleAI),
    MonsterType('D', "dragon", hd=10, ac=-1, dmg_dice='1d8/1d8/3d10', xp_value=6800),
]


def get_monster_types(depth: int) -> tuple[list[MonsterType], list[int]]:
    items = []
    weights = []
    for i, weight in enumerate(_weights(depth)):
        if weight > 0 and monsters[i].generate:
            items.append(monsters[i])
            weights.append(weight)
    return items, weights


def _weights(depth: int) -> list[int]:
    assert depth >= 1
    weights = [0] * 26
    under = 0
    over = 0
    for i in range(depth - 6, depth + 4):
        if i < 0:
            under += 10
        elif i >= len(weights):
            over += 10
        else:
            weights[i] += 10
    for i in range(0, 5):
        weights[i] += under // 5
    for i in range(21, 26):
        weights[i] += over // 5
    assert len(weights) == 26
    assert sum(weights) == 100
    return weights
