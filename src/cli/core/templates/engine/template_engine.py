# src/cli/core/templates/engine/template_engine.py
"""
Template Engine for generating and managing templates based on complexity levels.
Provides centralized template generation, caching, and management functionality.
"""

from typing import Dict, List, Any, Optional, Type
import os
import json
from datetime import datetime

from ..base.base_template import BaseTemplate
from ..base.template_validator import TemplateValidator, ValidationResult
from ..levels.level1_template import Level1Template
from ..levels.level2_template import Level2Template
from ..levels.level3_template import Level3Template
from ..levels.level4_template import Level4Template
from .complexity_detector import ComplexityDetector
from .template_cache import TemplateCache


class TemplateEngine:
    """
    Central template engine for generating and managing templates.
    Handles complexity detection, template generation, and caching.
    """
    
    def __init__(self, cache_directory: str = ".template_cache"):
        self.cache_directory = cache_directory
        self.validator = TemplateValidator()
        self.complexity_detector = ComplexityDetector()
        self.cache = TemplateCache(cache_directory)
        
        # Register available template levels
        self.template_levels: Dict[int, Type[BaseTemplate]] = {
            1: Level1Template,
            2: Level2Template,
            3: Level3Template,
            4: Level4Template
        }
        
        # Initialize cache directory
        os.makedirs(cache_directory, exist_ok=True)
    
    def generate_template(self, 
                         complexity_level: int, 
                         template_type: str = "generic",
                         data: Optional[Dict[str, Any]] = None) -> BaseTemplate:
        """
        Generate a template for the specified complexity level.
        
        Args:
            complexity_level: Complexity level (1-4)
            template_type: Type of template (spec, plan, task, etc.)
            data: Optional data to populate the template
        
        Returns:
            BaseTemplate instance for the specified level
        """
        # Validate complexity level
        if complexity_level not in self.template_levels:
            raise ValueError(f"Unsupported complexity level: {complexity_level}")
        
        # Get template class and create instance
        template_class = self.template_levels[complexity_level]
        template = template_class()
        
        # Set template type if provided
        if template_type != "generic":
            template.template_type = template_type
        
        # Populate with data if provided
        if data:
            template = self._populate_template(template, data)
        
        return template
    
    def detect_complexity_and_generate(self, 
                                     description: str, 
                                     context: Optional[Dict[str, Any]] = None) -> BaseTemplate:
        """
        Automatically detect complexity from description and generate appropriate template.
        
        Args:
            description: Task or feature description
            context: Optional context information
        
        Returns:
            BaseTemplate instance with detected complexity level
        """
        # Detect complexity level
        complexity_level = self.complexity_detector.detect_complexity(description, context)
        
        # Generate template
        template = self.generate_template(complexity_level, "auto_detected")
        
        # Pre-populate with detected information
        if context:
            template = self._populate_from_context(template, description, context)
        
        return template
    
    def validate_template_data(self, 
                              template: BaseTemplate, 
                              data: Dict[str, Any]) -> ValidationResult:
        """
        Validate template data against template requirements.
        
        Args:
            template: Template instance
            data: Data to validate
        
        Returns:
            ValidationResult with validation status and details
        """
        return self.validator.validate_template(data, template.get_all_fields(), template.get_template_type())
    
    def generate_template_content(self, 
                                 template: BaseTemplate, 
                                 data: Dict[str, Any]) -> str:
        """
        Generate formatted content from template and data.
        
        Args:
            template: Template instance
            data: Data to use for content generation
        
        Returns:
            Formatted string content
        """
        return template.generate_template_content(data)
    
    def save_template_to_file(self, 
                             template: BaseTemplate, 
                             data: Dict[str, Any], 
                             file_path: str) -> bool:
        """
        Save template content to a file.
        
        Args:
            template: Template instance
            data: Data to use for content generation
            file_path: Path where to save the file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            content = self.generate_template_content(template, data)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
        except Exception as e:
            print(f"Error saving template to file: {e}")
            return False
    
    def load_template_from_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Load template data from a JSON file.
        
        Args:
            file_path: Path to the template data file
        
        Returns:
            Dictionary with template data or None if failed
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading template from file: {e}")
            return None
    
    def get_available_complexity_levels(self) -> List[int]:
        """Get list of available complexity levels."""
        return sorted(self.template_levels.keys())
    
    def get_template_info(self, complexity_level: int) -> Optional[Dict[str, Any]]:
        """
        Get information about a template level.
        
        Args:
            complexity_level: Complexity level to get info for
        
        Returns:
            Dictionary with template information or None if not found
        """
        if complexity_level not in self.template_levels:
            return None
        
        template_class = self.template_levels[complexity_level]
        template_instance = template_class()
        
        return {
            "complexity_level": complexity_level,
            "template_type": template_instance.get_template_type(),
            "summary": template_instance.get_template_summary(),
            "expected_completion_time": template_instance.get_expected_completion_time(),
            "complexity_description": template_instance.get_complexity_description(),
            "required_fields": template_instance.required_fields,
            "optional_fields": template_instance.optional_fields,
            "total_fields": len(template_instance.get_all_fields())
        }
    
    def get_template_field_info(self, complexity_level: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed field information for a template level.
        
        Args:
            complexity_level: Complexity level to get field info for
        
        Returns:
            Dictionary with field information or None if not found
        """
        if complexity_level not in self.template_levels:
            return None
        
        template_class = self.template_levels[complexity_level]
        template_instance = template_class()
        
        field_info = {}
        for field_name in template_instance.get_all_fields():
            field = template_instance.get_field_metadata(field_name)
            if field:
                field_info[field_name] = {
                    "label": field.label,
                    "description": field.description,
                    "required": field.required,
                    "field_type": field.field_type.value,
                    "validation_rules": [rule.value for rule in field.validation_rules],
                    "help_text": field.help_text
                }
        
        return field_info
    
    def _populate_template(self, template: BaseTemplate, data: Dict[str, Any]) -> BaseTemplate:
        """Populate template with provided data."""
        # This is a placeholder - in a real implementation, you would
        # populate the template fields with the provided data
        return template
    
    def _populate_from_context(self, 
                              template: BaseTemplate, 
                              description: str, 
                              context: Dict[str, Any]) -> BaseTemplate:
        """Populate template with information from context and description."""
        # Pre-populate description if available
        if hasattr(template, 'description') and description:
            # This would be implemented to populate the template fields
            pass
        
        return template
    
    def create_template_preview(self, complexity_level: int) -> str:
        """
        Create a preview of what a template looks like.
        
        Args:
            complexity_level: Complexity level to preview
        
        Returns:
            String preview of the template
        """
        if complexity_level not in self.template_levels:
            return f"Complexity level {complexity_level} not supported"
        
        template_class = self.template_levels[complexity_level]
        template_instance = template_class()
        
        # Create preview content
        preview_lines = [
            f"# {template_instance.get_template_type()} Template - Level {complexity_level}",
            "",
            f"**Summary**: {template_instance.get_template_summary()}",
            "",
            f"**Expected Completion Time**: {template_instance.get_expected_completion_time()}",
            "",
            f"**Complexity Description**: {template_instance.get_complexity_description()}",
            "",
            "## Required Fields:",
            ""
        ]
        
        # Add required fields
        for field_name in template_instance.required_fields:
            field = template_instance.get_field_metadata(field_name)
            if field:
                preview_lines.append(f"- **{field.label}**: {field.description}")
        
        preview_lines.extend(["", "## Optional Fields:", ""])
        
        # Add optional fields
        for field_name in template_instance.optional_fields:
            field = template_instance.get_field_metadata(field_name)
            if field:
                preview_lines.append(f"- **{field.label}**: {field.description}")
        
        # Add conditional fields
        if template_instance.conditional_fields:
            preview_lines.extend(["", "## Conditional Fields:", ""])
            for field_name in template_instance.conditional_fields.keys():
                field = template_instance.get_field_metadata(field_name)
                if field:
                    preview_lines.append(f"- **{field.label}**: {field.description} (conditional)")
        
        return "\n".join(preview_lines)
    
    def export_template_schema(self, complexity_level: int) -> Optional[Dict[str, Any]]:
        """
        Export template schema as JSON.
        
        Args:
            complexity_level: Complexity level to export
        
        Returns:
            Dictionary with template schema or None if not found
        """
        if complexity_level not in self.template_levels:
            return None
        
        template_class = self.template_levels[complexity_level]
        template_instance = template_class()
        
        schema = {
            "complexity_level": complexity_level,
            "template_type": template_instance.get_template_type(),
            "created_at": datetime.now().isoformat(),
            "fields": {}
        }
        
        # Export all fields
        for field_name in template_instance.get_all_fields():
            field = template_instance.get_field_metadata(field_name)
            if field:
                schema["fields"][field_name] = field.to_dict()
        
        return schema
    
    def import_template_schema(self, schema: Dict[str, Any]) -> bool:
        """
        Import and register a template schema.
        
        Args:
            schema: Template schema to import
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # This would implement schema import functionality
            # For now, it's a placeholder
            return True
        except Exception as e:
            print(f"Error importing template schema: {e}")
            return False
