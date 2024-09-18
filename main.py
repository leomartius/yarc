#!/usr/bin/env python3
from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Any, Never

ASSETS = Path('assets')
SAVEFILE = Path('yarc.sav')


def parse_command_line() -> dict[str, Any]:
    parser = argparse.ArgumentParser(description="Yet Another Rogue Clone")
    parser.add_argument(
        '--log',
        metavar='LEVEL',
        choices=('debug', 'info', 'warning', 'error', 'critical', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'),
        default='DEBUG' if __debug__ else 'WARNING',
        dest='loglevel',
        help="set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    parser.add_argument(
        '--theme',
        metavar='THEME',
        choices=('default',),
        default='default',
        help="choose a graphical theme",
    )
    parser.add_argument('-v', '--version', action='store_true', help="print version number and exit")
    args = parser.parse_args()
    args.loglevel = args.loglevel.upper()
    return vars(args)


def main() -> Never:
    args = parse_command_line()
    logging.basicConfig(level=args['loglevel'])
    # Delay importing the version module until after logging is configured.
    from game.version import version_string
    print(f"Y.A.R.C. version {version_string.lstrip('v')}")
    if args['version']:
        raise SystemExit()
    # Import game modules after basic initialization.
    from game.main_menu import show_menu
    install_dir = Path(__file__).parent
    show_menu(install_dir / ASSETS, SAVEFILE, args['theme'])


if __name__ == '__main__':
    main()
