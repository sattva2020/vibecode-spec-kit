# src/cli/core/templates/levels/level2_template.py
"""
Level 2 Template - Simple Enhancement
Template for simple enhancements and moderate changes.
"""

from ..base.base_template import BaseTemplate
from ..base.template_field import TemplateField, FieldType, ValidationRule, FieldOption


class Level2Template(BaseTemplate):
    """
    Level 2 Template for Simple Enhancement tasks.
    Moderate complexity with standard planning and testing.
    """
    
    def __init__(self):
        super().__init__(complexity_level=2, template_type="Simple Enhancement")
    
    def _initialize_template(self):
        """Initialize Level 2 template fields."""
        
        # Title field
        title_field = TemplateField(
            name="title",
            field_type=FieldType.TEXT,
            label="Title",
            description="Clear title describing the enhancement",
            required=True,
            placeholder="e.g., Add user profile editing functionality",
            validation_rules=[ValidationRule.REQUIRED, ValidationRule.MIN_LENGTH_10]
        )
        self.add_field(title_field)
        
        # Description field
        description_field = TemplateField(
            name="description",
            field_type=FieldType.MULTILINE_TEXT,
            label="Description",
            description="Detailed description of the enhancement and its benefits",
            required=True,
            placeholder="Describe the enhancement, its purpose, and expected benefits",
            validation_rules=[ValidationRule.REQUIRED, ValidationRule.MIN_LENGTH_50]
        )
        self.add_field(description_field)
        
        # Requirements field
        requirements_field = TemplateField(
            name="requirements",
            field_type=FieldType.MULTILINE_TEXT,
            label="Requirements",
            description="Functional requirements for the enhancement",
            required=True,
            placeholder="List the functional requirements and specifications",
            validation_rules=[ValidationRule.REQUIRED, ValidationRule.MIN_LENGTH_30],
            help_text="Use bullet points or numbered lists for clarity"
        )
        self.add_field(requirements_field)
        
        # Implementation field
        implementation_field = TemplateField(
            name="implementation",
            field_type=FieldType.MULTILINE_TEXT,
            label="Implementation",
            description="Implementation approach and details",
            required=True,
            placeholder="Describe how the enhancement will be implemented",
            validation_rules=[ValidationRule.REQUIRED, ValidationRule.MIN_LENGTH_30]
        )
        self.add_field(implementation_field)
        
        # Testing strategy field
        testing_strategy_field = TemplateField(
            name="testing_strategy",
            field_type=FieldType.MULTILINE_TEXT,
            label="Testing Strategy",
            description="Testing approach and validation methods",
            required=True,
            placeholder="Describe testing approach including unit tests, integration tests, and user testing",
            validation_rules=[ValidationRule.REQUIRED, ValidationRule.MIN_LENGTH_20]
        )
        self.add_field(testing_strategy_field)
        
        # Dependencies field
        dependencies_field = TemplateField(
            name="dependencies",
            field_type=FieldType.MULTILINE_TEXT,
            label="Dependencies",
            description="Dependencies and prerequisites",
            required=False,
            placeholder="List any dependencies or prerequisites",
            help_text="Include external libraries, services, or other features required"
        )
        self.add_field(dependencies_field)
        
        # Estimated effort field
        effort_field = TemplateField(
            name="estimated_effort",
            field_type=FieldType.SELECT,
            label="Estimated Effort",
            description="Estimated time to complete the enhancement",
            required=False,
            default_value="2-5 days",
            options=[
                FieldOption("1-2 days", "1-2 days", "Small enhancement"),
                FieldOption("2-5 days", "2-5 days", "Medium enhancement"),
                FieldOption("1 week", "1 week", "Large enhancement"),
                FieldOption("1-2 weeks", "1-2 weeks", "Very large enhancement")
            ]
        )
        self.add_field(effort_field)
    
    def get_template_summary(self) -> str:
        """Get a summary of this template."""
        return (
            "Level 2 Template - Simple Enhancement\n"
            "Moderate complexity template for enhancements and improvements.\n"
            "Includes: Title, Description, Requirements, Implementation, Testing Strategy, Dependencies, Effort\n"
            "Best for: Feature enhancements, UI improvements, moderate functionality additions"
        )
    
    def get_expected_completion_time(self) -> str:
        """Get expected completion time for Level 2 tasks."""
        return "1 day to 1 week"
    
    def get_complexity_description(self) -> str:
        """Get description of Level 2 complexity."""
        return (
            "Simple Enhancement - Moderate complexity requiring planning and testing. "
            "Standard implementation approach with clear requirements and testing strategy."
        )
