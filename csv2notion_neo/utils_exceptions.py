"""
CSV2Notion Neo - Custom Exceptions

This module defines custom exception classes for CSV2Notion Neo.
It provides specific error types for different failure scenarios,
enabling better error handling and debugging throughout the application.
"""

class CriticalError(Exception):
    """Exception raised when a generic critical error occurs."""


class NotionError(Exception):
    """Exception raised when a Notion related critical error occurs."""


class TypeConversionError(Exception):
    """Exception raised when a type conversion error occurs."""
