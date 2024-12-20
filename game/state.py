from __future__ import annotations

import tcod

import game.turn
from game.action import (
    Action,
    BumpAction,
    DropAction,
    IdentifyAction,
    PickUpAction,
    StairsAction,
    TakeOffAction,
    UseAction,
    WaitAction,
)
from game.constants import Glyph
from game.entity import Item, Player
from game.input import Command, MoveCommand, handle_play_event, is_cancel, is_continue, to_index
from game.level import Level
from game.messages import MessageLog
from game.render import (
    fullscreen_select_prompt,
    fullscreen_wait_prompt,
    map_height,
    message_lines,
    render_inventory,
    render_map,
    render_messages,
    render_status,
    render_symbol_key,
    render_tombstone,
    screen_height,
)
from game.strings import help_text
from game.theme import Theme
from game.version import version_string


class State:
    def render(self, console: tcod.Console, player: Player, level: Level, log: MessageLog, theme: Theme) -> None:
        raise NotImplementedError()

    def event(self, event: tcod.event.Event, player: Player, level: Level, log: MessageLog) -> State:
        raise NotImplementedError()


class Play(State):
    def __init__(self) -> None:
        self.messages: list[str] | None = None

    def render(self, console: tcod.Console, player: Player, level: Level, log: MessageLog, theme: Theme) -> None:
        if self.messages is None:
            self.messages = log.get_unread(message_lines)
        render_messages(console, self.messages, 0, theme)
        render_map(console, level, message_lines, theme)
        render_status(console, player, level, message_lines + map_height, theme)

    def event(self, event: tcod.event.Event, player: Player, level: Level, log: MessageLog) -> State:
        command = handle_play_event(event)
        action: Action
        match command:
            case MoveCommand(dx, dy):
                action = BumpAction(dx, dy)
                return do_action(action, player, level, log)
            case Command.WAIT:
                action = WaitAction()
                return do_action(action, player, level, log)
            case Command.STAIRS:
                action = StairsAction()
                return do_action(action, player, level, log)
            case Command.MESSAGES:
                return FullscreenLog()
            case Command.KEYS:
                return KeyScreen()
            case Command.INVENTORY:
                return ShowInventory()
            case Command.HELP:
                return HelpScreen()
            case Command.DROP:
                return DropItem()
            case Command.PICKUP:
                action = PickUpAction()
                return do_action(action, player, level, log)
            case Command.QUAFF:
                return UseItem(glyph=Glyph.POTION, verb="quaff")
            case Command.READ:
                return UseItem(glyph=Glyph.SCROLL, verb="read")
            case Command.EAT:
                return UseItem(glyph=Glyph.FOOD, verb="eat")
            case Command.WIELD:
                if player.inventory.weapon_slot and player.inventory.weapon_slot.cursed:
                    log.append("You can't. It appears to be cursed.")
                    return Play()
                return UseItem(glyph=Glyph.WEAPON, verb="wield")
            case Command.WEAR:
                if player.inventory.armor_slot:
                    log.append("You are already wearing some. You'll have to take it off first.")
                    return Play()
                return UseItem(glyph=Glyph.ARMOR, verb="wear")
            case Command.TAKEOFF:
                action = TakeOffAction()
                return do_action(action, player, level, log)
            case Command.VERSION:
                log.append(f"Y.A.R.C. version {version_string.lstrip('v')}")
                return Play()
        return self


def do_action(action: Action, player: Player, level: Level, log: MessageLog) -> State:
    end_turn, next_state = action.perform(player, level, log)
    if end_turn:
        game.turn.end_turn(player, level, log)
    if player.stats.hp == 0:
        log.append("You die...")
        next_state = GameOver()
    if next_state:
        return More(next_state=next_state)
    if log.unread > message_lines:
        return More()
    return Play()


class More(State):
    def __init__(self, next_state: State | None = None) -> None:
        self.next_state = next_state
        self.messages: list[str] | None = None

    def render(self, console: tcod.Console, player: Player, level: Level, log: MessageLog, theme: Theme) -> None:
        if self.messages is None:
            self.messages = log.get_unread(message_lines)
            self.messages[-1] += "--More--"
        render_messages(console, self.messages, 0, theme)
        render_map(console, level, message_lines, theme)
        render_status(console, player, level, message_lines + map_height, theme)

    def event(self, event: tcod.event.Event, player: Player, level: Level, log: MessageLog) -> State:
        if is_continue(event):
            if self.next_state:
                if log.unread > 0:
                    return More(self.next_state)
                else:
                    return self.next_state
            if log.unread > message_lines:
                return More()
            else:
                return Play()
        else:
            return self


class GameOver(State):
    def render(self, console: tcod.Console, player: Player, level: Level, log: MessageLog, theme: Theme) -> None:
        render_tombstone(console, player, theme)

    def event(self, event: tcod.event.Event, player: Player, level: Level, log: MessageLog) -> State:
        if is_continue(event):
            raise SystemExit()
        return self


class FullscreenLog(State):
    def render(self, console: tcod.Console, player: Player, level: Level, log: MessageLog, theme: Theme) -> None:
        render_messages(console, log.get_latest(screen_height - 2), 0, theme)
        fullscreen_wait_prompt(console, theme)

    def event(self, event: tcod.event.Event, player: Player, level: Level, log: MessageLog) -> State:
        if is_continue(event):
            return Play()
        return self


class KeyScreen(State):
    def render(self, console: tcod.Console, player: Player, level: Level, log: MessageLog, theme: Theme) -> None:
        render_symbol_key(console, theme)
        fullscreen_wait_prompt(console, theme)

    def event(self, event: tcod.event.Event, player: Player, level: Level, log: MessageLog) -> State:
        if is_continue(event):
            return Play()
        return self


class ShowInventory(State):
    def render(self, console: tcod.Console, player: Player, level: Level, log: MessageLog, theme: Theme) -> None:
        render_inventory(console, player.inventory, theme)
        fullscreen_wait_prompt(console, theme)

    def event(self, event: tcod.event.Event, player: Player, level: Level, log: MessageLog) -> State:
        if is_continue(event):
            return Play()
        return self


class HelpScreen(State):
    def render(self, console: tcod.Console, player: Player, level: Level, log: MessageLog, theme: Theme) -> None:
        render_messages(console, help_text, 0, theme)
        fullscreen_wait_prompt(console, theme)

    def event(self, event: tcod.event.Event, player: Player, level: Level, log: MessageLog) -> State:
        if is_continue(event):
            return Play()
        return self


class DropItem(State):
    def render(self, console: tcod.Console, player: Player, level: Level, log: MessageLog, theme: Theme) -> None:
        render_inventory(console, player.inventory, theme)
        fullscreen_select_prompt(console, "drop", theme)

    def event(self, event: tcod.event.Event, player: Player, level: Level, log: MessageLog) -> State:
        if is_cancel(event):
            return Play()
        if player.inventory.items:
            index = to_index(event, max_l=ord('a') + len(player.inventory.items) - 1)
            if index is not None:
                item = player.inventory.items[index]
                action = DropAction(item)
                return do_action(action, player, level, log)
        return self


class UseItem(State):
    def __init__(self, glyph: Glyph, verb: str):
        self.glyph = glyph
        self.verb = verb

    def render(self, console: tcod.Console, player: Player, level: Level, log: MessageLog, theme: Theme) -> None:
        render_inventory(console, player.inventory, theme, filter_by_glyph=self.glyph)
        fullscreen_select_prompt(console, self.verb, theme)

    def event(self, event: tcod.event.Event, player: Player, level: Level, log: MessageLog) -> State:
        if is_cancel(event):
            return Play()
        if player.inventory.items:
            index = to_index(event, max_l=ord('a') + len(player.inventory.items) - 1)
            if index is not None:
                item = player.inventory.items[index]
                if item.glyph == self.glyph:
                    action = UseAction(item)
                    return do_action(action, player, level, log)
        return self


class IdentifyItem(State):
    def __init__(self, scroll: Item):
        self.scroll = scroll

    def render(self, console: tcod.Console, player: Player, level: Level, log: MessageLog, theme: Theme) -> None:
        render_inventory(console, player.inventory, theme)
        fullscreen_select_prompt(console, "identify", theme, escape=False)

    def event(self, event: tcod.event.Event, player: Player, level: Level, log: MessageLog) -> State:
        assert len(player.inventory.items) > 0
        index = to_index(event, max_l=ord('a') + len(player.inventory.items) - 1)
        if index is not None:
            item = player.inventory.items[index]
            action = IdentifyAction(item)
            player.inventory.remove_item(self.scroll)
            return do_action(action, player, level, log)
        return self
