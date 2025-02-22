"""
PDF Highlighter 2.0 - Qt Import Centralizer
Last Updated: 2025-02-22 21:19:08 UTC
"""

try:
    from PyQt5.QtWidgets import (
        QMainWindow,
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QToolBar,
        QAction,
        QFileDialog,
        QMessageBox,
        QColorDialog,
        QSpinBox,
        QLabel,
        QPushButton,
        QStatusBar,
        QSplitter,
        QScrollArea,
        QRubberBand,
        QApplication
    )

    from PyQt5.QtGui import (
        QIcon,
        QKeySequence,
        QImage,
        QPixmap,
        QPainter,
        QColor
    )

    from PyQt5.QtCore import (
        Qt,
        QSize,
        pyqtSignal,
        QPoint,
        QRect
    )
except ImportError as e:
    raise ImportError(f"PyQt5 is required. Install it with: pip install PyQt5\nError: {e}")