from __future__ import annotations

from typing import Literal

import numpy as np
import tcod

from game.constants import Glyph
from game.entity import Actor, Player
from game.inventory import Inventory
from game.level import Level
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
                equipped = ' (wielded)'
            elif item is inventory.armor_slot:
                equipped = ' (worn)'
            else:
                equipped = ''
            console.print(0, y, f"{chr(letter)}) a {item.name}" + equipped, fg=theme.default_fg)
            y += 1
        letter += 1
    if y == 0:
        console.print(0, 0, "Your inventory is empty.", fg=theme.default_fg)


def fullscreen_wait_prompt(console: tcod.Console, theme: Theme) -> None:
    console.print(0, screen_height - 1, "-- Press space bar to return --", fg=theme.default_fg)


def fullscreen_cancel_prompt(console: tcod.Console, theme: Theme) -> None:
    console.print(0, screen_height - 1, "-- Press Esc to cancel --", fg=theme.default_fg)


def highlight_cursor(console: tcod.Console, x: int, y: int, offset_y: int) -> None:
    y += offset_y
    r, g, b = console.rgb['bg'][x, y]
    console.rgb['bg'][x, y] = console.rgb['fg'][x, y]
    console.rgb['fg'][x, y] = r, g, b
