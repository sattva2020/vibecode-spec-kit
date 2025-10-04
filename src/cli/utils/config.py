"""
Configuration utilities for Memory Bank CLI
"""

from pathlib import Path
from typing import Dict, Any, Optional

from ..core.config import CLIConfig


class ConfigManager:
    """Manages CLI configuration"""
    
    @staticmethod
    def find_config_file() -> Optional[Path]:
        """Find configuration file in common locations"""
        search_paths = [
            Path("memory-bank-cli.json"),
            Path("memory-bank-cli.yml"),
            Path("memory-bank-cli.yaml"),
            Path(".memory-bank-cli.json"),
            Path(".memory-bank-cli.yml"),
            Path(".memory-bank-cli.yaml"),
            Path.home() / ".memory-bank-cli.json",
            Path.home() / ".memory-bank-cli.yml",
            Path.home() / ".memory-bank-cli.yaml"
        ]
        
        for config_path in search_paths:
            if config_path.exists():
                return config_path
        
        return None
    
    @staticmethod
    def create_default_config(config_path: Path) -> bool:
        """Create default configuration file"""
        try:
            config = CLIConfig.default()
            config.to_file(str(config_path))
            return True
        except Exception:
            return False
    
    @staticmethod
    def load_config(config_path: Optional[Path] = None) -> CLIConfig:
        """Load configuration from file or create default"""
        if config_path is None:
            config_path = ConfigManager.find_config_file()
        
        if config_path and config_path.exists():
            try:
                return CLIConfig.from_file(str(config_path))
            except Exception:
                pass
        
        return CLIConfig.default()
