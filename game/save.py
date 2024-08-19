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
    signature: str


SIGNATURE = 'YARC:0.1.0'


def save_game(filename: Path, player: Player, level: Level, log: MessageLog) -> None:
    savefile = SaveFile(player, level, log, SIGNATURE)
    content = lzma.compress(pickle.dumps(savefile))
    filename.write_bytes(content)
    logger.info("Savegame saved successfully: %s.", filename)


def load_game(filename: Path) -> tuple[Player, Level, MessageLog] | None:
    try:
        content = filename.read_bytes()
        savefile = pickle.loads(lzma.decompress(content))
    except FileNotFoundError:
        logger.debug("Savegame file not found: %s.", filename)
        return None
    if isinstance(savefile, SaveFile):
        if savefile.signature == SIGNATURE:
            logger.info("Savegame loaded successfully: %s.", filename)
            filename.unlink()
            return savefile.player, savefile.level, savefile.log
    logger.debug("Incompatible savegame file: %s.", filename)
    return None
