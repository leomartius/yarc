import pytest

import game.messages

MAX_LEN = 10
MESSAGE = 'a message'
ALL = MAX_LEN + 1


@pytest.fixture
def empty_log():
    return game.messages.MessageLog(max_size=MAX_LEN)


@pytest.fixture
def half_log(empty_log):
    for i in range(MAX_LEN // 2):
        empty_log.append(f'{i + 1}')
    return empty_log


@pytest.fixture
def full_log(empty_log):
    for i in range(MAX_LEN):
        empty_log.append(f'{i + 1}')
    return empty_log


@pytest.fixture
def read_log(full_log):
    full_log.get_unread(ALL)
    return full_log


def test_append_empty(empty_log):
    empty_log.append(MESSAGE)
    assert empty_log.unread == 1
    assert empty_log.get_latest(ALL) == [MESSAGE]
    assert empty_log.get_unread(ALL) == [MESSAGE]


def test_append_half(half_log):
    half_log.append(MESSAGE)
    assert half_log.unread == MAX_LEN // 2 + 1
    assert half_log.get_latest(ALL) == [f'{i}' for i in range(1, MAX_LEN // 2 + 1)] + [MESSAGE]
    assert half_log.get_unread(ALL) == [f'{i}' for i in range(1, MAX_LEN // 2 + 1)] + [MESSAGE]


def test_append_full(full_log):
    full_log.append(MESSAGE)
    assert full_log.unread == MAX_LEN
    assert full_log.get_latest(ALL) == [f'{i}' for i in range(2, MAX_LEN + 1)] + [MESSAGE]
    assert full_log.get_unread(ALL) == [f'{i}' for i in range(2, MAX_LEN + 1)] + [MESSAGE]


def test_append_read(read_log):
    read_log.append(MESSAGE)
    assert read_log.unread == 1
    assert read_log.get_latest(ALL) == [f'{i}' for i in range(2, MAX_LEN + 1)] + [MESSAGE]
    assert read_log.get_unread(ALL) == [MESSAGE]


def test_get_latest_empty(empty_log):
    assert empty_log.get_latest(1) == []
    assert empty_log.get_latest(2) == []
    assert empty_log.get_latest(MAX_LEN) == []


def test_get_latest_half(half_log):
    assert half_log.get_latest(1) == [f'{MAX_LEN // 2}']
    assert half_log.get_latest(2) == [f'{MAX_LEN // 2 - 1}', f'{MAX_LEN // 2}']
    assert half_log.get_latest(MAX_LEN // 2) == [f'{i}' for i in range(1, MAX_LEN // 2 + 1)]
    assert half_log.get_latest(MAX_LEN // 2 + 1) == [f'{i}' for i in range(1, MAX_LEN // 2 + 1)]


def test_get_latest_full(full_log):
    assert full_log.get_latest(1) == [f'{MAX_LEN}']
    assert full_log.get_latest(2) == [f'{MAX_LEN - 1}', f'{MAX_LEN}']
    assert full_log.get_latest(MAX_LEN // 2) == [f'{i}' for i in range(MAX_LEN // 2 + 1, MAX_LEN + 1)]
    assert full_log.get_latest(MAX_LEN) == [f'{i}' for i in range(1, MAX_LEN + 1)]
    assert full_log.get_latest(MAX_LEN + 1) == [f'{i}' for i in range(1, MAX_LEN + 1)]


def test_unread_empty(empty_log):
    assert empty_log.unread == 0


def test_unread_half(half_log):
    assert half_log.unread == MAX_LEN // 2


def test_unread_full(full_log):
    assert full_log.unread == MAX_LEN


def test_unread_read(read_log):
    assert read_log.unread == 0


def test_get_unread_empty(empty_log):
    assert empty_log.get_unread(1) == []
    assert empty_log.get_unread(2) == []
    assert empty_log.get_unread(MAX_LEN) == []


def test_get_unread_half(half_log):
    assert half_log.get_unread(1) == [f'{1}']
    assert half_log.get_unread(2) == [f'{2}', f'{3}']
    assert half_log.get_unread(ALL) == [f'{i}' for i in range(4, MAX_LEN // 2 + 1)]


def test_get_unread_full(full_log):
    assert full_log.get_unread(1) == [f'{1}']
    assert full_log.get_unread(2) == [f'{2}', f'{3}']
    assert full_log.get_unread(ALL) == [f'{i}' for i in range(4, MAX_LEN + 1)]


def test_get_unread_read(read_log):
    assert read_log.get_unread(1) == []
    assert read_log.get_unread(2) == []
    assert read_log.get_unread(MAX_LEN) == []
