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


def parse_dice(expression: str) -> list[tuple[int, int]]:
    assert re.match(r"^\d+d\d+(/\d+d\d+)*$", expression)
    result = []
    for dice in expression.split('/'):
        n, d = dice.split('d')
        result.append((int(n), int(d)))
    return result
