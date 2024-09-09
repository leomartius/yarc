#!/usr/bin/env python3
import glob
import logging
import os
import platform
import shutil
from subprocess import DEVNULL, PIPE, run

import PyInstaller.__main__

project_name = 'yarc'
logger = logging.getLogger(__name__)

# get git tag or commit
git_describe = run(['git', 'describe', '--tags', '--dirty', '--always'],
                   check=True, text=True, stdin=DEVNULL, stdout=PIPE, stderr=DEVNULL).stdout
version = git_describe.strip().replace('-', '_')
# copy source tree to build directory and hardcode version string
os.makedirs('build/src/game', exist_ok=True)
shutil.copy('main.py', 'build/src/')
for file in glob.glob('game/*.py'):
    shutil.copy(file, 'build/src/game/')
with open('build/src/game/version.py', 'w') as version_py:
    version_py.write(f"version_string = '{version}'\n")
# run pyinstaller
PyInstaller.__main__.run(['build.spec'])
# copy additional files
shutil.copy('LICENSE.txt', f'dist/{project_name}/')
shutil.copy('README.md', f'dist/{project_name}/')
# normalize platform name
os_ = platform.system().lower()
if os_ == 'darwin': os_ = 'macos'
arch = platform.machine().lower()
if arch == 'amd64': arch = 'x86_64'
# archive artifacts
base_name = f'{project_name}-{version}-{os_}-{arch}'
fmt = 'gztar' if os.name == 'posix' else 'zip'
logging.basicConfig(level=logging.INFO)
file = shutil.make_archive(f'dist/{base_name}', fmt, root_dir='dist', base_dir=project_name, logger=logger)
logger.info(f"Archive created: {file}")
