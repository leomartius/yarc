from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

import tcod


@dataclass(frozen=True, slots=True)
class MoveCommand:
    dx: int
    dy: int


class Command(Enum):
    WAIT = auto()
    STAIRS = auto()
    MESSAGES = auto()
    LOOK = auto()
    INVENTORY = auto()
    HELP = auto()
    DROP = auto()
    QUAFF = auto()
    READ = auto()
    WIELD = auto()
    WEAR = auto()
    TAKEOFF = auto()


MOVE_KEYS = {
    # Vim Keys (HJKL)
    tcod.event.KeySym.h: (-1, 0),
    tcod.event.KeySym.j: (0, 1),
    tcod.event.KeySym.k: (0, -1),
    tcod.event.KeySym.l: (1, 0),
    tcod.event.KeySym.y: (-1, -1),
    tcod.event.KeySym.u: (1, -1),
    tcod.event.KeySym.b: (-1, 1),
    tcod.event.KeySym.n: (1, 1),
    # Numeric Keypad
    tcod.event.KeySym.KP_8: (0, -1),
    tcod.event.KeySym.KP_2: (0, 1),
    tcod.event.KeySym.KP_4: (-1, 0),
    tcod.event.KeySym.KP_6: (1, 0),
    tcod.event.KeySym.KP_7: (-1, -1),
    tcod.event.KeySym.KP_9: (1, -1),
    tcod.event.KeySym.KP_1: (-1, 1),
    tcod.event.KeySym.KP_3: (1, 1),
    # Arrow Keys
    tcod.event.KeySym.UP: (0, -1),
    tcod.event.KeySym.DOWN: (0, 1),
    tcod.event.KeySym.LEFT: (-1, 0),
    tcod.event.KeySym.RIGHT: (1, 0),
    tcod.event.KeySym.HOME: (-1, -1),
    tcod.event.KeySym.END: (-1, 1),
    tcod.event.KeySym.PAGEUP: (1, -1),
    tcod.event.KeySym.PAGEDOWN: (1, 1),
}

COMMAND_KEYS = {
    tcod.event.KeySym.KP_5: Command.WAIT,
    tcod.event.KeySym.PERIOD: Command.WAIT,

    tcod.event.KeySym.m: Command.MESSAGES,
    tcod.event.KeySym.i: Command.INVENTORY,
    tcod.event.KeySym.d: Command.DROP,
    tcod.event.KeySym.q: Command.QUAFF,
    tcod.event.KeySym.r: Command.READ,
    tcod.event.KeySym.w: Command.WIELD,

    tcod.event.KeySym.SLASH: Command.LOOK,
    tcod.event.KeySym.KP_DIVIDE: Command.LOOK,
}

CONTINUE_KEYS = {
    tcod.event.KeySym.SPACE,
}

CANCEL_KEYS = {
    tcod.event.KeySym.ESCAPE,
}

SHIFTED_COMMAND_KEYS = {
    tcod.event.KeySym.w: Command.WEAR,
    tcod.event.KeySym.t: Command.TAKEOFF,

    tcod.event.KeySym.PERIOD: Command.STAIRS,
    tcod.event.KeySym.SLASH: Command.HELP,
}


def handle_play_event(event: tcod.event.Event) -> MoveCommand | Command | None:
    if isinstance(event, tcod.event.KeyDown):
        if event.mod & tcod.event.KMOD_SHIFT and event.sym in SHIFTED_COMMAND_KEYS:
            command = SHIFTED_COMMAND_KEYS[event.sym]
            return command
        if event.sym in MOVE_KEYS:
            dx, dy = MOVE_KEYS[event.sym]
            return MoveCommand(dx, dy)
        elif event.sym in COMMAND_KEYS:
            command = COMMAND_KEYS[event.sym]
            return command
    return None


def is_continue(event: tcod.event.Event) -> bool:
    return isinstance(event, tcod.event.KeyDown) and event.sym in CONTINUE_KEYS


def is_cancel(event: tcod.event.Event) -> bool:
    return isinstance(event, tcod.event.KeyDown) and event.sym in CANCEL_KEYS


def to_index(event: tcod.event.Event, *, min_l: int = ord('a'), max_l: int = ord('z')) -> int | None:
    if isinstance(event, tcod.event.KeyDown):
        if min_l <= event.sym <= max_l:
            return event.sym - min_l
    return None
