"""
Scribe - AI-powered documentation generator
"""
"""Data models for Scribe documentation generator."""

from dataclasses import dataclass


@dataclass
class FileInfo:
    """Information about a code file"""
    path: str
    content: str
    language: str
    size_kb: float
