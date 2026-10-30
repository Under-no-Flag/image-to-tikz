#!/usr/bin/env python3
"""Copy the standalone skill to an explicitly chosen agent skill directory."""
import argparse
import shutil
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--dest', required=True, type=Path, help='Full destination ending in image-to-tikz')
args = parser.parse_args()
source = Path(__file__).resolve().parents[1]/'skills/image-to-tikz'
dest = args.dest.expanduser().absolute()
if dest.exists() or dest.is_symlink():
    parser.error(f'Destination exists: {dest}. Back up or choose another path; no files were replaced.')
if dest.name != 'image-to-tikz':
    parser.error('Destination folder must be named image-to-tikz')
shutil.copytree(source, dest, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.DS_Store'))
print(f'Installed: {dest}\nNext: install requirements.txt in a Python virtual environment and run scripts/workflow.py doctor.')
