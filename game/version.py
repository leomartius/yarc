# In binary distributions, this module is overwritten by the build script.
from __future__ import annotations

import logging
from subprocess import DEVNULL, PIPE, run

logger = logging.getLogger(__name__)

version_string = "(no version string)"

try:
    git_describe = run(
        ['git', 'describe', '--tags', '--dirty', '--always'],
        check=True,
        text=True,
        stdin=DEVNULL,
        stdout=PIPE,
        stderr=DEVNULL,
    ).stdout
    version_string = git_describe.strip().replace('-', '_')
    logger.debug("Starting from git repository.")
except:  # noqa: E722
    logger.debug("Unable to run git.")
