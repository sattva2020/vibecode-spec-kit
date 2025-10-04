# src/cli/core/templates/base/base_template.py
"""
Base template class for all template types in the Memory Bank system.
Provides common functionality for template inheritance and validation.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass


@dataclass
class TemplateField:
    """Represents a field in a template with its metadata."""
    name: str
    field_type: str
    required: bool = False
    description: str = ""
    default_value: Any = None
    validation_rules: List[str] = None
    
    def __post_init__(self):
        if self.validation_rules is None:
            self.validation_rules = []


class BaseTemplate(ABC):
    """
    Abstract base class for all templates in the Memory Bank system.
    Implements the template inheritance pattern with complexity-based variations.
    """
    
    def __init__(self, complexity_level: int, template_type: str):
        self.complexity_level = complexity_level
        self.template_type = template_type
        self.required_fields: List[str] = []
        self.optional_fields: List[str] = []
        self.conditional_fields: Dict[str, Callable] = {}
        self.field_metadata: Dict[str, TemplateField] = {}
        self.validation_rules: List[str] = []
        
        # Initialize template structure
        self._initialize_template()
    
    @abstractmethod
    def _initialize_template(self):
        """Initialize template-specific fields and structure."""
        pass
    
    def add_field(self, field: TemplateField):
        """Add a field to the template."""
        self.field_metadata[field.name] = field
        
        if field.required:
            self.required_fields.append(field.name)
        else:
            self.optional_fields.append(field.name)
    
    def add_conditional_field(self, field_name: str, condition: Callable):
        """Add a conditional field that appears based on a condition."""
        self.conditional_fields[field_name] = condition
    
    def get_all_fields(self) -> List[str]:
        """Get all field names including conditional fields."""
        all_fields = self.required_fields + self.optional_fields
        
        # Add conditional fields that meet their conditions
        for field_name, condition in self.conditional_fields.items():
            if condition():
                all_fields.append(field_name)
        
        return all_fields
    
    def get_field_metadata(self, field_name: str) -> Optional[TemplateField]:
        """Get metadata for a specific field."""
        return self.field_metadata.get(field_name)
    
    def validate_field(self, field_name: str, value: Any) -> tuple[bool, str]:
        """Validate a specific field value."""
        field = self.get_field_metadata(field_name)
        if not field:
            return False, f"Unknown field: {field_name}"
        
        # Check required field
        if field.required and not value:
            return False, f"Required field '{field_name}' is missing"
        
        # Apply validation rules
        for rule in field.validation_rules:
            if not self._apply_validation_rule(rule, value):
                return False, f"Field '{field_name}' failed validation rule: {rule}"
        
        return True, ""
    
    def _apply_validation_rule(self, rule: str, value: Any) -> bool:
        """Apply a specific validation rule to a value."""
        if rule == "non_empty_string" and isinstance(value, str):
            return len(value.strip()) > 0
        elif rule == "min_length_10" and isinstance(value, str):
            return len(value) >= 10
        elif rule == "min_length_50" and isinstance(value, str):
            return len(value) >= 50
        elif rule == "positive_integer" and isinstance(value, int):
            return value > 0
        elif rule == "valid_email" and isinstance(value, str):
            return "@" in value and "." in value
        else:
            return True  # Unknown rule, assume valid
    
    def generate_template_content(self, data: Dict[str, Any]) -> str:
        """Generate template content based on provided data."""
        content_parts = []
        
        # Add header
        content_parts.append(f"# {self.template_type.title()} - Level {self.complexity_level}")
        content_parts.append("")
        
        # Process all fields
        for field_name in self.get_all_fields():
            field = self.get_field_metadata(field_name)
            if field:
                value = data.get(field_name, field.default_value)
                if value:
                    content_parts.append(f"## {field.name.replace('_', ' ').title()}")
                    content_parts.append(f"{value}")
                    content_parts.append("")
        
        return "\n".join(content_parts)
    
    def validate_template_data(self, data: Dict[str, Any]) -> tuple[bool, Dict[str, str]]:
        """Validate all template data and return validation results."""
        validation_results = {}
        all_valid = True
        
        # Validate required fields
        for field_name in self.required_fields:
            is_valid, error_msg = self.validate_field(field_name, data.get(field_name))
            if not is_valid:
                validation_results[field_name] = error_msg
                all_valid = False
        
        # Validate optional fields that have values
        for field_name in self.optional_fields:
            value = data.get(field_name)
            if value:  # Only validate if value is provided
                is_valid, error_msg = self.validate_field(field_name, value)
                if not is_valid:
                    validation_results[field_name] = error_msg
                    all_valid = False
        
        # Validate conditional fields
        for field_name, condition in self.conditional_fields.items():
            if condition() and field_name in data:
                is_valid, error_msg = self.validate_field(field_name, data.get(field_name))
                if not is_valid:
                    validation_results[field_name] = error_msg
                    all_valid = False
        
        return all_valid, validation_results
    
    def get_complexity_level(self) -> int:
        """Get the complexity level of this template."""
        return self.complexity_level
    
    def get_template_type(self) -> str:
        """Get the template type."""
        return self.template_type
