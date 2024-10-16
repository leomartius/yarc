from __future__ import annotations

from dataclasses import KW_ONLY, dataclass

from game.actor_ai import ActorAI, GreedyAI, IdleAI, MeanAI
from game.combat import Stats
from game.constants import Glyph
from game.dice import roll
from game.entity import Actor


@dataclass(frozen=True, slots=True)
class MonsterType:
    ch: str
    name: str
    _: KW_ONLY
    hd: int
    ac: int
    dmg: int
    xp_value: int
    ai: type[ActorAI] = MeanAI
    generate: bool = True

    def spawn(self, x: int, y: int) -> Actor:
        return Actor(x=x, y=y, glyph=Glyph.MONSTER, char=self.ch, name=self.name,
                     stats=Stats(max_hp=roll(self.hd, d=8), hd=self.hd, ac=self.ac, dmg=self.dmg, xp=self.xp_value),
                     ai=self.ai())


monsters: list[MonsterType] = [
    MonsterType('K', "kobold", hd=1, ac=7, dmg=4, xp_value=1),
    MonsterType('J', "jackal", hd=1, ac=7, dmg=2, xp_value=2),
    MonsterType('B', "bat", hd=1, ac=3, dmg=2, xp_value=1, ai=IdleAI),
    MonsterType('S', "snake", hd=1, ac=5, dmg=3, xp_value=2),
    MonsterType('H', "hobgoblin", hd=1, ac=5, dmg=8, xp_value=3),
    MonsterType('E', "floating eye", hd=1, ac=9, dmg=0, xp_value=5, ai=IdleAI, generate=False),
    MonsterType('A', "giant ant", hd=2, ac=3, dmg=6, xp_value=9),
    MonsterType('O', "orc", hd=1, ac=6, dmg=8, xp_value=5, ai=GreedyAI),
    MonsterType('Z', "zombie", hd=2, ac=8, dmg=8, xp_value=6),
    MonsterType('G', "gnome", hd=1, ac=5, dmg=6, xp_value=7, ai=IdleAI),
    MonsterType('L', "leprechaun", hd=3, ac=8, dmg=1, xp_value=10, ai=IdleAI, generate=False),
    MonsterType('C', "centaur", hd=4, ac=4, dmg=13, xp_value=15, ai=IdleAI),
    MonsterType('R', "rust monster", hd=5, ac=2, dmg=0, xp_value=20, generate=False),
    MonsterType('Q', "quasit", hd=3, ac=2, dmg=10, xp_value=32),
    MonsterType('N', "nymph", hd=3, ac=9, dmg=0, xp_value=37, ai=IdleAI, generate=False),
    MonsterType('Y', "yeti", hd=4, ac=6, dmg=13, xp_value=50, ai=IdleAI),
    MonsterType('T', "troll", hd=6, ac=4, dmg=31, xp_value=120),
    MonsterType('W', "wraith", hd=5, ac=4, dmg=6, xp_value=55, ai=IdleAI),
    MonsterType('F', "violet fungi", hd=8, ac=3, dmg=0, xp_value=80, generate=False),
    MonsterType('I', "invisible stalker", hd=8, ac=3, dmg=19, xp_value=120, ai=IdleAI, generate=False),
    MonsterType('X', "xorn", hd=7, ac=-2, dmg=39, xp_value=190),
    MonsterType('U', "umber hulk", hd=8, ac=2, dmg=41, xp_value=200),
    MonsterType('M', "mimic", hd=7, ac=7, dmg=14, xp_value=100, ai=IdleAI, generate=False),
    MonsterType('V', "vampire", hd=8, ac=1, dmg=10, xp_value=350),
    MonsterType('P', "purple worm", hd=15, ac=6, dmg=35, xp_value=4000, ai=IdleAI),
    MonsterType('D', "dragon", hd=10, ac=-1, dmg=50, xp_value=6800),
]


def eligible_monsters(depth: int) -> list[MonsterType]:
    min_level = max(1, min(depth - 5, len(monsters) - 4))
    max_level = max(5, min(depth + 4, len(monsters)))
    return [m for m in monsters[min_level - 1:max_level] if m.generate]
