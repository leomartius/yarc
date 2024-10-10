from __future__ import annotations

import logging
import random

from game.action import Action, MeleeAction, MoveAction, WaitAction
from game.constants import Tile
from game.dice import roll
from game.entity import Actor, Player
from game.level import Level

logger = logging.getLogger(__name__)


def aggravate(actor: Actor) -> None:
    assert not isinstance(actor, Player)
    if not isinstance(actor.ai, HostileAI):
        logger.debug("The %s turns hostile.", actor.name)
        actor.ai = HostileAI()


def pacify(actor: Actor) -> None:
    assert not isinstance(actor, Player)
    if not isinstance(actor.ai, IdleAI):
        logger.debug("The %s turns idle.", actor.name)
        actor.ai = IdleAI()


class ActorAI:
    def take_turn(self, actor: Actor, level: Level, player: Actor) -> Action:
        raise NotImplementedError()

    def on_attacked(self, actor: Actor) -> None:
        aggravate(actor)

    def on_disturbed(self, actor: Actor) -> None:
        pass

    def is_helpless(self) -> bool:
        raise NotImplementedError()


# do nothing unless attacked
class IdleAI(ActorAI):
    def take_turn(self, actor: Actor, level: Level, player: Actor) -> Action:
        return WaitAction()

    def is_helpless(self) -> bool:
        return True


# possibly turn hostile if disturbed
class MeanAI(ActorAI):
    def take_turn(self, actor: Actor, level: Level, player: Actor) -> Action:
        return WaitAction()

    def on_disturbed(self, actor: Actor) -> None:
        if roll(1, d=3) > 1:
            aggravate(actor)

    def is_helpless(self) -> bool:
        return True


# chase and attack the player
class HostileAI(ActorAI):
    @staticmethod
    def _find_nearest_door(goal_x: int, goal_y: int, level: Level,
                           x1: int, y1: int, x2: int, y2: int) -> tuple[int, int] | None:
        door = None
        distance = _distance(0, 0, level.width, level.height)
        for i in range(x1, x2 + 1):
            for j in range(y1, y2 + 1):
                if level.tiles[i, j] == Tile.DOOR:
                    new_dist = _distance(i, j, goal_x, goal_y)
                    if new_dist < distance:
                        door = (i, j)
                        distance = new_dist
        return door

    def take_turn(self, actor: Actor, level: Level, player: Actor) -> Action:
        if -1 <= player.x - actor.x <= +1 and -1 <= player.y - actor.y <= +1:
            if level.is_connected(actor.x, actor.y, player.x, player.y):
                return MeleeAction(player)
        for x1, y1, x2, y2 in level.rooms:
            if x1 < actor.x < x2 and y1 < actor.y < y2:
                if not (x1 <= player.x <= x2 and y1 <= player.y <= y2):
                    door = HostileAI._find_nearest_door(player.x, player.y, level, x1, y1, x2, y2)
                    if door:
                        return _approach(actor, door[0], door[1], level)
        return _approach(actor, player.x, player.y, level)

    def is_helpless(self) -> bool:
        return False


# Euclidean square distance
def _distance(x1: int, y1: int, x2: int, y2: int) -> int:
    return (x1 - x2) ** 2 + (y1 - y2) ** 2


# Move to the nearby cell that minimizes the Euclidean distance.
def _approach(actor: Actor, goal_x: int, goal_y: int, level: Level) -> Action:
    destinations = [(actor.x, actor.y)]
    distance = _distance(actor.x, actor.y, goal_x, goal_y)
    for i in range(actor.x - 1, actor.x + 2):
        for j in range(actor.y - 1, actor.y + 2):
            if (
                level.in_bounds(i, j)
                and level.is_walkable(i, j)
                and level.is_connected(actor.x, actor.y, i, j)
                and not level.get_actor_at(i, j)
            ):
                new_dist = _distance(i, j, goal_x, goal_y)
                if new_dist < distance:
                    destinations = [(i, j)]
                    distance = new_dist
                elif new_dist == distance:
                    destinations += [(i, j)]
    if (actor.x, actor.y) in destinations:
        return WaitAction()
    else:
        dest_x, dest_y = random.choice(destinations)
        return MoveAction(dest_x - actor.x, dest_y - actor.y)
