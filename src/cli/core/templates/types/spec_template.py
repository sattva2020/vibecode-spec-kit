# src/cli/core/templates/types/spec_template.py
"""
Specification template type for feature specifications.
Extends base templates with specification-specific fields and validation.
"""

from ..base.base_template import BaseTemplate
from ..base.template_field import TemplateField, FieldType, ValidationRule, FieldOption
from typing import Dict, Any


class SpecTemplate:
    """
    Specification template type with specification-specific fields and validation.
    Can be applied to any complexity level template.
    """
    
    @staticmethod
    def enhance_template(template: BaseTemplate) -> BaseTemplate:
        """
        Enhance a base template with specification-specific fields.
        
        Args:
            template: Base template to enhance
        
        Returns:
            Enhanced template with specification fields
        """
        # Add user stories field
        user_stories_field = TemplateField(
            name="user_stories",
            field_type=FieldType.MULTILINE_TEXT,
            label="User Stories",
            description="User stories describing the feature from user perspective",
            required=False,
            placeholder="As a [user type], I want [goal] so that [benefit]",
            validation_rules=[ValidationRule.MIN_LENGTH_20],
            help_text="Use standard user story format: As a [user], I want [goal] so that [benefit]"
        )
        template.add_field(user_stories_field)
        
        # Add functional requirements field
        functional_requirements_field = TemplateField(
            name="functional_requirements",
            field_type=FieldType.MULTILINE_TEXT,
            label="Functional Requirements",
            description="Detailed functional requirements and specifications",
            required=True,
            placeholder="List all functional requirements with clear specifications",
            validation_rules=[ValidationRule.REQUIRED, ValidationRule.MIN_LENGTH_50],
            help_text="Include detailed functional requirements with clear acceptance criteria"
        )
        template.add_field(functional_requirements_field)
        
        # Add non-functional requirements field
        non_functional_requirements_field = TemplateField(
            name="non_functional_requirements",
            field_type=FieldType.MULTILINE_TEXT,
            label="Non-Functional Requirements",
            description="Performance, security, and other non-functional requirements",
            required=False,
            placeholder="Performance, security, scalability, usability requirements",
            validation_rules=[ValidationRule.MIN_LENGTH_20],
            help_text="Include performance, security, usability, and other quality requirements"
        )
        template.add_field(non_functional_requirements_field)
        
        # Add acceptance criteria field (if not already present)
        if not template.get_field_metadata("acceptance_criteria"):
            acceptance_criteria_field = TemplateField(
                name="acceptance_criteria",
                field_type=FieldType.MULTILINE_TEXT,
                label="Acceptance Criteria",
                description="Clear, testable acceptance criteria",
                required=True,
                placeholder="Given [context], when [action], then [result]",
                validation_rules=[ValidationRule.REQUIRED, ValidationRule.MIN_LENGTH_30],
                help_text="Use Given-When-Then format for clear, testable criteria"
            )
            template.add_field(acceptance_criteria_field)
        
        # Add edge cases field
        edge_cases_field = TemplateField(
            name="edge_cases",
            field_type=FieldType.MULTILINE_TEXT,
            label="Edge Cases",
            description="Edge cases and error scenarios to consider",
            required=False,
            placeholder="List edge cases, error scenarios, and boundary conditions",
            help_text="Consider error handling, boundary conditions, and unusual scenarios"
        )
        template.add_field(edge_cases_field)
        
        # Add assumptions field
        assumptions_field = TemplateField(
            name="assumptions",
            field_type=FieldType.MULTILINE_TEXT,
            label="Assumptions",
            description="Assumptions made during specification",
            required=False,
            placeholder="List assumptions about user behavior, system state, etc.",
            help_text="Document assumptions that could affect implementation"
        )
        template.add_field(assumptions_field)
        
        # Add constraints field
        constraints_field = TemplateField(
            name="constraints",
            field_type=FieldType.MULTILINE_TEXT,
            label="Constraints",
            description="Technical, business, or time constraints",
            required=False,
            placeholder="List constraints that limit implementation options",
            help_text="Include technical limitations, business rules, and time constraints"
        )
        template.add_field(constraints_field)
        
        # Add dependencies field (if not already present)
        if not template.get_field_metadata("dependencies"):
            dependencies_field = TemplateField(
                name="dependencies",
                field_type=FieldType.MULTILINE_TEXT,
                label="Dependencies",
                description="External dependencies and prerequisites",
                required=False,
                placeholder="List external systems, libraries, or other features required",
                help_text="Include both technical and business dependencies"
            )
            template.add_field(dependencies_field)
        
        # Add priority field
        priority_field = TemplateField(
            name="priority",
            field_type=FieldType.SELECT,
            label="Priority",
            description="Business priority of this specification",
            required=False,
            default_value="medium",
            options=[
                FieldOption("low", "Low", "Nice to have"),
                FieldOption("medium", "Medium", "Important"),
                FieldOption("high", "High", "Critical"),
                FieldOption("urgent", "Urgent", "Must have immediately")
            ]
        )
        template.add_field(priority_field)
        
        # Add business value field
        business_value_field = TemplateField(
            name="business_value",
            field_type=FieldType.MULTILINE_TEXT,
            label="Business Value",
            description="Business value and expected outcomes",
            required=False,
            placeholder="Describe the business value and expected outcomes",
            help_text="Explain how this feature provides value to users and business"
        )
        template.add_field(business_value_field)
        
        return template
    
    @staticmethod
    def validate_spec_template(template_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate specification-specific requirements.
        
        Args:
            template_data: Template data to validate
        
        Returns:
            Validation results with errors and warnings
        """
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        # Check for user story format
        user_stories = template_data.get("user_stories", "")
        if user_stories:
            if not SpecTemplate._validate_user_story_format(user_stories):
                validation_results["warnings"].append(
                    "User stories should follow standard format: 'As a [user], I want [goal] so that [benefit]'"
                )
        
        # Check for acceptance criteria format
        acceptance_criteria = template_data.get("acceptance_criteria", "")
        if acceptance_criteria:
            if not SpecTemplate._validate_acceptance_criteria_format(acceptance_criteria):
                validation_results["warnings"].append(
                    "Acceptance criteria should use Given-When-Then format"
                )
        
        # Check for functional requirements completeness
        functional_reqs = template_data.get("functional_requirements", "")
        if functional_reqs and len(functional_reqs) < 100:
            validation_results["suggestions"].append(
                "Functional requirements could be more detailed"
            )
        
        # Check for edge cases consideration
        if not template_data.get("edge_cases"):
            validation_results["suggestions"].append(
                "Consider adding edge cases and error scenarios"
            )
        
        # Check for assumptions documentation
        if not template_data.get("assumptions"):
            validation_results["suggestions"].append(
                "Document assumptions to avoid implementation issues"
            )
        
        return validation_results
    
    @staticmethod
    def _validate_user_story_format(user_stories: str) -> bool:
        """Validate user story format."""
        # Basic check for user story format
        lines = user_stories.split('\n')
        for line in lines:
            line = line.strip()
            if line and not (line.startswith('As a') and 'I want' in line and 'so that' in line):
                return False
        return True
    
    @staticmethod
    def _validate_acceptance_criteria_format(criteria: str) -> bool:
        """Validate acceptance criteria format."""
        # Basic check for Given-When-Then format
        lines = criteria.split('\n')
        for line in lines:
            line = line.strip()
            if line and not (line.startswith('Given') or line.startswith('When') or line.startswith('Then')):
                return False
        return True
    
    @staticmethod
    def generate_spec_content(template_data: Dict[str, Any]) -> str:
        """
        Generate specification content from template data.
        
        Args:
            template_data: Template data
        
        Returns:
            Formatted specification content
        """
        content_parts = []
        
        # Header
        title = template_data.get("title", "Feature Specification")
        content_parts.append(f"# {title}")
        content_parts.append("")
        
        # Description
        description = template_data.get("description", "")
        if description:
            content_parts.append("## Description")
            content_parts.append(description)
            content_parts.append("")
        
        # User Stories
        user_stories = template_data.get("user_stories", "")
        if user_stories:
            content_parts.append("## User Stories")
            content_parts.append(user_stories)
            content_parts.append("")
        
        # Functional Requirements
        functional_reqs = template_data.get("functional_requirements", "")
        if functional_reqs:
            content_parts.append("## Functional Requirements")
            content_parts.append(functional_reqs)
            content_parts.append("")
        
        # Non-Functional Requirements
        non_functional_reqs = template_data.get("non_functional_requirements", "")
        if non_functional_reqs:
            content_parts.append("## Non-Functional Requirements")
            content_parts.append(non_functional_reqs)
            content_parts.append("")
        
        # Acceptance Criteria
        acceptance_criteria = template_data.get("acceptance_criteria", "")
        if acceptance_criteria:
            content_parts.append("## Acceptance Criteria")
            content_parts.append(acceptance_criteria)
            content_parts.append("")
        
        # Edge Cases
        edge_cases = template_data.get("edge_cases", "")
        if edge_cases:
            content_parts.append("## Edge Cases")
            content_parts.append(edge_cases)
            content_parts.append("")
        
        # Assumptions
        assumptions = template_data.get("assumptions", "")
        if assumptions:
            content_parts.append("## Assumptions")
            content_parts.append(assumptions)
            content_parts.append("")
        
        # Constraints
        constraints = template_data.get("constraints", "")
        if constraints:
            content_parts.append("## Constraints")
            content_parts.append(constraints)
            content_parts.append("")
        
        # Dependencies
        dependencies = template_data.get("dependencies", "")
        if dependencies:
            content_parts.append("## Dependencies")
            content_parts.append(dependencies)
            content_parts.append("")
        
        # Business Value
        business_value = template_data.get("business_value", "")
        if business_value:
            content_parts.append("## Business Value")
            content_parts.append(business_value)
            content_parts.append("")
        
        # Priority
        priority = template_data.get("priority", "")
        if priority:
            content_parts.append("## Priority")
            content_parts.append(f"**Priority Level**: {priority.title()}")
            content_parts.append("")
        
        return "\n".join(content_parts)
