import pytest

import game.monsters


@pytest.mark.skip(reason="Enable to dump the full table.")
def test_dump_weights():
    print()
    for d in range(1, 33):
        weights = game.monsters._weights(d)
        print("  ".join(f"{item:2d}" for item in weights))


def test_level_1():
    weights = game.monsters._weights(1)
    assert weights == [20] * 5 + [0] * 21


def test_level_2_to_5():
    for d in range(2, 6):
        weights = game.monsters._weights(d)
        assert weights == [22 - 2 * d] * 5 + [10] * (d - 1) + [0] * (22 - d)


def test_level_6():
    weights = game.monsters._weights(6)
    assert weights == [10] * 10 + [0] * 16


def test_level_7_to_21():
    for d in range(7, 22):
        weights = game.monsters._weights(d)
        assert weights == [0] * (d - 6) + [10] * 10 + [0] * (22 - d)


def test_level_22():
    weights = game.monsters._weights(22)
    assert weights == [0] * 16 + [10] * 10


def test_level_23_to_26():
    for d in range(23, 27):
        weights = game.monsters._weights(d)
        assert weights == [0] * (d - 6) + [10] * (27 - d) + [2 * d - 34] * 5


def test_level_27():
    weights = game.monsters._weights(27)
    assert weights == [0] * 21 + [20] * 5


def test_level_28_to_31():
    for d in range(28, 32):
        weights = game.monsters._weights(d)
        assert weights == [0] * 21 + [2 * d - 44] * (d - 27) + [2 * d - 34] * (32 - d)


def test_level_32():
    weights = game.monsters._weights(32)
    assert weights == [0] * 21 + [20] * 5


def test_level_33_and_beyond():
    for d in range(33, 100):
        weights = game.monsters._weights(d)
        assert weights == [0] * 21 + [20] * 5
