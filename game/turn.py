from __future__ import annotations

from game.entity import Player
from game.level import Level
from game.messages import MessageLog


def end_turn(player: Player, level: Level, log: MessageLog) -> None:
    level.update_fov(player.x, player.y)
    for actor in level.actors:
        if actor.ai:
            if player.stats.hp == 0:
                break
            actor.ai.take_turn(actor, level, player).perform(actor, level, log)
