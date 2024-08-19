from __future__ import annotations

from dataclasses import dataclass, KW_ONLY

from game.actor_ai import ActorAI, IdleAI, MeanAI
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

    def spawn(self, x: int, y: int) -> Actor:
        return Actor(x=x, y=y, glyph=Glyph.MONSTER, char=self.ch, name=self.name,
                     stats=Stats(max_hp=roll(self.hd, d=8), hd=self.hd, ac=self.ac, dmg=self.dmg, xp=self.xp_value),
                     ai=self.ai())


monsters: list[MonsterType] = [
    MonsterType('K', 'kobold', hd=1, ac=7, dmg=4, xp_value=1),
    MonsterType('J', 'jackal', hd=1, ac=7, dmg=2, xp_value=2),
    MonsterType('B', 'bat', hd=1, ac=3, dmg=2, xp_value=1, ai=IdleAI),  # TODO erratic movement
    MonsterType('S', 'snake', hd=1, ac=5, dmg=3, xp_value=3),
    MonsterType('H', 'hobgoblin', hd=1, ac=5, dmg=8, xp_value=3),
    NotImplemented,  # E floating eye
    NotImplemented,  # A giant ant
    MonsterType('O', 'orc', hd=1, ac=6, dmg=8, xp_value=5),
    MonsterType('Z', 'zombie', hd=2, ac=8, dmg=8, xp_value=7),
    MonsterType('G', 'gnome', hd=1, ac=5, dmg=6, xp_value=8, ai=IdleAI),
    NotImplemented,  # L leprechaun
    MonsterType('C', 'centaur', hd=4, ac=4, dmg=13, xp_value=15, ai=IdleAI),  # TODO multiple attacks
    NotImplemented,  # R rust monster
    MonsterType('Q', 'quasit', hd=3, ac=2, dmg=10, xp_value=35),  # TODO multiple attacks
    NotImplemented,  # N nymph
    MonsterType('Y', 'yeti', hd=4, ac=6, dmg=13, xp_value=50, ai=IdleAI),  # TODO multiple attacks
]


def eligible_monsters(depth: int) -> list[MonsterType]:
    min_level = max(1, min(depth - 5, len(monsters) - 4))
    max_level = max(5, min(depth + 4, len(monsters)))
    return [m for m in monsters[min_level - 1:max_level] if isinstance(m, MonsterType)]
