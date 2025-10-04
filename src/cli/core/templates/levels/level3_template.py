# src/cli/core/templates/levels/level3_template.py
"""
Level 3 Template - Intermediate Feature
Comprehensive template for intermediate features requiring planning and design.
"""

from ..base.base_template import BaseTemplate
from ..base.template_field import TemplateField, FieldType, ValidationRule, FieldOption


class Level3Template(BaseTemplate):
    """
    Level 3 Template for Intermediate Feature tasks.
    Comprehensive template with planning, architecture, and testing considerations.
    """
    
    def __init__(self):
        super().__init__(complexity_level=3, template_type="Intermediate Feature")
    
    def _initialize_template(self):
        """Initialize Level 3 template fields."""
        
        # Title field
        title_field = TemplateField(
            name="title",
            field_type=FieldType.TEXT,
            label="Title",
            description="Clear title describing the feature",
            required=True,
            placeholder="e.g., Implement user authentication system",
            validation_rules=[ValidationRule.REQUIRED, ValidationRule.MIN_LENGTH_10]
        )
        self.add_field(title_field)
        
        # Description field
        description_field = TemplateField(
            name="description",
            field_type=FieldType.MULTILINE_TEXT,
            label="Description",
            description="Comprehensive description of the feature and its purpose",
            required=True,
            placeholder="Describe the feature, its purpose, and how it fits into the overall system",
            validation_rules=[ValidationRule.REQUIRED, ValidationRule.MIN_LENGTH_100]
        )
        self.add_field(description_field)
        
        # Requirements field
        requirements_field = TemplateField(
            name="requirements",
            field_type=FieldType.MULTILINE_TEXT,
            label="Requirements",
            description="Detailed functional and non-functional requirements",
            required=True,
            placeholder="List all requirements including functional, performance, security, etc.",
            validation_rules=[ValidationRule.REQUIRED, ValidationRule.MIN_LENGTH_50],
            help_text="Use bullet points or numbered lists for clarity"
        )
        self.add_field(requirements_field)
        
        # Architecture field
        architecture_field = TemplateField(
            name="architecture",
            field_type=FieldType.MULTILINE_TEXT,
            label="Architecture",
            description="System architecture and design decisions",
            required=True,
            placeholder="Describe the architecture, components, and design patterns to be used",
            validation_rules=[ValidationRule.REQUIRED, ValidationRule.MIN_LENGTH_100]
        )
        self.add_field(architecture_field)
        
        # Dependencies field
        dependencies_field = TemplateField(
            name="dependencies",
            field_type=FieldType.MULTILINE_TEXT,
            label="Dependencies",
            description="External dependencies and prerequisites",
            required=True,
            placeholder="List all dependencies including libraries, services, database changes, etc.",
            validation_rules=[ValidationRule.REQUIRED],
            help_text="Include both technical and business dependencies"
        )
        self.add_field(dependencies_field)
        
        # Implementation phases field
        phases_field = TemplateField(
            name="implementation_phases",
            field_type=FieldType.MULTILINE_TEXT,
            label="Implementation Phases",
            description="Breakdown of implementation into logical phases",
            required=True,
            placeholder="List implementation phases with clear deliverables",
            validation_rules=[ValidationRule.REQUIRED, ValidationRule.MIN_LENGTH_50],
            help_text="Use numbered phases with clear milestones"
        )
        self.add_field(phases_field)
        
        # Testing strategy field
        testing_strategy_field = TemplateField(
            name="testing_strategy",
            field_type=FieldType.MULTILINE_TEXT,
            label="Testing Strategy",
            description="Comprehensive testing approach and strategy",
            required=True,
            placeholder="Describe unit tests, integration tests, and acceptance criteria",
            validation_rules=[ValidationRule.REQUIRED, ValidationRule.MIN_LENGTH_50]
        )
        self.add_field(testing_strategy_field)
        
        # Acceptance criteria field
        acceptance_criteria_field = TemplateField(
            name="acceptance_criteria",
            field_type=FieldType.MULTILINE_TEXT,
            label="Acceptance Criteria",
            description="Clear, testable acceptance criteria",
            required=True,
            placeholder="Define specific, measurable criteria for feature completion",
            validation_rules=[ValidationRule.REQUIRED, ValidationRule.MIN_LENGTH_30]
        )
        self.add_field(acceptance_criteria_field)
        
        # Creative phases field (conditional)
        creative_phases_field = TemplateField(
            name="creative_phases",
            field_type=FieldType.MULTILINE_TEXT,
            label="Creative Phases",
            description="Areas requiring creative design decisions",
            required=False,
            placeholder="Identify components that need design decisions or creative solutions",
            validation_rules=[ValidationRule.MIN_LENGTH_20],
            conditional_show="complexity_level",
            conditional_value=3
        )
        self.add_field(creative_phases_field)
        
        # Risk assessment field
        risk_assessment_field = TemplateField(
            name="risk_assessment",
            field_type=FieldType.MULTILINE_TEXT,
            label="Risk Assessment",
            description="Identified risks and mitigation strategies",
            required=False,
            placeholder="List potential risks and how they will be mitigated",
            help_text="Include technical, business, and timeline risks"
        )
        self.add_field(risk_assessment_field)
        
        # Performance considerations field
        performance_field = TemplateField(
            name="performance_considerations",
            field_type=FieldType.MULTILINE_TEXT,
            label="Performance Considerations",
            description="Performance requirements and optimization strategies",
            required=False,
            placeholder="Describe performance requirements and optimization approaches",
            help_text="Include response time, throughput, and scalability considerations"
        )
        self.add_field(performance_field)
        
        # Security considerations field
        security_field = TemplateField(
            name="security_considerations",
            field_type=FieldType.MULTILINE_TEXT,
            label="Security Considerations",
            description="Security requirements and considerations",
            required=False,
            placeholder="Describe security requirements, threats, and mitigation strategies",
            help_text="Include authentication, authorization, data protection, etc."
        )
        self.add_field(security_field)
        
        # Estimated effort field
        effort_field = TemplateField(
            name="estimated_effort",
            field_type=FieldType.SELECT,
            label="Estimated Effort",
            description="Estimated time to complete the feature",
            required=False,
            default_value="1-2 weeks",
            options=[
                FieldOption("3-5 days", "3-5 days", "Small feature"),
                FieldOption("1-2 weeks", "1-2 weeks", "Medium feature"),
                FieldOption("2-4 weeks", "2-4 weeks", "Large feature"),
                FieldOption("1+ months", "1+ months", "Very large feature")
            ]
        )
        self.add_field(effort_field)
        
        # Success metrics field
        success_metrics_field = TemplateField(
            name="success_metrics",
            field_type=FieldType.MULTILINE_TEXT,
            label="Success Metrics",
            description="Metrics to measure feature success",
            required=False,
            placeholder="Define measurable success criteria and KPIs",
            help_text="Include both technical and business metrics"
        )
        self.add_field(success_metrics_field)
    
    def get_template_summary(self) -> str:
        """Get a summary of this template."""
        return (
            "Level 3 Template - Intermediate Feature\n"
            "Comprehensive template for features requiring planning, architecture, and testing.\n"
            "Includes: Title, Description, Requirements, Architecture, Dependencies, "
            "Implementation Phases, Testing Strategy, Acceptance Criteria, Creative Phases, "
            "Risk Assessment, Performance & Security Considerations, Effort, Success Metrics\n"
            "Best for: New features, significant enhancements, integrations"
        )
    
    def get_expected_completion_time(self) -> str:
        """Get expected completion time for Level 3 tasks."""
        return "3 days to 1 month"
    
    def get_complexity_description(self) -> str:
        """Get description of Level 3 complexity."""
        return (
            "Intermediate Feature - Moderate complexity requiring comprehensive planning, "
            "architectural considerations, and structured implementation. "
            "May require creative phases for design decisions."
        )
