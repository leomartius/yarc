from __future__ import annotations

import logging
import random

from game.constants import Glyph, Tile
from game.entity import ArmorItem, Item, WeaponItem
from game.items import get_item_categories
from game.level import Level
from game.monsters import get_monster_types

# hardcoded 80x22 subdivision
H_GRID = [0, 26, 27, 53, 54, 80]
V_GRID = [0, 7, 8, 14, 15, 22]

# minimum room size is 4x4
MIN_ROOM_WIDTH = 4
MIN_ROOM_HEIGHT = 4

logger = logging.getLogger(__name__)

rng = random.Random()


# a cell in the 3x3 map grid
class Cell:
    def __init__(self, index: int):
        assert 0 <= index < 9
        self.index = index

    @property
    def grid_i(self) -> int:
        return self.index % 3

    @property
    def grid_j(self) -> int:
        return self.index // 3

    @property
    def x1(self) -> int:
        return H_GRID[self.grid_i * 2]

    @property
    def y1(self) -> int:
        return V_GRID[self.grid_j * 2]

    @property
    def width(self) -> int:
        return H_GRID[self.grid_i * 2 + 1] - self.x1

    @property
    def height(self) -> int:
        return V_GRID[self.grid_j * 2 + 1] - self.y1

    @property
    def x2(self) -> int:
        return H_GRID[self.grid_i * 2 + 1] - 1

    @property
    def y2(self) -> int:
        return V_GRID[self.grid_j * 2 + 1] - 1

    def is_neighbour(self, other: Cell) -> bool:
        if self.grid_i == other.grid_i:
            return other.grid_j == self.grid_j - 1 or other.grid_j == self.grid_j + 1
        elif self.grid_j == other.grid_j:
            return other.grid_i == self.grid_i - 1 or other.grid_i == self.grid_i + 1
        return False

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Cell):
            return NotImplemented
        return self.index == other.index


class Room:
    def __init__(self, x1: int, y1: int, width: int, height: int, cell: Cell):
        assert width >= MIN_ROOM_WIDTH and height >= MIN_ROOM_HEIGHT
        self.x1, self.y1 = x1, y1
        self.width, self.height = width, height
        self.cell = cell

    @property
    def x2(self) -> int:
        return self.x1 + self.width - 1

    @property
    def y2(self) -> int:
        return self.y1 + self.height - 1

    @property
    def inner_slice(self) -> tuple[slice, slice]:
        return slice(self.x1 + 1, self.x1 + self.width - 1), slice(self.y1 + 1, self.y1 + self.height - 1)


class Junction:
    def __init__(self, x: int, y: int, cell: Cell):
        self.x, self.y = x, y
        self.cell = cell


def line_slice(x1: int, y1: int, x2: int, y2: int) -> tuple[slice, slice]:
    assert x1 == x2 or y1 == y2
    if x1 > x2:
        x1, x2 = x2, x1
    if y1 > y2:
        y1, y2 = y2, y1
    return slice(x1, x2 + 1), slice(y1, y2 + 1)


def make_room(cell: Cell, level: Level) -> Room:
    room_width = rng.randint(MIN_ROOM_WIDTH, cell.width)
    room_x1 = rng.randint(cell.x1, cell.x1 + (cell.width - room_width))
    room_height = rng.randint(MIN_ROOM_HEIGHT, cell.height)
    room_y1 = rng.randint(cell.y1, cell.y1 + (cell.height - room_height))
    room = Room(room_x1, room_y1, room_width, room_height, cell)
    level.tiles[line_slice(room.x1, room.y1, room.x1, room.y2)] = Tile.V_WALL
    level.tiles[line_slice(room.x2, room.y1, room.x2, room.y2)] = Tile.V_WALL
    level.tiles[line_slice(room.x1, room.y1, room.x2, room.y1)] = Tile.H_WALL
    level.tiles[line_slice(room.x1, room.y2, room.x2, room.y2)] = Tile.H_WALL
    level.tiles[room.inner_slice] = Tile.FLOOR
    level.tiles[room.x1, room.y1] = Tile.TL_CORNER
    level.tiles[room.x2, room.y1] = Tile.TR_CORNER
    level.tiles[room.x1, room.y2] = Tile.BL_CORNER
    level.tiles[room.x2, room.y2] = Tile.BR_CORNER
    level.rooms.append((room.x1, room.y1, room.x2, room.y2))
    return room


def make_junction(cell: Cell, level: Level) -> Junction:
    x = rng.randint(cell.x1, cell.x2)
    y = rng.randint(cell.y1, cell.y2)
    level.tiles[x, y] = Tile.PASSAGE
    return Junction(x, y, cell)


def make_passage(room1: Room | Junction, room2: Room | Junction, level: Level) -> None:
    assert room1.cell != room2.cell
    assert room1.cell.is_neighbour(room2.cell)
    if room1.cell.grid_j == room2.cell.grid_j:
        # make horizontal passage
        if room1.cell.grid_i > room2.cell.grid_i:
            room1, room2 = room2, room1
        if isinstance(room1, Room):
            x1, y1 = room1.x2, rng.randint(room1.y1 + 1, room1.y2 - 1)
        else:
            x1, y1 = room1.x, room1.y
        if isinstance(room2, Room):
            x2, y2 = room2.x1, rng.randint(room2.y1 + 1, room2.y2 - 1)
        else:
            x2, y2 = room2.x, room2.y
        assert x2 - x1 > 1
        xm = rng.randint(x1 + 1, x2 - 1)
        level.tiles[line_slice(x1, y1, xm, y1)] = Tile.PASSAGE
        level.tiles[line_slice(xm, y1, xm, y2)] = Tile.PASSAGE
        level.tiles[line_slice(xm, y2, x2, y2)] = Tile.PASSAGE
        if isinstance(room1, Room):
            level.tiles[x1, y1] = Tile.DOOR
        if isinstance(room2, Room):
            level.tiles[x2, y2] = Tile.DOOR
    else:
        assert room1.cell.grid_i == room2.cell.grid_i
        # make vertical passage
        if room1.cell.grid_j > room2.cell.grid_j:
            room1, room2 = room2, room1
        if isinstance(room1, Room):
            x1, y1 = rng.randint(room1.x1 + 1, room1.x2 - 1), room1.y2
        else:
            x1, y1 = room1.x, room1.y
        if isinstance(room2, Room):
            x2, y2 = rng.randint(room2.x1 + 1, room2.x2 - 1), room2.y1
        else:
            x2, y2 = room2.x, room2.y
        assert y2 - y1 > 1
        ym = rng.randint(y1 + 1, y2 - 1)
        level.tiles[line_slice(x1, y1, x1, ym)] = Tile.PASSAGE
        level.tiles[line_slice(x1, ym, x2, ym)] = Tile.PASSAGE
        level.tiles[line_slice(x2, ym, x2, y2)] = Tile.PASSAGE
        if isinstance(room1, Room):
            level.tiles[x1, y1] = Tile.DOOR
        if isinstance(room2, Room):
            level.tiles[x2, y2] = Tile.DOOR


def connect_rooms(all_rooms: list[Room | Junction], level: Level) -> None:
    passages = []
    # ensure all rooms/junctions are connected
    connected = [rng.choice(all_rooms)]
    unconnected = [room for room in all_rooms if room not in connected]
    while unconnected:
        curr = rng.choice(connected)
        neighbours = [room for room in unconnected if room.cell.is_neighbour(curr.cell)]
        if neighbours:
            dest = rng.choice(neighbours)
            connected.append(dest)
            unconnected.remove(dest)
            make_passage(curr, dest, level)
            passages += [(curr, dest), (dest, curr)]
    # add some random passages
    for _ in range(rng.randrange(5)):
        curr = rng.choice(all_rooms)
        neighbours = [room for room in all_rooms if room.cell.is_neighbour(curr.cell) and (curr, room) not in passages]
        if neighbours:
            dest = rng.choice(neighbours)
            make_passage(curr, dest, level)
            passages += [(curr, dest), (dest, curr)]


def find_empty_spot_in_room(room: Room, level: Level) -> tuple[int, int]:
    if __debug__:
        found = False
        for x in range(room.x1 + 1, room.x1 + room.width - 1):
            for y in range(room.y1 + 1, room.y1 + room.height - 1):
                if not level.get_entities_at(x, y):
                    found = True
        assert found, "No empty coordinates were found in the given room."
    while True:
        x = rng.randint(room.x1 + 1, room.x2 - 1)
        y = rng.randint(room.y1 + 1, room.y2 - 1)
        if not level.get_entities_at(x, y):
            return x, y


def find_empty_spot(all_rooms: list[Room | Junction], level: Level) -> tuple[int, int]:
    rooms = [room for room in all_rooms if isinstance(room, Room)]
    if __debug__:
        found = False
        for room in rooms:
            for x in range(room.x1 + 1, room.x1 + room.width - 1):
                for y in range(room.y1 + 1, room.y1 + room.height - 1):
                    if not level.get_entities_at(x, y):
                        found = True
        assert found, "No empty coordinates were found on the entire map."
    while True:
        room = rng.choice(rooms)
        x = rng.randint(room.x1 + 1, room.x2 - 1)
        y = rng.randint(room.y1 + 1, room.y2 - 1)
        if not level.get_entities_at(x, y):
            return x, y


def place_gold(room: Room, level: Level) -> None:
    x, y = find_empty_spot_in_room(room, level)
    gold = Item(x=x, y=y, glyph=Glyph.GOLD, name='gold', gold=rng.randint(1, 50 + 10 * level.depth) + 1)
    level.entities.add(gold)


def place_monster(room: Room, level: Level) -> None:
    x, y = find_empty_spot_in_room(room, level)
    extra_hd = max(0, level.depth - 26)
    monster_types, weights = get_monster_types(level.depth)
    monster_type = rng.choices(monster_types, weights).pop()
    monster = monster_type.spawn(x, y, extra_hd)
    level.entities.add(monster)


def place_item(all_rooms: list[Room | Junction], level: Level) -> None:
    x, y = find_empty_spot(all_rooms, level)
    categories, weights = get_item_categories()
    category = rng.choices(categories, weights).pop()
    item_types, weights = category.get_item_types()
    item_type = rng.choices(item_types, weights).pop()
    item = item_type.spawn(x, y)
    if isinstance(item, ArmorItem):
        r = rng.random()
        if r < 0.20:
            item.cursed = True
            item.armor.plus_ac = -rng.randint(1, 3)
        elif r < 0.28:
            item.armor.plus_ac = +rng.randint(1, 3)
    elif isinstance(item, WeaponItem):
        r = rng.random()
        if r < 0.10:
            item.cursed = True
            item.weapon.plus_hit = -rng.randint(1, 3)
        elif r < 0.15:
            item.weapon.plus_hit = +rng.randint(1, 3)
    level.entities.add(item)


def generate_level(map_width: int, map_height: int, depth: int) -> Level:
    assert map_width == 80 and map_height == 22
    level = Level(map_width, map_height, depth)

    seed = random.SystemRandom().getrandbits(64)
    rng.seed(seed)
    logger.info("Level seed is 0x%08X", seed)

    junction_indices = rng.choices(range(9), k=rng.randrange(4))
    rooms: list[Room | Junction] = []
    for i in range(9):
        cell = Cell(i)
        if i in junction_indices:
            rooms.append(make_junction(cell, level))
        else:
            rooms.append(make_room(cell, level))

    connect_rooms(rooms, level)

    for room in rooms:
        if isinstance(room, Room):
            monster_chance = .25
            if rng.random() < .5:
                place_gold(room, level)
                monster_chance = .8
            if rng.random() < monster_chance:
                place_monster(room, level)

    for _ in range(9):
        if rng.random() < .35:
            place_item(rooms, level)

    level.stairs_x, level.stairs_y = find_empty_spot(rooms, level)
    level.tiles[level.stairs_x, level.stairs_y] = Tile.STAIRS
    do_not_place_here = Item(x=level.stairs_x, y=level.stairs_y, glyph=Glyph.INVALID, name='do_not_place_here')
    level.entities.add(do_not_place_here)

    level.entry_x, level.entry_y = find_empty_spot(rooms, level)
    level.entities.remove(do_not_place_here)

    return level
