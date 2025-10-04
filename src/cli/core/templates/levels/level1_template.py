# src/cli/core/templates/levels/level1_template.py
"""
Level 1 Template - Quick Bug Fix
Simple template for quick bug fixes and minor issues.
"""

from ..base.base_template import BaseTemplate
from ..base.template_field import TemplateField, FieldType, ValidationRule, FieldOption


class Level1Template(BaseTemplate):
    """
    Level 1 Template for Quick Bug Fix tasks.
    Minimal complexity with essential fields only.
    """
    
    def __init__(self):
        super().__init__(complexity_level=1, template_type="Quick Bug Fix")
    
    def _initialize_template(self):
        """Initialize Level 1 template fields."""
        
        # Title field
        title_field = TemplateField(
            name="title",
            field_type=FieldType.TEXT,
            label="Title",
            description="Brief title describing the bug fix",
            required=True,
            placeholder="e.g., Fix login button not responding",
            validation_rules=[ValidationRule.REQUIRED, ValidationRule.MIN_LENGTH_10]
        )
        self.add_field(title_field)
        
        # Description field
        description_field = TemplateField(
            name="description",
            field_type=FieldType.MULTILINE_TEXT,
            label="Description",
            description="Detailed description of the bug and its impact",
            required=True,
            placeholder="Describe the bug, how to reproduce it, and its impact on users",
            validation_rules=[ValidationRule.REQUIRED, ValidationRule.MIN_LENGTH_50]
        )
        self.add_field(description_field)
        
        # Solution field
        solution_field = TemplateField(
            name="solution",
            field_type=FieldType.MULTILINE_TEXT,
            label="Solution",
            description="Proposed solution or fix for the bug",
            required=True,
            placeholder="Describe the proposed fix, including any code changes or configuration updates",
            validation_rules=[ValidationRule.REQUIRED, ValidationRule.MIN_LENGTH_20]
        )
        self.add_field(solution_field)
        
        # Testing notes field
        testing_field = TemplateField(
            name="testing_notes",
            field_type=FieldType.MULTILINE_TEXT,
            label="Testing Notes",
            description="Notes on how to test the fix",
            required=False,
            placeholder="Steps to verify the fix works correctly",
            validation_rules=[ValidationRule.MIN_LENGTH_10]
        )
        self.add_field(testing_field)
        
        # Priority field
        priority_field = TemplateField(
            name="priority",
            field_type=FieldType.SELECT,
            label="Priority",
            description="Priority level for this bug fix",
            required=False,
            default_value="medium",
            options=[
                FieldOption("low", "Low", "Can be fixed in next release"),
                FieldOption("medium", "Medium", "Should be fixed soon"),
                FieldOption("high", "High", "Needs immediate attention"),
                FieldOption("critical", "Critical", "Blocks functionality")
            ]
        )
        self.add_field(priority_field)
        
        # Estimated effort field
        effort_field = TemplateField(
            name="estimated_effort",
            field_type=FieldType.SELECT,
            label="Estimated Effort",
            description="Estimated time to complete the fix",
            required=False,
            default_value="1-2 hours",
            options=[
                FieldOption("15-30min", "15-30 minutes", "Quick fix"),
                FieldOption("1-2 hours", "1-2 hours", "Standard fix"),
                FieldOption("half day", "Half day", "Complex fix"),
                FieldOption("1 day", "1 day", "Very complex fix")
            ]
        )
        self.add_field(effort_field)
        
        # Dependencies field
        dependencies_field = TemplateField(
            name="dependencies",
            field_type=FieldType.TEXT,
            label="Dependencies",
            description="Any dependencies or prerequisites for this fix",
            required=False,
            placeholder="e.g., Database migration, external service update, etc.",
            help_text="Leave empty if no dependencies"
        )
        self.add_field(dependencies_field)
    
    def get_template_summary(self) -> str:
        """Get a summary of this template."""
        return (
            "Level 1 Template - Quick Bug Fix\n"
            "Minimal complexity template for simple bug fixes and minor issues.\n"
            "Includes: Title, Description, Solution, Testing Notes, Priority, Effort, Dependencies\n"
            "Best for: Single-file changes, configuration updates, minor UI fixes"
        )
    
    def get_expected_completion_time(self) -> str:
        """Get expected completion time for Level 1 tasks."""
        return "15 minutes to 1 day"
    
    def get_complexity_description(self) -> str:
        """Get description of Level 1 complexity."""
        return (
            "Quick Bug Fix - Simple, isolated changes that can be completed quickly. "
            "Minimal planning required, straightforward implementation, basic testing sufficient."
        )
