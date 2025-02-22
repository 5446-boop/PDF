"""
PDF Highlighter 2.0 - Main Window
Last Updated: 2025-02-22 20:48:47 UTC
Version: 2.0.0
"""

import os
import logging
from PyQt5.QtWidgets import (
    QMainWindow, QFileDialog, QMessageBox, QToolBar,
    QAction, QColorDialog, QStatusBar
)
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtCore import Qt, QSettings

from src.config.settings import AppConfig
from src.ui.viewer import PDFViewer
from src.ui.shortcuts import Shortcuts

logger = logging.getLogger(__name__)