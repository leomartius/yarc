from __future__ import annotations

from enum import IntEnum


class Tile(IntEnum):
    # solid tiles
    ROCK = 0
    TL_CORNER = 1
    TR_CORNER = 2
    BL_CORNER = 3
    BR_CORNER = 4
    H_WALL = 5
    V_WALL = 6
    # walkable tiles
    FLOOR = 7
    PASSAGE = 8
    STAIRS = 9
    TRAP = 10
    DOOR = 11
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
    MAGIC = 10
    # monster glyphs depend on type
    MONSTER = -1
    # placeholder
    INVALID = -2
