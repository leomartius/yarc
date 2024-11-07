from __future__ import annotations

import logging
import random

import numpy as np

from game.action import Action, BumpAction, WaitAction
from game.constants import Tile
from game.dice import roll
from game.entity import Actor, Item, Player
from game.level import Level
from game.pathfinding import find_path

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

    def on_disturbed(self, actor: Actor, level: Level) -> None:
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

    def on_disturbed(self, actor: Actor, level: Level) -> None:
        if roll(1, d=3) > 1:
            aggravate(actor)

    def is_helpless(self) -> bool:
        return True


# run towards gold if possible
class GreedyAI(ActorAI):
    goal: Item | None = None

    def take_turn(self, actor: Actor, level: Level, player: Actor) -> Action:
        if self.goal is None:
            return WaitAction()
        elif self.goal not in level.entities:
            aggravate(actor)
            assert actor.ai
            return actor.ai.take_turn(actor, level, player)
        else:
            assert (actor.x, actor.y) != (self.goal.x, self.goal.y)
            action = _approach(actor, self.goal.x, self.goal.y, level)
            if isinstance(action, BumpAction):
                assert not actor.erratic
                if (actor.x + action.dx, actor.y + action.dy) == (self.goal.x, self.goal.y):
                    pacify(actor)
            return action

    def on_disturbed(self, actor: Actor, level: Level) -> None:
        if self.goal is None:
            room = level.get_room_at(actor.x, actor.y)
            assert room is not None
            x1, y1, x2, y2 = room
            for item in level.items:
                if item.gold and x1 < item.x < x2 and y1 < item.y < y2:
                    logger.debug("The %s starts running toward a pile of gold.", actor.name)
                    self.goal = item
                    return
            else:
                aggravate(actor)

    def is_helpless(self) -> bool:
        return self.goal is None


# chase and attack the player
class HostileAI(ActorAI):
    def take_turn(self, actor: Actor, level: Level, player: Actor) -> Action:
        # attack the player if possible
        if -1 <= player.x - actor.x <= +1 and -1 <= player.y - actor.y <= +1:
            if level.is_connected(actor.x, actor.y, player.x, player.y):
                return BumpAction(player.x - actor.x, player.y - actor.y)
        # move toward the player if in the same room
        if room := level.get_room_at(actor.x, actor.y):
            x1, y1, x2, y2 = room
            if x1 <= player.x <= x2 and y1 <= player.y <= y2:
                return _approach(actor, player.x, player.y, level)
            # if inside a room, move toward the exit door
            if x1 < actor.x < x2 and y1 < actor.y < y2:
                path = _path_to(actor, player.x, player.y, level)
                for x, y in path:
                    if level.tiles[x, y] == Tile.DOOR:
                        door = x, y
                        break
                assert door
                return _approach(actor, door[0], door[1], level)
        # otherwise, find a path to the player
        path = _path_to(actor, player.x, player.y, level)
        assert len(path) > 2
        dest = path[2]
        return _approach(actor, dest[0], dest[1], level)

    def is_helpless(self) -> bool:
        return False


# Euclidean square distance
def _distance(x1: int, y1: int, x2: int, y2: int) -> int:
    return (x1 - x2) ** 2 + (y1 - y2) ** 2


# Move toward the destination using a greedy best-first algorithm.
# Find the nearby cell that minimizes the Euclidean distance to the goal.
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
        return BumpAction(dest_x - actor.x, dest_y - actor.y)


# Find a path to the destination using the A* algorithm.
# The algorithm is configured to be consistent with the movement rules.
# Return the whole sequence of steps.
def _path_to(actor: Actor, goal_x: int, goal_y: int, level: Level) -> list[tuple[int, int]]:
    cost = level.walkable.astype(np.int8)
    return find_path((actor.x, actor.y), (goal_x, goal_y), cost)
