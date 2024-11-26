from __future__ import annotations

import logging
import lzma
import pickle
from dataclasses import dataclass
from pathlib import Path

from game.entity import Player
from game.level import Level
from game.messages import MessageLog

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class SaveFile:
    player: Player
    level: Level
    log: MessageLog


def save_game(filename: Path, player: Player, level: Level, log: MessageLog) -> None:
    savefile = SaveFile(player, level, log)
    _save(filename, savefile)
    logger.info("Savegame saved successfully: '%s'", filename)


def load_game(filename: Path) -> tuple[Player, Level, MessageLog] | None:
    savefile = _load(filename)
    if savefile:
        logger.info("Savegame loaded successfully: '%s'", filename)
        filename.unlink()
        return savefile.player, savefile.level, savefile.log
    return None


HEADER = b'YARC\0\2\0\2'
assert len(HEADER) == 8


def _save(filename: Path, savefile: SaveFile) -> None:
    serialized = pickle.dumps(savefile)
    compressed = lzma.compress(serialized)
    with filename.open('wb') as f:
        f.write(HEADER)
        f.write(compressed)


def _load(filename: Path) -> SaveFile | None:
    try:
        with filename.open('rb') as f:
            header = f.read(len(HEADER))
            if header != HEADER:
                logger.debug("Incompatible savegame file: '%s' (wrong header)", filename)
                return None
            content = f.read()
    except FileNotFoundError:
        logger.debug("Savegame file not found: '%s'", filename)
        return None
    except OSError as e:
        logger.warning("Unable to open file: '%s'", filename, exc_info=e)
        return None
    try:
        savefile = pickle.loads(lzma.decompress(content))
        assert isinstance(savefile, SaveFile)
        return savefile
    except Exception as e:
        logger.error("Incompatible savegame file: '%s'", filename, exc_info=e)
        return None
