from __future__ import annotations

from enum import IntEnum


class Tile(IntEnum):
    # solid tiles
    ROCK = 0
    H_WALL = 1
    V_WALL = 2
    # walkable tiles
    FLOOR = 3
    PASSAGE = 4
    STAIRS = 5
    DOOR = 6
    # sentinel values
    DEFAULT = ROCK
    MAX_SOLID = V_WALL
    MIN_WALKABLE = FLOOR
    MAX_VALUE = DOOR


class Glyph(IntEnum):
    PLAYER = 0
    GOLD = 1
    POTION = 2
    SCROLL = 3
    FOOD = 4
    WEAPON = 5
    ARMOR = 6
    RING = 7
    WAND = 8
    AMULET = 9
    # monster glyphs depend on type
    MONSTER = -1
    # placeholder
    INVALID = -2
