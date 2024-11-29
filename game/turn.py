from __future__ import annotations

from game.dice import roll
from game.entity import Player
from game.level import Level
from game.messages import MessageLog


def wake_up_room(room: tuple[int, int, int, int] | None, level: Level) -> None:
    assert room is not None
    x1, y1, x2, y2 = room
    actors_in_room = {actor for actor in level.actors if actor.ai and x1 <= actor.x <= x2 and y1 <= actor.y <= y2}
    for actor in actors_in_room:
        assert actor.ai is not None
        actor.ai.on_disturbed(actor, level)


def end_turn(player: Player, level: Level, log: MessageLog) -> None:
    level.update_fov(player.x, player.y)
    _heal_player(player)
    _hunger_clock(player, log)
    for actor in level.actors:
        if actor.ai:
            if player.stats.hp == 0:
                break
            actor.ai.take_turn(actor, level, player).perform(actor, level, log)
            if actor.x - 1 <= player.x <= actor.x + 1 and actor.y - 1 <= player.y <= actor.y + 1:
                actor.ai.on_disturbed(actor, level)


def _heal_player(player: Player) -> None:
    player.heal_counter += 1
    hp_gain = 0
    if player.stats.hd <= 7:
        if player.heal_counter >= 21 - player.stats.hd * 2:
            hp_gain = 1
    else:
        if player.heal_counter >= 3:
            hp_gain = roll(1, player.stats.hd - 7)
    if hp_gain > 0:
        player.stats.hp = min(player.stats.hp + hp_gain, player.stats.max_hp)
        player.heal_counter = 0


def _hunger_clock(player: Player, log: MessageLog) -> None:
    prev_value = player.hunger_clock
    player.hunger_clock -= 1
    if player.hunger_clock < -850:
        player.stats.hp = 0
        player.cause_of_death = "starvation"
    elif player.hunger_clock < 0 <= prev_value:
        log.append("You feel too weak from lack of food. You faint.")
    elif player.hunger_clock < 150 <= prev_value:
        log.append("You are starting to feel weak.")
    elif player.hunger_clock < 300 <= prev_value:
        log.append("You are starting to get hungry.")
