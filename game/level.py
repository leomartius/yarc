from __future__ import annotations

import numpy as np

from game.constants import Tile
from game.entity import Actor, Entity, Item


class Level:
    def __init__(self, width: int, height: int, depth: int):
        self.width, self.height = width, height
        self.depth = depth
        self.tiles = np.zeros((width, height), dtype=np.uint8, order='F')
        self.visible = np.zeros((width, height), dtype=bool, order='F')
        self.explored = np.zeros((width, height), dtype=bool, order='F')
        self.rooms: list[tuple[int, int, int, int]] = []
        self.entities: set[Entity] = set()
        self.entry_x, self.entry_y = 0, 0
        self.stairs_x, self.stairs_y = 0, 0
        self.completed = False

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def is_walkable(self, x: int, y: int) -> bool:
        assert self.in_bounds(x, y)
        return bool(self.tiles[x, y] >= Tile.MIN_WALKABLE)

    def is_connected(self, x1: int, y1: int, x2: int, y2: int) -> bool:
        assert self.in_bounds(x1, y1) and self.in_bounds(x2, y2)
        assert self.is_walkable(x1, y1) and self.is_walkable(x2, y2)
        assert -1 <= x2 - x1 <= +1 and -1 <= y2 - y1 <= +1
        if x2 == x1 or y2 == y1:
            return True
        else:
            # when moving diagonally, you can't cut corners
            return self.is_walkable(x1, y2) and self.is_walkable(x2, y1)

    @property
    def actors(self) -> set[Actor]:
        return {entity for entity in self.entities if isinstance(entity, Actor)}

    def get_entities_at(self, x: int, y: int) -> set[Entity]:
        assert self.in_bounds(x, y)
        return {entity for entity in self.entities if entity.x == x and entity.y == y}

    def get_actor_at(self, x: int, y: int) -> Actor | None:
        assert self.in_bounds(x, y)
        actors_at_xy = {entity for entity in self.get_entities_at(x, y) if isinstance(entity, Actor)}
        assert len(actors_at_xy) <= 1
        return actors_at_xy.pop() if actors_at_xy else None

    def get_item_at(self, x: int, y: int) -> Item | None:
        assert self.in_bounds(x, y)
        items_at_xy = {entity for entity in self.get_entities_at(x, y) if isinstance(entity, Item)}
        assert len(items_at_xy) <= 1
        return items_at_xy.pop() if items_at_xy else None

    def get_room_at(self, x: int, y: int) -> tuple[int, int, int, int] | None:
        assert self.in_bounds(x, y)
        for x1, y1, x2, y2 in self.rooms:
            if x1 <= x <= x2 and y1 <= y <= y2:
                return x1, y1, x2, y2
        return None

    def update_fov(self, x: int, y: int) -> None:
        self.visible[:] = False

        for i in range(x - 1, x + 2):
            for j in range(y - 1, y + 2):
                if self.in_bounds(i, j):
                    if self.tiles[x, y] != Tile.PASSAGE:
                        self.visible[i, j] = self.tiles[i, j] != Tile.ROCK
                    else:
                        self.visible[i, j] = self.tiles[i, j] in (Tile.PASSAGE, Tile.DOOR)

        for x1, y1, x2, y2 in self.rooms:
            if x1 <= x <= x2 and y1 <= y <= y2:
                self.visible[x1:x2 + 1, y1:y2 + 1] = True

        self.explored |= self.visible
