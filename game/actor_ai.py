from __future__ import annotations

import logging

from game.action import Action, MeleeAction, MoveAction, WaitAction
from game.constants import Tile
from game.dice import percent
from game.entity import Actor
from game.level import Level

logger = logging.getLogger(__name__)


class ActorAI:
    def take_turn(self, actor: Actor, level: Level, player: Actor) -> Action:
        raise NotImplementedError()

    def attacked(self, actor: Actor, level: Level) -> None:
        pass


# do not attack unless provoked
class IdleAI(ActorAI):
    def take_turn(self, actor: Actor, level: Level, player: Actor) -> Action:
        return WaitAction()

    def attacked(self, actor: Actor, level: Level) -> None:
        logger.debug("The %s turns hostile.", actor.name)
        actor.ai = HostileAI()


# may turn hostile if the player is visible
class MeanAI(ActorAI):
    def take_turn(self, actor: Actor, level: Level, player: Actor) -> Action:
        if level.visible[actor.x, actor.y]:
            if percent(20):
                logger.debug("The %s turns hostile.", actor.name)
                actor.ai = HostileAI()
        return WaitAction()

    def attacked(self, actor: Actor, level: Level) -> None:
        logger.debug("The %s turns hostile.", actor.name)
        actor.ai = HostileAI()


# chase and attack the player
class HostileAI(ActorAI):
    @staticmethod
    def _distance(x1: int, y1: int, x2: int, y2: int) -> int:
        return (x1 - x2) ** 2 + (y1 - y2) ** 2

    @staticmethod
    def _find_nearest_door(goal_x: int, goal_y: int, level: Level,
                           x1: int, y1: int, x2: int, y2: int) -> tuple[int, int] | None:
        door = None
        distance = HostileAI._distance(0, 0, level.width, level.height)
        for i in range(x1, x2 + 1):
            for j in range(y1, y2 + 1):
                if level.tiles[i, j] == Tile.DOOR:
                    new_dist = HostileAI._distance(i, j, goal_x, goal_y)
                    if new_dist < distance:
                        door = (i, j)
                        distance = new_dist
        return door

    @staticmethod
    def _approach(actor: Actor, goal_x: int, goal_y: int, level: Level) -> Action:
        dest_x, dest_y = actor.x, actor.y
        distance = HostileAI._distance(actor.x, actor.y, goal_x, goal_y)
        for i in range(actor.x - 1, actor.x + 2):
            for j in range(actor.y - 1, actor.y + 2):
                if (level.in_bounds(i, j) and level.is_walkable(i, j)
                        and level.is_connected(actor.x, actor.y, i, j)
                        and not level.get_actor_at(i, j)):
                    new_dist = HostileAI._distance(i, j, goal_x, goal_y)
                    if new_dist < distance:
                        dest_x, dest_y = i, j
                        distance = new_dist
        if (dest_x, dest_y) == (actor.x, actor.y):
            return WaitAction()
        else:
            return MoveAction(dest_x - actor.x, dest_y - actor.y)

    def take_turn(self, actor: Actor, level: Level, player: Actor) -> Action:
        if -1 <= player.x - actor.x <= +1 and -1 <= player.y - actor.y <= +1:
            if level.is_connected(actor.x, actor.y, player.x, player.y):
                return MeleeAction(player)
        for x1, y1, x2, y2 in level.rooms:
            if x1 < actor.x < x2 and y1 < actor.y < y2:
                if not (x1 <= player.x <= x2 and y1 <= player.y <= y2):
                    door = HostileAI._find_nearest_door(player.x, player.y, level, x1, y1, x2, y2)
                    if door:
                        return HostileAI._approach(actor, door[0], door[1], level)
        return HostileAI._approach(actor, player.x, player.y, level)
