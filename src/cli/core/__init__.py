"""
Core modules for Memory Bank CLI
"""

from .config import CLIConfig
from .memory_bank import MemoryBank
from .constitution import ConstitutionalValidator
# from .templates import TemplateManager  # Deprecated - now using src/cli/core/templates/
from .ai_agents import AIAgentManager

__all__ = [
    'CLIConfig',
    'MemoryBank', 
    'ConstitutionalValidator',
    'AIAgentManager'
]
