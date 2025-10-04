# src/cli/core/templates/base/template_field.py
"""
Template field definitions and validation for the Memory Bank template system.
"""

from dataclasses import dataclass
from typing import Any, List, Optional, Dict
from enum import Enum


class FieldType(Enum):
    """Enumeration of supported field types."""
    TEXT = "text"
    MULTILINE_TEXT = "multiline_text"
    NUMBER = "number"
    BOOLEAN = "boolean"
    SELECT = "select"
    MULTI_SELECT = "multi_select"
    DATE = "date"
    EMAIL = "email"
    URL = "url"
    LIST = "list"
    DICT = "dict"


class ValidationRule(Enum):
    """Enumeration of validation rules."""
    REQUIRED = "required"
    NON_EMPTY_STRING = "non_empty_string"
    MIN_LENGTH_10 = "min_length_10"
    MIN_LENGTH_20 = "min_length_20"
    MIN_LENGTH_30 = "min_length_30"
    MIN_LENGTH_50 = "min_length_50"
    MIN_LENGTH_100 = "min_length_100"
    MIN_LENGTH_150 = "min_length_150"
    MIN_LENGTH_200 = "min_length_200"
    MAX_LENGTH_500 = "max_length_500"
    POSITIVE_INTEGER = "positive_integer"
    VALID_EMAIL = "valid_email"
    VALID_URL = "valid_url"
    NO_SPECIAL_CHARS = "no_special_chars"
    ALPHANUMERIC = "alphanumeric"


@dataclass
class FieldOption:
    """Represents an option for select/multi-select fields."""
    value: str
    label: str
    description: Optional[str] = None


@dataclass
class TemplateField:
    """
    Enhanced template field with comprehensive metadata and validation.
    """
    name: str
    field_type: FieldType
    label: str
    description: str
    required: bool = False
    default_value: Any = None
    placeholder: str = ""
    validation_rules: List[ValidationRule] = None
    options: List[FieldOption] = None  # For select/multi-select fields
    help_text: str = ""
    conditional_show: Optional[str] = None  # Field name to check for conditional display
    conditional_value: Any = None  # Value to check for conditional display
    
    def __post_init__(self):
        if self.validation_rules is None:
            self.validation_rules = []
        if self.options is None:
            self.options = []
        
        # Add required validation rule if field is required
        if self.required and ValidationRule.REQUIRED not in self.validation_rules:
            self.validation_rules.append(ValidationRule.REQUIRED)
    
    def add_validation_rule(self, rule: ValidationRule):
        """Add a validation rule to the field."""
        if rule not in self.validation_rules:
            self.validation_rules.append(rule)
    
    def remove_validation_rule(self, rule: ValidationRule):
        """Remove a validation rule from the field."""
        if rule in self.validation_rules:
            self.validation_rules.remove(rule)
    
    def add_option(self, option: FieldOption):
        """Add an option for select/multi-select fields."""
        self.options.append(option)
    
    def get_option_by_value(self, value: str) -> Optional[FieldOption]:
        """Get an option by its value."""
        for option in self.options:
            if option.value == value:
                return option
        return None
    
    def validate_value(self, value: Any) -> tuple[bool, str]:
        """
        Validate a field value against all validation rules.
        Returns (is_valid, error_message).
        """
        # Check required field
        if ValidationRule.REQUIRED in self.validation_rules:
            if not value or (isinstance(value, str) and not value.strip()):
                return False, f"Field '{self.label}' is required"
        
        # Skip other validations if value is empty and not required
        if not value:
            return True, ""
        
        # Apply validation rules
        for rule in self.validation_rules:
            if rule == ValidationRule.REQUIRED:
                continue  # Already checked above
            
            is_valid, error_msg = self._apply_validation_rule(rule, value)
            if not is_valid:
                return False, error_msg
        
        return True, ""
    
    def _apply_validation_rule(self, rule: ValidationRule, value: Any) -> tuple[bool, str]:
        """Apply a specific validation rule to a value."""
        if rule == ValidationRule.NON_EMPTY_STRING:
            if not isinstance(value, str) or not value.strip():
                return False, "Value must be a non-empty string"
        
        elif rule == ValidationRule.MIN_LENGTH_10:
            if isinstance(value, str) and len(value) < 10:
                return False, "Value must be at least 10 characters long"
        
        elif rule == ValidationRule.MIN_LENGTH_20:
            if isinstance(value, str) and len(value) < 20:
                return False, "Value must be at least 20 characters long"
        
        elif rule == ValidationRule.MIN_LENGTH_30:
            if isinstance(value, str) and len(value) < 30:
                return False, "Value must be at least 30 characters long"
        
        elif rule == ValidationRule.MIN_LENGTH_50:
            if isinstance(value, str) and len(value) < 50:
                return False, "Value must be at least 50 characters long"
        
        elif rule == ValidationRule.MIN_LENGTH_100:
            if isinstance(value, str) and len(value) < 100:
                return False, "Value must be at least 100 characters long"
        
        elif rule == ValidationRule.MIN_LENGTH_150:
            if isinstance(value, str) and len(value) < 150:
                return False, "Value must be at least 150 characters long"
        
        elif rule == ValidationRule.MIN_LENGTH_200:
            if isinstance(value, str) and len(value) < 200:
                return False, "Value must be at least 200 characters long"
        
        elif rule == ValidationRule.MAX_LENGTH_500:
            if isinstance(value, str) and len(value) > 500:
                return False, "Value must be no more than 500 characters long"
        
        elif rule == ValidationRule.POSITIVE_INTEGER:
            if not isinstance(value, int) or value <= 0:
                return False, "Value must be a positive integer"
        
        elif rule == ValidationRule.VALID_EMAIL:
            if isinstance(value, str):
                if "@" not in value or "." not in value:
                    return False, "Value must be a valid email address"
        
        elif rule == ValidationRule.VALID_URL:
            if isinstance(value, str):
                if not value.startswith(("http://", "https://")):
                    return False, "Value must be a valid URL starting with http:// or https://"
        
        elif rule == ValidationRule.NO_SPECIAL_CHARS:
            if isinstance(value, str):
                import re
                if re.search(r'[<>:"/\\|?*]', value):
                    return False, "Value cannot contain special characters: < > : \" / \\ | ? *"
        
        elif rule == ValidationRule.ALPHANUMERIC:
            if isinstance(value, str):
                import re
                if not re.match(r'^[a-zA-Z0-9\s_-]+$', value):
                    return False, "Value must contain only alphanumeric characters, spaces, hyphens, and underscores"
        
        return True, ""
    
    def should_show(self, form_data: Dict[str, Any]) -> bool:
        """
        Determine if this field should be shown based on conditional logic.
        """
        if not self.conditional_show:
            return True
        
        conditional_value = form_data.get(self.conditional_show)
        return conditional_value == self.conditional_value
    
    def get_rendered_value(self, value: Any) -> str:
        """
        Get a human-readable representation of the field value.
        """
        if value is None:
            return ""
        
        if self.field_type == FieldType.BOOLEAN:
            return "Yes" if value else "No"
        
        elif self.field_type in [FieldType.SELECT, FieldType.MULTI_SELECT]:
            if isinstance(value, list):
                return ", ".join([str(v) for v in value])
            else:
                option = self.get_option_by_value(str(value))
                return option.label if option else str(value)
        
        elif self.field_type == FieldType.LIST:
            if isinstance(value, list):
                return "\n".join([f"- {item}" for item in value])
            else:
                return str(value)
        
        elif self.field_type == FieldType.DICT:
            if isinstance(value, dict):
                return "\n".join([f"- **{k}**: {v}" for k, v in value.items()])
            else:
                return str(value)
        
        else:
            return str(value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the field to a dictionary representation."""
        return {
            "name": self.name,
            "field_type": self.field_type.value,
            "label": self.label,
            "description": self.description,
            "required": self.required,
            "default_value": self.default_value,
            "placeholder": self.placeholder,
            "validation_rules": [rule.value for rule in self.validation_rules],
            "options": [
                {
                    "value": opt.value,
                    "label": opt.label,
                    "description": opt.description
                }
                for opt in self.options
            ],
            "help_text": self.help_text,
            "conditional_show": self.conditional_show,
            "conditional_value": self.conditional_value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TemplateField':
        """Create a TemplateField from a dictionary representation."""
        field = cls(
            name=data["name"],
            field_type=FieldType(data["field_type"]),
            label=data["label"],
            description=data["description"],
            required=data.get("required", False),
            default_value=data.get("default_value"),
            placeholder=data.get("placeholder", ""),
            validation_rules=[
                ValidationRule(rule) for rule in data.get("validation_rules", [])
            ],
            options=[
                FieldOption(
                    value=opt["value"],
                    label=opt["label"],
                    description=opt.get("description")
                )
                for opt in data.get("options", [])
            ],
            help_text=data.get("help_text", ""),
            conditional_show=data.get("conditional_show"),
            conditional_value=data.get("conditional_value")
        )
        return field
