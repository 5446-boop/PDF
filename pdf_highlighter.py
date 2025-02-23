#!/usr/bin/env python3
"""
PDF Highlighter 2.0 - Entry Point
Last Updated: 2025-02-23 00:45:20 UTC
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).resolve().parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from src.main import main
except ImportError as e:
    print(f"Error: Required modules not found. Please install required packages:")
    print("pip install PyQt5 PyMuPDF")
    print(f"\nOriginal error: {e}")
    sys.exit(1)

if __name__ == "__main__":
    sys.exit(main())