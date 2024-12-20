from __future__ import annotations

from pathlib import Path
from typing import Never

import tcod

from game.combat import Armor, Stats, Weapon
from game.constants import Glyph
from game.consumable import Food
from game.entity import ArmorItem, Item, Player, WeaponItem
from game.inventory import Inventory
from game.level import Level
from game.messages import MessageLog
from game.procgen import generate_level
from game.render import map_height, map_width
from game.save import save_game
from game.state import GameOver, Play, State
from game.theme import Theme
from game.turn import wake_up_room


def new_game() -> tuple[Player, Level, MessageLog]:
    level = generate_level(map_width, map_height, 1)
    inventory = Inventory()
    food = Item(x=0, y=0, glyph=Glyph.FOOD, name="ration of food", consumable=Food(spoilable=True))
    inventory.add_item(food)
    armor = ArmorItem(
        x=0, y=0, glyph=Glyph.ARMOR, name="ring mail", armor=Armor(base_ac=7, plus_ac=+1), identified=True
    )
    inventory.add_item(armor)
    inventory.armor_slot = armor
    weapon = WeaponItem(
        x=0,
        y=0,
        glyph=Glyph.WEAPON,
        name="mace",
        weapon=Weapon(plus_hit=+1, plus_dmg=+1, dmg_dice='2d4'),
        identified=True,
    )
    inventory.add_item(weapon)
    inventory.weapon_slot = weapon
    player = Player(
        x=level.entry_x,
        y=level.entry_y,
        glyph=Glyph.PLAYER,
        name="Rodney",
        stats=Stats(max_hp=12, ac=10, hd=1, dmg_dice='1d4', xp=0, strength=16),
        gold=0,
        inventory=inventory,
        hunger_clock=1300,
    )
    level.entities.add(player)
    wake_up_room(level.get_room_at(player.x, player.y), level)
    level.update_fov(player.x, player.y)
    log = MessageLog()
    log.append("Welcome to the Dungeons of Doom! Press '?' for a list of available commands.")
    return player, level, log


def game_loop(context: tcod.context.Context, console: tcod.Console, theme: Theme, savefile: Path,
              player: Player, level: Level, log: MessageLog) -> Never:
    state: State = Play()
    while True:
        console.clear(fg=theme.default_fg, bg=theme.default_bg)
        state.render(console, player, level, log, theme)
        context.present(console, keep_aspect=True, integer_scaling=True, clear_color=theme.default_bg)
        for event in tcod.event.wait():
            if isinstance(event, tcod.event.Quit):
                if not isinstance(state, GameOver):
                    save_game(savefile, player, level, log)
                raise SystemExit()
            state = state.event(event, player, level, log)
            if level.completed:
                level = generate_level(map_width, map_height, level.depth + 1)
                player.x, player.y = level.entry_x, level.entry_y
                level.entities.add(player)
                wake_up_room(level.get_room_at(player.x, player.y), level)
                level.update_fov(player.x, player.y)
