from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import tcod


@dataclass(frozen=True, slots=True)
class Theme:
    tileset: tuple[str, int, int, Iterable[int]]
    default_fg: tuple[int, int, int]
    default_bg: tuple[int, int, int]
    status_fg: tuple[int, int, int]
    monster_fg: tuple[int, int, int]
    entity_glyphs: list[tuple[str, tuple[int, int, int]]]
    visible_glyphs: np.ndarray[Any, np.dtype[np.void]]
    explored_glyphs: np.ndarray[Any, np.dtype[np.void]]
    unexplored: np.void

    def load_tileset(self, datadir: Path) -> tcod.tileset.Tileset:
        filename, columns, rows, charmap = self.tileset
        return tcod.tileset.load_tilesheet(datadir / filename, columns, rows, charmap)


default = Theme(
    tileset=('vga-9x16-cp437.png', 16, 16, tcod.tileset.CHARMAP_CP437),
    default_fg=(0xAA, 0xAA, 0xAA),
    default_bg=(0x00, 0x00, 0x00),
    status_fg=(0xAA, 0xAA, 0xAA),
    monster_fg=(0xAA, 0xAA, 0xAA),
    entity_glyphs=[
        ('@', (0xAA, 0xAA, 0xAA)),  # player
        ('*', (0xAA, 0xAA, 0xAA)),  # gold
        ('!', (0xAA, 0xAA, 0xAA)),  # potion
        ('?', (0xAA, 0xAA, 0xAA)),  # scroll
        (':', (0xAA, 0xAA, 0xAA)),  # food
        (')', (0xAA, 0xAA, 0xAA)),  # weapon
        (']', (0xAA, 0xAA, 0xAA)),  # armor
        ('=', (0xAA, 0xAA, 0xAA)),  # ring
        ('/', (0xAA, 0xAA, 0xAA)),  # wand
        (',', (0xAA, 0xAA, 0xAA)),  # amulet
        ('$', (0xAA, 0xAA, 0xAA)),  # magic
    ],
    visible_glyphs=np.array(
        [
            (ord(' '), (0xAA, 0xAA, 0xAA), (0x00, 0x00, 0x00)),  # rock
            (ord('-'), (0xAA, 0xAA, 0xAA), (0x00, 0x00, 0x00)),  # top left corner
            (ord('-'), (0xAA, 0xAA, 0xAA), (0x00, 0x00, 0x00)),  # top right corner
            (ord('-'), (0xAA, 0xAA, 0xAA), (0x00, 0x00, 0x00)),  # bottom left corner
            (ord('-'), (0xAA, 0xAA, 0xAA), (0x00, 0x00, 0x00)),  # bottom right corner
            (ord('-'), (0xAA, 0xAA, 0xAA), (0x00, 0x00, 0x00)),  # horizontal wall
            (ord('|'), (0xAA, 0xAA, 0xAA), (0x00, 0x00, 0x00)),  # vertical wall
            (ord('.'), (0xAA, 0xAA, 0xAA), (0x00, 0x00, 0x00)),  # floor
            (ord('#'), (0xAA, 0xAA, 0xAA), (0x00, 0x00, 0x00)),  # passage
            (ord('%'), (0xAA, 0xAA, 0xAA), (0x00, 0x00, 0x00)),  # stairs
            (ord('^'), (0xAA, 0xAA, 0xAA), (0x00, 0x00, 0x00)),  # trap
            (ord('+'), (0xAA, 0xAA, 0xAA), (0x00, 0x00, 0x00)),  # door
        ],
        dtype=tcod.console.rgb_graphic,
    ),
    explored_glyphs=np.array(
        [
            (ord(' '), (0xAA, 0xAA, 0xAA), (0x00, 0x00, 0x00)),  # rock
            (ord('-'), (0xAA, 0xAA, 0xAA), (0x00, 0x00, 0x00)),  # top left corner
            (ord('-'), (0xAA, 0xAA, 0xAA), (0x00, 0x00, 0x00)),  # top right corner
            (ord('-'), (0xAA, 0xAA, 0xAA), (0x00, 0x00, 0x00)),  # bottom left corner
            (ord('-'), (0xAA, 0xAA, 0xAA), (0x00, 0x00, 0x00)),  # bottom right corner
            (ord('-'), (0xAA, 0xAA, 0xAA), (0x00, 0x00, 0x00)),  # horizontal wall
            (ord('|'), (0xAA, 0xAA, 0xAA), (0x00, 0x00, 0x00)),  # vertical wall
            (ord('.'), (0xAA, 0xAA, 0xAA), (0x00, 0x00, 0x00)),  # floor
            (ord('#'), (0xAA, 0xAA, 0xAA), (0x00, 0x00, 0x00)),  # passage
            (ord('%'), (0xAA, 0xAA, 0xAA), (0x00, 0x00, 0x00)),  # stairs
            (ord('^'), (0xAA, 0xAA, 0xAA), (0x00, 0x00, 0x00)),  # trap
            (ord('+'), (0xAA, 0xAA, 0xAA), (0x00, 0x00, 0x00)),  # door
        ],
        dtype=tcod.console.rgb_graphic,
    ),
    unexplored=np.void((ord(' '), (0xAA, 0xAA, 0xAA), (0x00, 0x00, 0x00)), dtype=tcod.console.rgb_graphic),
)


# =================
#  VT220 emulation
# =================

# The font used is 10x20, with an aspect ratio of 2 (instead of the correct
# 2.5), and features embedded scanlines to simulate the appearance of text on
# a CRT display. The colors aim to approximate those of P3 (amber), P1 (green),
# and P4 (white) phosphors, displayed on a dark gray background.

VT220 = ('vt220-10x20-ascii.png', 16, 6, range(32, 128))
MONO_BLACK = (0x1E, 0x1E, 0x1E)
MONO_AMBER = (0xFF, 0xA4, 0x00)
MONO_GREEN = (0x41, 0xFF, 0x00)
MONO_WHITE = (0xF9, 0xF2, 0xFF)

vt220_amber = Theme(
    tileset=VT220,
    default_fg=MONO_AMBER,
    default_bg=MONO_BLACK,
    status_fg=MONO_AMBER,
    monster_fg=MONO_AMBER,
    entity_glyphs=[
        ('@', MONO_AMBER),  # player
        ('*', MONO_AMBER),  # gold
        ('!', MONO_AMBER),  # potion
        ('?', MONO_AMBER),  # scroll
        (':', MONO_AMBER),  # food
        (')', MONO_AMBER),  # weapon
        (']', MONO_AMBER),  # armor
        ('=', MONO_AMBER),  # ring
        ('/', MONO_AMBER),  # wand
        (',', MONO_AMBER),  # amulet
        ('$', MONO_AMBER),  # magic
    ],
    visible_glyphs=np.array(
        [
            (ord(' '), MONO_AMBER, MONO_BLACK),  # rock
            (ord('-'), MONO_AMBER, MONO_BLACK),  # top left corner
            (ord('-'), MONO_AMBER, MONO_BLACK),  # top right corner
            (ord('-'), MONO_AMBER, MONO_BLACK),  # bottom left corner
            (ord('-'), MONO_AMBER, MONO_BLACK),  # bottom right corner
            (ord('-'), MONO_AMBER, MONO_BLACK),  # horizontal wall
            (ord('|'), MONO_AMBER, MONO_BLACK),  # vertical wall
            (ord('.'), MONO_AMBER, MONO_BLACK),  # floor
            (ord('#'), MONO_AMBER, MONO_BLACK),  # passage
            (ord('%'), MONO_AMBER, MONO_BLACK),  # stairs
            (ord('^'), MONO_AMBER, MONO_BLACK),  # trap
            (ord('+'), MONO_AMBER, MONO_BLACK),  # door
        ],
        dtype=tcod.console.rgb_graphic,
    ),
    explored_glyphs=np.array(
        [
            (ord(' '), MONO_AMBER, MONO_BLACK),  # rock
            (ord('-'), MONO_AMBER, MONO_BLACK),  # top left corner
            (ord('-'), MONO_AMBER, MONO_BLACK),  # top right corner
            (ord('-'), MONO_AMBER, MONO_BLACK),  # bottom left corner
            (ord('-'), MONO_AMBER, MONO_BLACK),  # bottom right corner
            (ord('-'), MONO_AMBER, MONO_BLACK),  # horizontal wall
            (ord('|'), MONO_AMBER, MONO_BLACK),  # vertical wall
            (ord('.'), MONO_AMBER, MONO_BLACK),  # floor
            (ord('#'), MONO_AMBER, MONO_BLACK),  # passage
            (ord('%'), MONO_AMBER, MONO_BLACK),  # stairs
            (ord('^'), MONO_AMBER, MONO_BLACK),  # trap
            (ord('+'), MONO_AMBER, MONO_BLACK),  # door
        ],
        dtype=tcod.console.rgb_graphic,
    ),
    unexplored=np.void((ord(' '), MONO_AMBER, MONO_BLACK), dtype=tcod.console.rgb_graphic),
)

vt220_green = Theme(
    tileset=VT220,
    default_fg=MONO_GREEN,
    default_bg=MONO_BLACK,
    status_fg=MONO_GREEN,
    monster_fg=MONO_GREEN,
    entity_glyphs=[
        ('@', MONO_GREEN),  # player
        ('*', MONO_GREEN),  # gold
        ('!', MONO_GREEN),  # potion
        ('?', MONO_GREEN),  # scroll
        (':', MONO_GREEN),  # food
        (')', MONO_GREEN),  # weapon
        (']', MONO_GREEN),  # armor
        ('=', MONO_GREEN),  # ring
        ('/', MONO_GREEN),  # wand
        (',', MONO_GREEN),  # amulet
        ('$', MONO_GREEN),  # magic
    ],
    visible_glyphs=np.array(
        [
            (ord(' '), MONO_GREEN, MONO_BLACK),  # rock
            (ord('-'), MONO_GREEN, MONO_BLACK),  # top left corner
            (ord('-'), MONO_GREEN, MONO_BLACK),  # top right corner
            (ord('-'), MONO_GREEN, MONO_BLACK),  # bottom left corner
            (ord('-'), MONO_GREEN, MONO_BLACK),  # bottom right corner
            (ord('-'), MONO_GREEN, MONO_BLACK),  # horizontal wall
            (ord('|'), MONO_GREEN, MONO_BLACK),  # vertical wall
            (ord('.'), MONO_GREEN, MONO_BLACK),  # floor
            (ord('#'), MONO_GREEN, MONO_BLACK),  # passage
            (ord('%'), MONO_GREEN, MONO_BLACK),  # stairs
            (ord('^'), MONO_GREEN, MONO_BLACK),  # trap
            (ord('+'), MONO_GREEN, MONO_BLACK),  # door
        ],
        dtype=tcod.console.rgb_graphic,
    ),
    explored_glyphs=np.array(
        [
            (ord(' '), MONO_GREEN, MONO_BLACK),  # rock
            (ord('-'), MONO_GREEN, MONO_BLACK),  # top left corner
            (ord('-'), MONO_GREEN, MONO_BLACK),  # top right corner
            (ord('-'), MONO_GREEN, MONO_BLACK),  # bottom left corner
            (ord('-'), MONO_GREEN, MONO_BLACK),  # bottom right corner
            (ord('-'), MONO_GREEN, MONO_BLACK),  # horizontal wall
            (ord('|'), MONO_GREEN, MONO_BLACK),  # vertical wall
            (ord('.'), MONO_GREEN, MONO_BLACK),  # floor
            (ord('#'), MONO_GREEN, MONO_BLACK),  # passage
            (ord('%'), MONO_GREEN, MONO_BLACK),  # stairs
            (ord('^'), MONO_GREEN, MONO_BLACK),  # trap
            (ord('+'), MONO_GREEN, MONO_BLACK),  # door
        ],
        dtype=tcod.console.rgb_graphic,
    ),
    unexplored=np.void((ord(' '), MONO_GREEN, MONO_BLACK), dtype=tcod.console.rgb_graphic),
)

vt220_white = Theme(
    tileset=VT220,
    default_fg=MONO_WHITE,
    default_bg=MONO_BLACK,
    status_fg=MONO_WHITE,
    monster_fg=MONO_WHITE,
    entity_glyphs=[
        ('@', MONO_WHITE),  # player
        ('*', MONO_WHITE),  # gold
        ('!', MONO_WHITE),  # potion
        ('?', MONO_WHITE),  # scroll
        (':', MONO_WHITE),  # food
        (')', MONO_WHITE),  # weapon
        (']', MONO_WHITE),  # armor
        ('=', MONO_WHITE),  # ring
        ('/', MONO_WHITE),  # wand
        (',', MONO_WHITE),  # amulet
        ('$', MONO_WHITE),  # magic
    ],
    visible_glyphs=np.array(
        [
            (ord(' '), MONO_WHITE, MONO_BLACK),  # rock
            (ord('-'), MONO_WHITE, MONO_BLACK),  # top left corner
            (ord('-'), MONO_WHITE, MONO_BLACK),  # top right corner
            (ord('-'), MONO_WHITE, MONO_BLACK),  # bottom left corner
            (ord('-'), MONO_WHITE, MONO_BLACK),  # bottom right corner
            (ord('-'), MONO_WHITE, MONO_BLACK),  # horizontal wall
            (ord('|'), MONO_WHITE, MONO_BLACK),  # vertical wall
            (ord('.'), MONO_WHITE, MONO_BLACK),  # floor
            (ord('#'), MONO_WHITE, MONO_BLACK),  # passage
            (ord('%'), MONO_WHITE, MONO_BLACK),  # stairs
            (ord('^'), MONO_WHITE, MONO_BLACK),  # trap
            (ord('+'), MONO_WHITE, MONO_BLACK),  # door
        ],
        dtype=tcod.console.rgb_graphic,
    ),
    explored_glyphs=np.array(
        [
            (ord(' '), MONO_WHITE, MONO_BLACK),  # rock
            (ord('-'), MONO_WHITE, MONO_BLACK),  # top left corner
            (ord('-'), MONO_WHITE, MONO_BLACK),  # top right corner
            (ord('-'), MONO_WHITE, MONO_BLACK),  # bottom left corner
            (ord('-'), MONO_WHITE, MONO_BLACK),  # bottom right corner
            (ord('-'), MONO_WHITE, MONO_BLACK),  # horizontal wall
            (ord('|'), MONO_WHITE, MONO_BLACK),  # vertical wall
            (ord('.'), MONO_WHITE, MONO_BLACK),  # floor
            (ord('#'), MONO_WHITE, MONO_BLACK),  # passage
            (ord('%'), MONO_WHITE, MONO_BLACK),  # stairs
            (ord('^'), MONO_WHITE, MONO_BLACK),  # trap
            (ord('+'), MONO_WHITE, MONO_BLACK),  # door
        ],
        dtype=tcod.console.rgb_graphic,
    ),
    unexplored=np.void((ord(' '), MONO_WHITE, MONO_BLACK), dtype=tcod.console.rgb_graphic),
)
