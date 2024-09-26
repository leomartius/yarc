from __future__ import annotations

import random
import re


def roll(n: int, d: int) -> int:
    assert n > 0 and d > 0
    total = 0
    for _ in range(n):
        total += random.randint(1, d)
    return total


def percent(p: int) -> bool:
    return random.randrange(100) < p


def parse_dice(dice: str) -> tuple[int, int]:
    assert re.match(r"^\d+d\d+$", dice)
    n, d = dice.split('d')
    return int(n), int(d)
