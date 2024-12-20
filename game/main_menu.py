from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Never

import tcod

import game.theme
from game.entity import Player
from game.game_loop import game_loop, new_game
from game.level import Level
from game.messages import MessageLog
from game.render import screen_height, screen_width
from game.save import load_game
from game.strings import banner
from game.version import version_string

logger = logging.getLogger(__name__)


def show_menu(datadir: Path, savefile: Path, theme_name: str, borderless: bool, scale_factor: int) -> Never:
    logger.info("Starting main UI initialization.")
    if os.name == 'nt':
        tcod.lib.SDL_SetHint(b'SDL_WINDOWS_DPI_AWARENESS', b'system')
    logger.debug(f"Loading theme: {theme_name}")
    theme: game.theme.Theme = getattr(game.theme, theme_name)
    tileset = theme.load_tileset(datadir)
    with tcod.context.new(
        columns=screen_width,
        rows=screen_height,
        width=screen_width * tileset.tile_width * scale_factor,
        height=screen_height * tileset.tile_height * scale_factor,
        tileset=tileset,
        title="Yet Another Rogue Clone",
        sdl_window_flags=tcod.context.SDL_WINDOW_BORDERLESS if borderless else None,
    ) as context:
        console = tcod.console.Console(screen_width, screen_height, order='F')
        player, level, log = main_menu(context, console, theme, savefile)
        game_loop(context, console, theme, savefile, player, level, log)


def main_menu(
    context: tcod.context.Context, console: tcod.Console, theme: game.theme.Theme, savefile: Path
) -> tuple[Player, Level, MessageLog]:
    load_error = False
    while True:
        console.clear(fg=theme.default_fg, bg=theme.default_bg)
        y = 0

        def center(text: str, skip_lines: int = 0) -> None:
            nonlocal y
            y += skip_lines
            console.print(screen_width // 2, y, text, alignment=tcod.constants.CENTER)
            y += 1

        for line in banner:
            center(line)
        center("-= Yet Another Rogue Clone =-", 1)
        center("Start (N)ew Game", 1)
        center("(C)ontinue Saved Game")
        center("(Q)uit")
        if load_error:
            center("No saved game found.", 2)
        console.print(screen_width - 1, screen_height - 1, version_string, alignment=tcod.constants.RIGHT)
        context.present(console, keep_aspect=True, integer_scaling=True, clear_color=theme.default_bg)
        for event in tcod.event.wait():
            if isinstance(event, tcod.event.Quit):
                raise SystemExit()
            if isinstance(event, tcod.event.KeyDown):
                if load_error:
                    load_error = False
                    continue
                if event.sym in (tcod.event.KeySym.q, tcod.event.KeySym.ESCAPE):
                    raise SystemExit()
                elif event.sym == tcod.event.KeySym.c:
                    saved_state = load_game(savefile)
                    if saved_state is not None:
                        player, level, log = saved_state
                        return player, level, log
                    else:
                        load_error = True
                elif event.sym == tcod.event.KeySym.n:
                    logger.info("New game started.")
                    player, level, log = new_game()
                    return player, level, log
