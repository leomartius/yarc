from __future__ import annotations

import logging
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
from game.version import version_string

logger = logging.getLogger(__name__)


def show_menu(datadir: Path, savefile: Path, theme_name: str) -> Never:
    logger.info("Starting main UI initialization.")
    logger.debug(f"Loading theme: {theme_name}")
    theme: game.theme.Theme = getattr(game.theme, theme_name)
    tileset = theme.load_tileset(datadir)
    with tcod.context.new(
            columns=screen_width,
            rows=screen_height,
            tileset=tileset,
            title="Yet Another Rogue Clone",
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
        console.print(0, 1, "Yet Another Rogue Clone", fg=theme.default_fg)
        console.print(1, 3, "n) Play a new game", fg=theme.default_fg)
        console.print(1, 4, "c) Continue last game", fg=theme.default_fg)
        console.print(1, 5, "q) Quit", fg=theme.default_fg)
        if load_error:
            console.print(1, 7, "No saved game to load.", fg=theme.default_fg)
        console.print(79, 23, version_string, fg=theme.default_fg, alignment=tcod.constants.RIGHT)
        context.present(console)
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
