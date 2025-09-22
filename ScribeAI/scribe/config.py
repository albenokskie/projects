"""
Scribe - AI-powered documentation generator
"""
"""Configuration management for Scribe."""

import os
import yaml
from typing import List


class Config:
    """Manages configuration from codex_config.yaml"""
    
    def __init__(self, config_path: str = "codex_config.yaml"):
        self.config_path = config_path
        self.data = self._load_config()
        
    def _load_config(self) -> dict:
        """Load configuration from YAML file"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    @property
    def confluence_url(self) -> str:
        return self.data['confluence']['url']
    
    @property
    def confluence_space_key(self) -> str:
        return self.data['confluence']['space_key']
    
    @property
    def confluence_username(self) -> str:
        return self.data['confluence']['username']
    
    @property
    def confluence_api_token(self) -> str:
        return self.data['confluence']['api_token']
    
    @property
    def ai_model(self) -> str:
        return self.data['ai']['model']
    
    @property
    def ai_api_key(self) -> str:
        return self.data['ai']['api_key']
    
    @property
    def ai_api_endpoint(self) -> str:
        return self.data['ai']['api_endpoint']
    
    @property
    def ignore_patterns(self) -> List[str]:
        return self.data['settings']['ignore_patterns']
    
    @property
    def include_private(self) -> bool:
        return self.data['settings']['include_private']
    
    @property
    def max_file_size_kb(self) -> int:
        return self.data['settings']['max_file_size_kb']
    
    @property
    def preview_before_publish(self) -> bool:
        return self.data['settings']['preview_before_publish']
