from __future__ import annotations

import random


def roll(n: int, d: int) -> int:
    assert n > 0 and d > 0
    total = 0
    for _ in range(n):
        total += random.randint(1, d)
    return total


def percent(p: int) -> bool:
    return random.randrange(100) < p
