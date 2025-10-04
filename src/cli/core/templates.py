"""
Template management for Memory Bank CLI
"""

from pathlib import Path
from typing import Dict, List, Any, Optional


class TemplateManager:
    """Manages Spec Kit templates"""
    
    def __init__(self, memory_bank_path: str = "memory-bank"):
        self.memory_bank_path = Path(memory_bank_path)
        self.template_dir = self.memory_bank_path / "templates"
    
    def list_templates(self) -> List[str]:
        """List available templates"""
        if not self.template_dir.exists():
            return []
        
        return [f.name for f in self.template_dir.glob("*.md")]
    
    def get_template(self, template_name: str) -> Optional[str]:
        """Get template content"""
        template_file = self.memory_bank_path / template_name
        if template_file.exists():
            return template_file.read_text(encoding='utf-8')
        return None
    
    def generate_template(self, template_name: str, **kwargs) -> str:
        """Generate template with parameters"""
        template_content = self.get_template(template_name)
        if template_content:
            # Simple template substitution
            for key, value in kwargs.items():
                template_content = template_content.replace(f"[{key.upper()}]", str(value))
            return template_content
        return ""
