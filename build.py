#!/usr/bin/env python3
import logging
import os
import platform
import shutil
import subprocess

import PyInstaller.__main__

project_name = 'yarc'
logger = logging.getLogger(__name__)

# run pyinstaller
PyInstaller.__main__.run(['build.spec'])
# copy additional files
shutil.copy('LICENSE.txt', f'dist/{project_name}/')
shutil.copy('README.md', f'dist/{project_name}/')
# get git tag or commit
version = subprocess.check_output(['git', 'describe', '--tags', '--dirty', '--always'], text=True).strip()
version = version.replace('-', '_')
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
