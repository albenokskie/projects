"""
Scribe - AI-powered documentation generator
"""
"""Code analysis module for Scribe."""

import os
import fnmatch
from pathlib import Path
from typing import List
import re

from .config import Config
from .models import FileInfo
from .constants import LANGUAGE_EXTENSIONS


class CodeAnalyzer:
    """Analyzes codebase and extracts relevant files"""
    
    def __init__(self, config: Config):
        self.config = config
        
    def should_ignore(self, path: str) -> bool:
        """Check if a file/directory should be ignored"""
        path_parts = Path(path).parts
        
        for pattern in self.config.ignore_patterns:
            # Check if any part of the path matches the pattern
            for part in path_parts:
                if fnmatch.fnmatch(part, pattern):
                    return True
            # Also check the full path
            if fnmatch.fnmatch(path, pattern):
                return True
                
        return False
    
    def get_language(self, file_path: str) -> str:
        """Determine the programming language from file extension"""
        ext = Path(file_path).suffix.lower()
        return LANGUAGE_EXTENSIONS.get(ext, 'text')
    
    def analyze_directory(self, directory: str) -> List[FileInfo]:
        """Analyze all code files in a directory"""
        files = []
        
        for root, dirs, filenames in os.walk(directory):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if not self.should_ignore(os.path.join(root, d))]
            
            for filename in filenames:
                file_path = os.path.join(root, filename)
                
                if self.should_ignore(file_path):
                    continue
                
                # Check file size
                try:
                    size_kb = os.path.getsize(file_path) / 1024
                    if size_kb > self.config.max_file_size_kb:
                        print(f"Skipping large file: {file_path} ({size_kb:.1f} KB)")
                        continue
                    
                    # Read file content
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Skip binary files
                    if '\0' in content:
                        continue
                    
                    language = self.get_language(file_path)
                    
                    # Skip if not including private and file contains private indicators
                    if not self.config.include_private:
                        if language == 'python' and re.search(r'def _|class _', content):
                            # Still include the file but AI will handle private method filtering
                            pass
                    
                    files.append(FileInfo(
                        path=os.path.relpath(file_path, directory),
                        content=content,
                        language=language,
                        size_kb=size_kb
                    ))
                    
                except Exception as e:
                    print(f"Error reading file {file_path}: {e}")
                    
        return files
