from __future__ import annotations

from datetime import datetime
from typing import Literal

import numpy as np
import tcod

from game.constants import Glyph, Tile
from game.entity import Actor, Player
from game.inventory import Inventory
from game.level import Level
from game.strings import symbol_key, tombstone
from game.theme import Theme

# screen layout
map_width = 80
map_height = 22
status_lines = 1
message_lines = 1
screen_width = map_width
screen_height = message_lines + map_height + status_lines


def render_map(console: tcod.Console, level: Level, offset_y: int, theme: Theme) -> None:
    visible_map = theme.visible_glyphs[level.tiles]
    explored_map = theme.explored_glyphs[level.tiles]
    console.rgb[0:level.width, offset_y:(level.height + offset_y)] = np.select(
        condlist=[level.visible, level.explored],
        choicelist=[visible_map, explored_map],
        default=theme.unexplored,
    )

    for entity in sorted(level.entities, key=lambda en: isinstance(en, Actor)):
        if level.visible[entity.x, entity.y]:
            if isinstance(entity, Actor) and entity.glyph == Glyph.MONSTER:
                assert entity.char is not None
                console.print(entity.x, entity.y + offset_y, entity.char, fg=theme.monster_fg)
            else:
                char, foreground = theme.entity_glyphs[entity.glyph]
                console.print(entity.x, entity.y + offset_y, char, fg=foreground)


def render_status(console: tcod.Console, player: Player, level: Level, offset_y: int, theme: Theme) -> None:
    s = player.stats
    if player.inventory.armor_slot:
        ac = player.inventory.armor_slot.armor.ac
    else:
        ac = player.stats.ac
    status_line = (f"Level: {level.depth}  Gold: {player.gold}  "
                   f"Hp: {s.hp}({s.max_hp})  Str: {s.strength}  Ac: {ac}  Exp: {s.hd}/{s.xp}")
    console.print(0, offset_y, status_line, fg=theme.default_fg)


def render_messages(console: tcod.Console, messages: list[str], offset_y: int, theme: Theme) -> None:
    y = offset_y
    for message in messages:
        console.print(0, y, message, fg=theme.default_fg)
        y += 1


def render_inventory(console: tcod.Console, inventory: Inventory, theme: Theme, *,
                     filter_by_glyph: Glyph | Literal[False] = False) -> None:
    y = 0
    letter = ord('a')
    for item in inventory.items:
        if filter_by_glyph is False or item.glyph == filter_by_glyph:
            if item is inventory.weapon_slot:
                equipped = " (weapon in hand)"
            elif item is inventory.armor_slot:
                equipped = " (being worn)"
            else:
                equipped = ''
            console.print(0, y, f"{chr(letter)}) a {item.name}" + equipped, fg=theme.default_fg)
            y += 1
        letter += 1
    if y == 0:
        if filter_by_glyph is False:
            console.print(0, 0, "You are empty-handed.", fg=theme.default_fg)
        else:
            console.print(0, 0, "You don't have anything appropriate.", fg=theme.default_fg)


def render_symbol_key(console: tcod.Console, theme: Theme) -> None:
    y = 0
    for line in symbol_key:
        console.print(0, y, line, fg=theme.default_fg)
        y += 1

    def overlay_tile(x: int, y: int, tile: Tile) -> None:
        console.rgb[x, y] = theme.visible_glyphs[tile]

    overlay_tile(4, 0, Tile.FLOOR)
    overlay_tile(2, 1, Tile.H_WALL)
    overlay_tile(6, 1, Tile.V_WALL)
    overlay_tile(4, 2, Tile.DOOR)
    overlay_tile(4, 3, Tile.PASSAGE)
    overlay_tile(4, 4, Tile.STAIRS)
    overlay_tile(4, 5, Tile.TRAP)

    def overlay_glyph(x: int, y: int, glyph: Glyph) -> None:
        char, foreground = theme.entity_glyphs[glyph]
        console.print(x, y, char, fg=foreground)

    overlay_glyph(4, 6, Glyph.AMULET)
    overlay_glyph(4, 7, Glyph.PLAYER)
    overlay_glyph(44, 0, Glyph.GOLD)
    overlay_glyph(44, 1, Glyph.FOOD)
    overlay_glyph(44, 2, Glyph.POTION)
    overlay_glyph(44, 3, Glyph.SCROLL)
    overlay_glyph(44, 4, Glyph.WEAPON)
    overlay_glyph(44, 5, Glyph.ARMOR)
    overlay_glyph(44, 6, Glyph.RING)
    overlay_glyph(44, 7, Glyph.WAND)

    for i in range(13):
        console.print(4, 9 + i, chr(ord('A') + i), fg=theme.monster_fg)
        console.print(44, 9 + i, chr(ord('N') + i), fg=theme.monster_fg)


def render_tombstone(console: tcod.Console, player: Player, theme: Theme) -> None:
    offset_y = screen_height - len(tombstone) - 3
    y = offset_y
    for line in tombstone:
        console.print(0, y, line, fg=theme.default_fg)
        y += 1
    assert player.cause_of_death is not None
    killed_by = "killed by a"
    if player.cause_of_death[0] in 'aeiou':
        killed_by += "n"
    console.print(19, offset_y + 6, f"{player.name}".center(18), fg=theme.default_fg)
    console.print(19, offset_y + 7, f"{player.gold} Au".center(18), fg=theme.default_fg)
    console.print(19, offset_y + 8, killed_by.center(18), fg=theme.default_fg)
    console.print(19, offset_y + 9, player.cause_of_death.center(18), fg=theme.default_fg)
    console.print(19, offset_y + 10, f"{datetime.now().year}".center(18), fg=theme.default_fg)
    console.print(0, screen_height - 1, "[Press enter to continue]", fg=theme.default_fg)


def fullscreen_wait_prompt(console: tcod.Console, theme: Theme) -> None:
    console.print(0, screen_height - 1, "--Press space to continue--", fg=theme.default_fg)


def fullscreen_cancel_prompt(console: tcod.Console, theme: Theme) -> None:
    console.print(0, screen_height - 1, "--Press Esc to cancel--", fg=theme.default_fg)
