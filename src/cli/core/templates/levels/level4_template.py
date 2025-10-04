# src/cli/core/templates/levels/level4_template.py
"""
Level 4 Template - Complex System
Template for complex systems and enterprise-level features.
"""

from ..base.base_template import BaseTemplate
from ..base.template_field import TemplateField, FieldType, ValidationRule, FieldOption


class Level4Template(BaseTemplate):
    """
    Level 4 Template for Complex System tasks.
    Maximum complexity with comprehensive planning, architecture, and testing.
    """
    
    def __init__(self):
        super().__init__(complexity_level=4, template_type="Complex System")
    
    def _initialize_template(self):
        """Initialize Level 4 template fields."""
        
        # Title field
        title_field = TemplateField(
            name="title",
            field_type=FieldType.TEXT,
            label="Title",
            description="Comprehensive title describing the complex system",
            required=True,
            placeholder="e.g., Enterprise microservices architecture implementation",
            validation_rules=[ValidationRule.REQUIRED, ValidationRule.MIN_LENGTH_10]
        )
        self.add_field(title_field)
        
        # Description field
        description_field = TemplateField(
            name="description",
            field_type=FieldType.MULTILINE_TEXT,
            label="Description",
            description="Comprehensive description of the complex system and its scope",
            required=True,
            placeholder="Describe the system, its scope, and business impact",
            validation_rules=[ValidationRule.REQUIRED, ValidationRule.MIN_LENGTH_200]
        )
        self.add_field(description_field)
        
        # Requirements field
        requirements_field = TemplateField(
            name="requirements",
            field_type=FieldType.MULTILINE_TEXT,
            label="Requirements",
            description="Comprehensive functional and non-functional requirements",
            required=True,
            placeholder="List all requirements including functional, performance, security, scalability",
            validation_rules=[ValidationRule.REQUIRED, ValidationRule.MIN_LENGTH_100],
            help_text="Include both functional and non-functional requirements"
        )
        self.add_field(requirements_field)
        
        # System design field
        system_design_field = TemplateField(
            name="system_design",
            field_type=FieldType.MULTILINE_TEXT,
            label="System Design",
            description="High-level system design and architecture",
            required=True,
            placeholder="Describe the overall system architecture and design decisions",
            validation_rules=[ValidationRule.REQUIRED, ValidationRule.MIN_LENGTH_100]
        )
        self.add_field(system_design_field)
        
        # Architecture field
        architecture_field = TemplateField(
            name="architecture",
            field_type=FieldType.MULTILINE_TEXT,
            label="Architecture",
            description="Detailed system architecture and component design",
            required=True,
            placeholder="Describe detailed architecture, components, and design patterns",
            validation_rules=[ValidationRule.REQUIRED, ValidationRule.MIN_LENGTH_150]
        )
        self.add_field(architecture_field)
        
        # Dependencies field
        dependencies_field = TemplateField(
            name="dependencies",
            field_type=FieldType.MULTILINE_TEXT,
            label="Dependencies",
            description="Comprehensive dependencies and prerequisites",
            required=True,
            placeholder="List all dependencies including infrastructure, services, teams",
            validation_rules=[ValidationRule.REQUIRED, ValidationRule.MIN_LENGTH_50],
            help_text="Include technical, business, and organizational dependencies"
        )
        self.add_field(dependencies_field)
        
        # Implementation phases field
        phases_field = TemplateField(
            name="implementation_phases",
            field_type=FieldType.MULTILINE_TEXT,
            label="Implementation Phases",
            description="Detailed breakdown of implementation phases",
            required=True,
            placeholder="Break down implementation into detailed phases with milestones",
            validation_rules=[ValidationRule.REQUIRED, ValidationRule.MIN_LENGTH_100],
            help_text="Include phases, milestones, and deliverables"
        )
        self.add_field(phases_field)
        
        # Integration points field
        integration_points_field = TemplateField(
            name="integration_points",
            field_type=FieldType.MULTILINE_TEXT,
            label="Integration Points",
            description="System integration points and interfaces",
            required=True,
            placeholder="Describe all integration points and interfaces with other systems",
            validation_rules=[ValidationRule.REQUIRED, ValidationRule.MIN_LENGTH_50]
        )
        self.add_field(integration_points_field)
        
        # Performance considerations field
        performance_field = TemplateField(
            name="performance_considerations",
            field_type=FieldType.MULTILINE_TEXT,
            label="Performance Considerations",
            description="Performance requirements and optimization strategies",
            required=True,
            placeholder="Describe performance requirements, bottlenecks, and optimization strategies",
            validation_rules=[ValidationRule.REQUIRED, ValidationRule.MIN_LENGTH_50]
        )
        self.add_field(performance_field)
        
        # Security analysis field
        security_field = TemplateField(
            name="security_analysis",
            field_type=FieldType.MULTILINE_TEXT,
            label="Security Analysis",
            description="Security requirements and threat analysis",
            required=True,
            placeholder="Analyze security requirements, threats, and mitigation strategies",
            validation_rules=[ValidationRule.REQUIRED, ValidationRule.MIN_LENGTH_50]
        )
        self.add_field(security_field)
        
        # Testing strategy field
        testing_strategy_field = TemplateField(
            name="testing_strategy",
            field_type=FieldType.MULTILINE_TEXT,
            label="Testing Strategy",
            description="Comprehensive testing strategy and approach",
            required=True,
            placeholder="Describe comprehensive testing including unit, integration, system, and acceptance testing",
            validation_rules=[ValidationRule.REQUIRED, ValidationRule.MIN_LENGTH_100]
        )
        self.add_field(testing_strategy_field)
        
        # Risk assessment field
        risk_assessment_field = TemplateField(
            name="risk_assessment",
            field_type=FieldType.MULTILINE_TEXT,
            label="Risk Assessment",
            description="Comprehensive risk assessment and mitigation strategies",
            required=True,
            placeholder="Identify and assess risks including technical, business, and timeline risks",
            validation_rules=[ValidationRule.REQUIRED, ValidationRule.MIN_LENGTH_50]
        )
        self.add_field(risk_assessment_field)
        
        # Success metrics field
        success_metrics_field = TemplateField(
            name="success_metrics",
            field_type=FieldType.MULTILINE_TEXT,
            label="Success Metrics",
            description="Success metrics and KPIs for the system",
            required=True,
            placeholder="Define measurable success criteria and KPIs",
            validation_rules=[ValidationRule.REQUIRED, ValidationRule.MIN_LENGTH_30]
        )
        self.add_field(success_metrics_field)
        
        # Estimated effort field
        effort_field = TemplateField(
            name="estimated_effort",
            field_type=FieldType.SELECT,
            label="Estimated Effort",
            description="Estimated time to complete the complex system",
            required=False,
            default_value="2-6 months",
            options=[
                FieldOption("1-2 months", "1-2 months", "Large system"),
                FieldOption("2-6 months", "2-6 months", "Enterprise system"),
                FieldOption("6-12 months", "6-12 months", "Very large system"),
                FieldOption("1+ year", "1+ year", "Massive system")
            ]
        )
        self.add_field(effort_field)
    
    def get_template_summary(self) -> str:
        """Get a summary of this template."""
        return (
            "Level 4 Template - Complex System\n"
            "Maximum complexity template for enterprise systems and complex architectures.\n"
            "Includes: Title, Description, Requirements, System Design, Architecture, Dependencies, "
            "Implementation Phases, Integration Points, Performance, Security, Testing, Risk Assessment, Success Metrics, Effort\n"
            "Best for: Enterprise systems, microservices, complex architectures, platform development"
        )
    
    def get_expected_completion_time(self) -> str:
        """Get expected completion time for Level 4 tasks."""
        return "1 month to 1+ years"
    
    def get_complexity_description(self) -> str:
        """Get description of Level 4 complexity."""
        return (
            "Complex System - Maximum complexity requiring comprehensive planning, "
            "architecture design, and enterprise-level considerations. "
            "Requires multiple teams, extensive testing, and careful risk management."
        )
