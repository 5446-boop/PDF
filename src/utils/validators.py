"""
PDF Highlighter 2.0 - Validation Utilities
Last Updated: 2025-02-22 22:05:44 UTC
"""

import logging
import inspect
from functools import wraps
from typing import Type, List, Dict

logger = logging.getLogger(__name__)

def validate_class_requirements(required_methods: List[str] = None, 
                             required_attributes: List[str] = None):
    """
    Decorator to validate that a class has all required methods and attributes.
    
    Args:
        required_methods (List[str]): List of method names that must exist
        required_attributes (List[str]): List of attributes that must exist
    """
    def decorator(cls: Type):
        original_init = cls.__init__
        
        @wraps(original_init)
        def new_init(self, *args, **kwargs):
            # Validate methods
            if required_methods:
                missing_methods = []
                for method_name in required_methods:
                    if not hasattr(cls, method_name) or not callable(getattr(cls, method_name)):
                        missing_methods.append(method_name)
                
                if missing_methods:
                    error_msg = f"Class {cls.__name__} is missing required methods: {', '.join(missing_methods)}"
                    logger.error(error_msg)
                    raise AttributeError(error_msg)
            
            # Call original init
            original_init(self, *args, **kwargs)
            
            # Validate attributes after initialization
            if required_attributes:
                missing_attrs = []
                for attr in required_attributes:
                    if not hasattr(self, attr):
                        missing_attrs.append(attr)
                
                if missing_attrs:
                    error_msg = f"Instance of {cls.__name__} is missing required attributes: {', '.join(missing_attrs)}"
                    logger.error(error_msg)
                    raise AttributeError(error_msg)
            
        cls.__init__ = new_init
        return cls
    return decorator