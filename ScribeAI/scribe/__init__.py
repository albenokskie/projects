"""
Scribe - AI-powered documentation generator for Confluence
"""
"""Scribe - AI-powered documentation generator for Confluence."""

from .config import Config
from .analyzer import CodeAnalyzer
from .generator import AIDocumentationGenerator
from .publisher import ConfluencePublisher
from .models import FileInfo

__version__ = "1.0.0"
__all__ = [
    "Config",
    "CodeAnalyzer",
    "AIDocumentationGenerator",
    "ConfluencePublisher",
    "FileInfo",
]
