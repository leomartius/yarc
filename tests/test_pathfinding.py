import numpy as np
import pytest

import game.pathfinding


@pytest.fixture
def empty():
    return np.array(
        [
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
        ],
        dtype=np.int8,
        order='F',
    )


def test_cardinal_strait_line(empty):
    path = game.pathfinding.find_path((0, 2), (4, 2), empty)
    assert path == [(0, 2), (1, 2), (2, 2), (3, 2), (4, 2)]
    path = game.pathfinding.find_path((4, 2), (0, 2), empty)
    assert path == [(4, 2), (3, 2), (2, 2), (1, 2), (0, 2)]
    path = game.pathfinding.find_path((2, 0), (2, 4), empty)
    assert path == [(2, 0), (2, 1), (2, 2), (2, 3), (2, 4)]
    path = game.pathfinding.find_path((2, 4), (2, 0), empty)
    assert path == [(2, 4), (2, 3), (2, 2), (2, 1), (2, 0)]


def test_diagonal_strait_line(empty):
    path = game.pathfinding.find_path((0, 0), (4, 4), empty)
    assert path == [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]
    path = game.pathfinding.find_path((4, 4), (0, 0), empty)
    assert path == [(4, 4), (3, 3), (2, 2), (1, 1), (0, 0)]
    path = game.pathfinding.find_path((0, 4), (4, 0), empty)
    assert path == [(0, 4), (1, 3), (2, 2), (3, 1), (4, 0)]
    path = game.pathfinding.find_path((4, 0), (0, 4), empty)
    assert path == [(4, 0), (3, 1), (2, 2), (1, 3), (0, 4)]


@pytest.fixture
def room():
    return np.array(
        [
            [0, 1, 0, 0, 0],
            [1, 1, 1, 1, 0],
            [0, 1, 1, 1, 0],
            [0, 1, 1, 1, 1],
            [0, 0, 0, 1, 0],
        ],
        dtype=np.int8,
        order='F',
    )


def test_traverse_room(room):
    path = game.pathfinding.find_path((0, 1), (3, 4), room)
    assert path == [(0, 1), (1, 1), (2, 2), (3, 3), (3, 4)]
    path = game.pathfinding.find_path((3, 4), (0, 1), room)
    assert path == [(3, 4), (3, 3), (2, 2), (1, 1), (0, 1)]
    path = game.pathfinding.find_path((1, 0), (4, 3), room)
    assert path == [(1, 0), (1, 1), (2, 2), (3, 3), (4, 3)]
    path = game.pathfinding.find_path((4, 3), (1, 0), room)
    assert path == [(4, 3), (3, 3), (2, 2), (1, 1), (1, 0)]


@pytest.fixture
def door1():
    return np.array(
        [
            [1, 1, 1],
            [0, 1, 0],
            [1, 1, 1],
        ],
        dtype=np.int8,
        order='F',
    )


def test_vertical_door(door1):
    path = game.pathfinding.find_path((0, 0), (2, 2), door1)
    assert path == [(0, 0), (0, 1), (1, 1), (2, 1), (2, 2)]
    path = game.pathfinding.find_path((2, 2), (0, 0), door1)
    assert path == [(2, 2), (2, 1), (1, 1), (0, 1), (0, 0)]
    path = game.pathfinding.find_path((2, 0), (0, 2), door1)
    assert path == [(2, 0), (2, 1), (1, 1), (0, 1), (0, 2)]
    path = game.pathfinding.find_path((0, 2), (2, 0), door1)
    assert path == [(0, 2), (0, 1), (1, 1), (2, 1), (2, 0)]


@pytest.fixture
def door2():
    return np.array(
        [
            [1, 0, 1],
            [1, 1, 1],
            [1, 0, 1],
        ],
        dtype=np.int8,
        order='F',
    )


def test_horizontal_door(door2):
    path = game.pathfinding.find_path((0, 0), (2, 2), door2)
    assert path == [(0, 0), (1, 0), (1, 1), (1, 2), (2, 2)]
    path = game.pathfinding.find_path((2, 2), (0, 0), door2)
    assert path == [(2, 2), (1, 2), (1, 1), (1, 0), (0, 0)]
    path = game.pathfinding.find_path((2, 0), (0, 2), door2)
    assert path == [(2, 0), (1, 0), (1, 1), (1, 2), (0, 2)]
    path = game.pathfinding.find_path((0, 2), (2, 0), door2)
    assert path == [(0, 2), (1, 2), (1, 1), (1, 0), (2, 0)]


@pytest.fixture
def passage():
    return np.array(
        [
            [0, 1, 0],
            [1, 1, 1],
            [0, 1, 0],
        ],
        dtype=np.int8,
        order='F',
    )


def test_bending_passage(passage):
    path = game.pathfinding.find_path((1, 0), (0, 1), passage)
    assert path == [(1, 0), (1, 1), (0, 1)]
    path = game.pathfinding.find_path((0, 1), (1, 0), passage)
    assert path == [(0, 1), (1, 1), (1, 0)]
    path = game.pathfinding.find_path((1, 0), (2, 1), passage)
    assert path == [(1, 0), (1, 1), (2, 1)]
    path = game.pathfinding.find_path((2, 1), (1, 0), passage)
    assert path == [(2, 1), (1, 1), (1, 0)]
    path = game.pathfinding.find_path((1, 2), (0, 1), passage)
    assert path == [(1, 2), (1, 1), (0, 1)]
    path = game.pathfinding.find_path((0, 1), (1, 2), passage)
    assert path == [(0, 1), (1, 1), (1, 2)]
    path = game.pathfinding.find_path((1, 2), (2, 1), passage)
    assert path == [(1, 2), (1, 1), (2, 1)]
    path = game.pathfinding.find_path((2, 1), (1, 2), passage)
    assert path == [(2, 1), (1, 1), (1, 2)]
