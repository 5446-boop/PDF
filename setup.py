"""
PDF Highlighter 2.0 - Setup Script
Last Updated: 2025-02-22 21:19:08 UTC
"""

import os
from pathlib import Path

# Create directory structure
directories = [
    'src',
    'src/ui',
    'src/config',
]

for directory in directories:
    Path(directory).mkdir(parents=True, exist_ok=True)

# Create __init__.py files
init_files = [
    'src/__init__.py',
    'src/ui/__init__.py',
    'src/config/__init__.py'
]

for init_file in init_files:
    with open(init_file, 'w') as f:
        f.write('"""PDF Highlighter 2.0"""\n')