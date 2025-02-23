"""
PDF Highlighter 2.0 - Startup Validation System
Last Updated: 2025-02-22 22:24:52 UTC
"""

import sys
import logging
import importlib
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class StartupValidator:
    """Validates all required components before application startup."""
    
    REQUIRED_PACKAGES = {
        'PyQt5': 'pip install PyQt5',
        'fitz': 'pip install PyMuPDF'
    }
    
    REQUIRED_QT_MODULES = [
        'QtWidgets',
        'QtCore',
        'QtGui'
    ]
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.qt_modules: Dict[str, Any] = {}
        
    def validate_environment(self) -> bool:
        """
        Validate the entire environment.
        
        Returns:
            bool: True if environment is valid, False otherwise
        """
        return all([
            self.validate_python_version(),
            self.validate_required_packages(),
            self.validate_qt_environment(),
            self.validate_project_structure()
        ])
        
    def validate_python_version(self) -> bool:
        """Check Python version requirements."""
        required_version = (3, 7)
        current_version = sys.version_info[:2]
        
        if current_version < required_version:
            self.errors.append(
                f"Python {required_version[0]}.{required_version[1]} or higher is required. "
                f"Current version: {current_version[0]}.{current_version[1]}"
            )
            return False
        return True
        
    def validate_required_packages(self) -> bool:
        """Validate that all required packages are installed."""
        all_packages_valid = True
        
        for package, install_cmd in self.REQUIRED_PACKAGES.items():
            try:
                importlib.import_module(package.lower())
            except ImportError:
                self.errors.append(
                    f"Required package '{package}' is not installed. "
                    f"Install it with: {install_cmd}"
                )
                all_packages_valid = False
                
        return all_packages_valid
        
    def validate_qt_environment(self) -> bool:
        """Validate Qt environment and import required modules."""
        try:
            from PyQt5 import QtWidgets, QtCore, QtGui
            
            # Store Qt modules for later use
            self.qt_modules = {
                'QtWidgets': QtWidgets,
                'QtCore': QtCore,
                'QtGui': QtGui
            }
            
            return True
            
        except Exception as e:
            self.errors.append(f"Failed to initialize Qt environment: {str(e)}")
            return False
            
    def validate_project_structure(self) -> bool:
        """Validate project directory structure and files."""
        required_dirs = [
            'src',
            'src/ui',
            'src/utils',
            'src/config'
        ]
        
        required_files = [
            'src/__init__.py',
            'src/ui/__init__.py',
            'src/utils/__init__.py',
            'src/config/__init__.py',
            'src/main.py',
            'src/ui/main_window.py',
            'src/ui/qt_imports.py'
        ]
        
        # Check directories
        for directory in required_dirs:
            if not Path(directory).is_dir():
                self.errors.append(f"Required directory missing: {directory}")
                return False
                
        # Check files
        for file in required_files:
            if not Path(file).is_file():
                self.errors.append(f"Required file missing: {file}")
                return False
                
        return True
        
    def get_qt_module(self, module_name: str) -> Any:
        """Get a validated Qt module."""
        return self.qt_modules.get(module_name)
        
    def print_status(self):
        """Print validation status."""
        if self.errors:
            print("\nErrors:")
            for error in self.errors:
                print(f"❌ {error}")
                
        if self.warnings:
            print("\nWarnings:")
            for warning in self.warnings:
                print(f"⚠️ {warning}")
                
        if not self.errors and not self.warnings:
            print("✅ All validations passed successfully!")