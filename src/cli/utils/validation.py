"""
Input validation utilities for Memory Bank CLI
"""

from typing import Any, List, Optional
from pathlib import Path


class InputValidator:
    """Validates CLI input parameters"""
    
    @staticmethod
    def validate_path(path: str) -> bool:
        """Validate file or directory path"""
        try:
            Path(path).resolve()
            return True
        except Exception:
            return False
    
    @staticmethod
    def validate_complexity_level(level: int) -> bool:
        """Validate complexity level"""
        return isinstance(level, int) and 1 <= level <= 4
    
    @staticmethod
    def validate_ai_agent(agent_name: str) -> bool:
        """Validate AI agent name"""
        valid_agents = ["github-copilot", "claude-code", "gemini-cli", "cursor"]
        return agent_name in valid_agents
    
    @staticmethod
    def validate_output_format(format: str) -> bool:
        """Validate output format"""
        valid_formats = ["text", "json", "yaml"]
        return format in valid_formats
    
    @staticmethod
    def validate_verbosity(verbosity: int) -> bool:
        """Validate verbosity level"""
        return isinstance(verbosity, int) and verbosity >= 0
