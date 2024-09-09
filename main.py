#!/usr/bin/env python3
from __future__ import annotations

import logging
from pathlib import Path
from typing import Never

ASSETS = Path('assets')
SAVEFILE = Path('yarc.sav')


def main() -> Never:
    if __debug__:
        logging.basicConfig(level=logging.DEBUG)
    # Delay importing the version module until after logging is configured.
    from game.version import version_string
    print(f"Y.A.R.C. version {version_string.lstrip('v')}")
    # Import game modules after basic initialization.
    from game.main_menu import show_menu
    install_dir = Path(__file__).parent
    show_menu(install_dir / ASSETS, SAVEFILE)


if __name__ == '__main__':
    main()
