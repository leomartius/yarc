from __future__ import annotations

from game.entity import Player
from game.level import Level
from game.messages import MessageLog


def wake_up_room(room: tuple[int, int, int, int] | None, level: Level) -> None:
    assert room is not None
    x1, y1, x2, y2 = room
    actors_in_room = {actor for actor in level.actors if actor.ai and x1 <= actor.x <= x2 and y1 <= actor.y <= y2}
    for actor in actors_in_room:
        assert actor.ai is not None
        actor.ai.on_disturbed(actor)


def end_turn(player: Player, level: Level, log: MessageLog) -> None:
    level.update_fov(player.x, player.y)
    for actor in level.actors:
        if actor.ai:
            if player.stats.hp == 0:
                break
            actor.ai.take_turn(actor, level, player).perform(actor, level, log)
            if actor.x - 1 <= player.x <= actor.x + 1 and actor.y - 1 <= player.y <= actor.y + 1:
                actor.ai.on_disturbed(actor)
