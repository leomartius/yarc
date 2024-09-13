from __future__ import annotations

import tcod

from game.action import Action, BumpAction, DropAction, StairsAction, TakeOffAction, UseAction, WaitAction
from game.constants import Glyph
from game.entity import Player
from game.help import help_text
from game.input import Command, MoveCommand, handle_play_event, is_cancel, is_continue, to_index
from game.level import Level
from game.messages import MessageLog
from game.render import (
    fullscreen_cancel_prompt,
    fullscreen_wait_prompt,
    highlight_cursor,
    map_height,
    message_lines,
    render_inventory,
    render_map,
    render_messages,
    render_status,
    screen_height,
)
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
            case Command.LOOK:
                return LookAround(player, log)
            case Command.INVENTORY:
                return ShowInventory()
            case Command.HELP:
                return HelpScreen()
            case Command.DROP:
                return DropItem()
            case Command.QUAFF:
                return UseItem(glyph=Glyph.POTION)
            case Command.READ:
                return UseItem(glyph=Glyph.SCROLL)
            case Command.WIELD:
                return UseItem(glyph=Glyph.WEAPON)
            case Command.WEAR:
                return UseItem(glyph=Glyph.ARMOR)
            case Command.TAKEOFF:
                action = TakeOffAction()
                return do_action(action, player, level, log)
            case Command.VERSION:
                log.append(f"Y.A.R.C. version {version_string.lstrip('v')}")
                return Play()
        return self


def do_action(action: Action, player: Player, level: Level, log: MessageLog) -> State:
    end_turn = action.perform(player, level, log)
    if end_turn:
        level.update_fov(player.x, player.y)
        for actor in level.actors:
            if actor.ai:
                actor.ai.take_turn(actor, level, player).perform(actor, level, log)
    if player.stats.hp == 0:
        return GameOver()
    if log.unread > message_lines:
        return More()
    return Play()


class More(State):
    def __init__(self) -> None:
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
            if log.unread > message_lines:
                return More()
            else:
                return Play()
        else:
            return self


class GameOver(State):
    def render(self, console: tcod.Console, player: Player, level: Level, log: MessageLog, theme: Theme) -> None:
        render_status(console, player, level, message_lines + map_height, theme)
        render_messages(console, log.get_latest(message_lines), 0, theme)

    def event(self, event: tcod.event.Event, player: Player, level: Level, log: MessageLog) -> State:
        return self


class FullscreenLog(State):
    def render(self, console: tcod.Console, player: Player, level: Level, log: MessageLog, theme: Theme) -> None:
        render_messages(console, log.get_latest(screen_height - 2), 0, theme)
        fullscreen_wait_prompt(console, theme)

    def event(self, event: tcod.event.Event, player: Player, level: Level, log: MessageLog) -> State:
        if is_continue(event):
            return Play()
        return self


class LookAround(State):
    def __init__(self, player: Player, log: MessageLog):
        log.append("Pick an object...")
        self.x, self.y = player.x, player.y

    def render(self, console: tcod.Console, player: Player, level: Level, log: MessageLog, theme: Theme) -> None:
        render_map(console, level, message_lines, theme)
        highlight_cursor(console, self.x, self.y, message_lines)
        render_messages(console, log.get_latest(message_lines), 0, theme)
        fullscreen_wait_prompt(console, theme)

    def event(self, event: tcod.event.Event, player: Player, level: Level, log: MessageLog) -> State:
        if is_continue(event):
            actor = level.get_actor_at(self.x, self.y)
            if actor:
                log.append(actor.name)
            else:
                item = level.get_item_at(self.x, self.y)
                if item:
                    log.append(item.name)
            log.get_unread(1)
            return Play()
        command = handle_play_event(event)
        if isinstance(command, MoveCommand):
            if level.in_bounds(self.x + command.dx, self.y + command.dy):
                self.x, self.y = self.x + command.dx, self.y + command.dy
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
        fullscreen_cancel_prompt(console, theme)

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
    def __init__(self, glyph: Glyph):
        self.glyph = glyph

    def render(self, console: tcod.Console, player: Player, level: Level, log: MessageLog, theme: Theme) -> None:
        render_inventory(console, player.inventory, theme, filter_by_glyph=self.glyph)
        fullscreen_cancel_prompt(console, theme)

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
