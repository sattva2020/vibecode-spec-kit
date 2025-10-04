# src/cli/core/templates/base/template_validator.py
"""
Template validation system for the Memory Bank template framework.
Provides comprehensive validation, scoring, and compliance checking.
"""

from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from .template_field import TemplateField, FieldType, ValidationRule


@dataclass
class ValidationResult:
    """Result of template validation."""
    is_valid: bool
    score: int
    max_score: int
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]
    missing_fields: List[str]
    incomplete_fields: List[str]


@dataclass
class ComplianceResult:
    """Result of compliance checking."""
    compliant: bool
    compliance_score: float
    violations: List[str]
    recommendations: List[str]


class TemplateValidator:
    """
    Comprehensive template validation system with scoring and compliance checking.
    """
    
    def __init__(self):
        self.validation_rules = self._initialize_validation_rules()
        self.scoring_weights = self._initialize_scoring_weights()
        self.compliance_standards = self._initialize_compliance_standards()
    
    def _initialize_validation_rules(self) -> Dict[str, List[str]]:
        """Initialize validation rules for different template types."""
        return {
            "spec": [
                "title_required",
                "description_min_length_50",
                "requirements_structured",
                "acceptance_criteria_defined"
            ],
            "plan": [
                "objectives_clear",
                "phases_defined",
                "dependencies_identified",
                "timeline_realistic"
            ],
            "task": [
                "title_required",
                "description_min_length_10",
                "acceptance_criteria_defined",
                "estimated_effort_provided"
            ]
        }
    
    def _initialize_scoring_weights(self) -> Dict[str, int]:
        """Initialize scoring weights for different quality aspects."""
        return {
            "completeness": 40,      # 40% of total score
            "quality": 30,           # 30% of total score
            "structure": 20,         # 20% of total score
            "compliance": 10         # 10% of total score
        }
    
    def _initialize_compliance_standards(self) -> Dict[str, List[str]]:
        """Initialize compliance standards for different template types."""
        return {
            "spec": [
                "user_story_format",
                "acceptance_criteria_present",
                "non_functional_requirements_considered",
                "edge_cases_identified"
            ],
            "plan": [
                "phases_logically_ordered",
                "dependencies_explicitly_stated",
                "risk_assessment_included",
                "success_metrics_defined"
            ],
            "task": [
                "clear_acceptance_criteria",
                "estimated_effort_provided",
                "dependencies_identified",
                "testing_strategy_included"
            ]
        }
    
    def validate_template(self, 
                         template_data: Dict[str, Any], 
                         fields: List[TemplateField],
                         template_type: str = "generic") -> ValidationResult:
        """
        Perform comprehensive validation of template data.
        
        Args:
            template_data: The data to validate
            fields: List of template fields with validation rules
            template_type: Type of template (spec, plan, task, etc.)
        
        Returns:
            ValidationResult with validation status and details
        """
        errors = []
        warnings = []
        suggestions = []
        missing_fields = []
        incomplete_fields = []
        
        # Validate individual fields
        field_scores = {}
        for field in fields:
            if field.should_show(template_data):
                value = template_data.get(field.name)
                is_valid, error_msg = field.validate_value(value)
                
                if not is_valid:
                    errors.append(f"{field.label}: {error_msg}")
                    if field.required:
                        missing_fields.append(field.name)
                    else:
                        incomplete_fields.append(field.name)
                
                # Calculate field quality score
                field_scores[field.name] = self._calculate_field_score(field, value)
        
        # Apply template-specific validation rules
        template_errors = self._validate_template_rules(template_data, template_type)
        errors.extend(template_errors)
        
        # Generate warnings and suggestions
        warnings = self._generate_warnings(template_data, fields)
        suggestions = self._generate_suggestions(template_data, fields, template_type)
        
        # Calculate overall score
        total_score = sum(field_scores.values())
        max_score = len(fields) * 100
        
        # Apply scoring weights
        weighted_score = self._apply_scoring_weights(total_score, max_score, template_data, fields)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            score=weighted_score,
            max_score=100,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            missing_fields=missing_fields,
            incomplete_fields=incomplete_fields
        )
    
    def _calculate_field_score(self, field: TemplateField, value: Any) -> int:
        """Calculate quality score for a single field."""
        if not value:
            return 0 if field.required else 50
        
        score = 50  # Base score for having a value
        
        # Bonus points for quality
        if isinstance(value, str):
            if len(value) >= 50:
                score += 30
            elif len(value) >= 20:
                score += 20
            elif len(value) >= 10:
                score += 10
            
            # Check for structure
            if '\n' in value or '-' in value or '*' in value:
                score += 10  # Structured content
        
        # Bonus points for required fields
        if field.required:
            score += 10
        
        return min(score, 100)
    
    def _validate_template_rules(self, data: Dict[str, Any], template_type: str) -> List[str]:
        """Validate template-specific rules."""
        errors = []
        rules = self.validation_rules.get(template_type, [])
        
        for rule in rules:
            if rule == "title_required" and not data.get("title"):
                errors.append("Title is required")
            elif rule == "description_min_length_50":
                desc = data.get("description", "")
                if len(desc) < 50:
                    errors.append("Description must be at least 50 characters long")
            elif rule == "requirements_structured":
                reqs = data.get("requirements", "")
                if reqs and not any(marker in reqs for marker in ["-", "*", "1.", "•"]):
                    errors.append("Requirements should be structured with bullet points or numbering")
            elif rule == "acceptance_criteria_defined":
                ac = data.get("acceptance_criteria", "")
                if not ac:
                    errors.append("Acceptance criteria must be defined")
            elif rule == "objectives_clear":
                obj = data.get("objectives", "")
                if not obj or len(obj) < 20:
                    errors.append("Objectives must be clear and detailed")
            elif rule == "phases_defined":
                phases = data.get("phases", [])
                if not phases:
                    errors.append("Implementation phases must be defined")
            elif rule == "dependencies_identified":
                deps = data.get("dependencies", [])
                if isinstance(deps, str) and not deps:
                    errors.append("Dependencies should be identified (use 'None' if none)")
            elif rule == "timeline_realistic":
                timeline = data.get("timeline", "")
                if timeline and "TBD" not in timeline and "TODO" not in timeline:
                    # Basic check for realistic timeline
                    pass  # Could add more sophisticated checks here
        
        return errors
    
    def _generate_warnings(self, data: Dict[str, Any], fields: List[TemplateField]) -> List[str]:
        """Generate warnings for potential issues."""
        warnings = []
        
        # Check for missing optional but recommended fields
        recommended_fields = ["testing_notes", "risks", "assumptions", "constraints"]
        for field_name in recommended_fields:
            if not data.get(field_name):
                warnings.append(f"Consider adding {field_name.replace('_', ' ')}")
        
        # Check for short descriptions
        description = data.get("description", "")
        if description and len(description) < 100:
            warnings.append("Description could be more detailed")
        
        # Check for missing technical details
        if data.get("complexity_level", 0) >= 3:
            if not data.get("architecture"):
                warnings.append("Architecture section recommended for complex tasks")
            if not data.get("dependencies"):
                warnings.append("Dependencies should be identified for complex tasks")
        
        return warnings
    
    def _generate_suggestions(self, data: Dict[str, Any], fields: List[TemplateField], template_type: str) -> List[str]:
        """Generate improvement suggestions."""
        suggestions = []
        
        # Template-specific suggestions
        if template_type == "spec":
            if not data.get("user_stories"):
                suggestions.append("Consider adding user stories for better requirement clarity")
            if not data.get("non_functional_requirements"):
                suggestions.append("Include non-functional requirements (performance, security, etc.)")
        
        elif template_type == "plan":
            if not data.get("risk_assessment"):
                suggestions.append("Add risk assessment and mitigation strategies")
            if not data.get("success_metrics"):
                suggestions.append("Define success metrics and acceptance criteria")
        
        elif template_type == "task":
            if not data.get("testing_strategy"):
                suggestions.append("Include testing strategy and approach")
            if not data.get("rollback_plan"):
                suggestions.append("Consider adding rollback plan for complex changes")
        
        # General suggestions
        if data.get("complexity_level", 0) >= 3:
            suggestions.append("Consider breaking down into smaller, manageable tasks")
            suggestions.append("Add creative phases for complex design decisions")
        
        return suggestions
    
    def _apply_scoring_weights(self, 
                              total_score: int, 
                              max_score: int, 
                              data: Dict[str, Any], 
                              fields: List[TemplateField]) -> int:
        """Apply scoring weights to calculate final weighted score."""
        # Calculate component scores
        completeness_score = self._calculate_completeness_score(data, fields)
        quality_score = self._calculate_quality_score(data, fields)
        structure_score = self._calculate_structure_score(data, fields)
        compliance_score = self._calculate_compliance_score(data, fields)
        
        # Apply weights
        weighted_score = (
            completeness_score * self.scoring_weights["completeness"] +
            quality_score * self.scoring_weights["quality"] +
            structure_score * self.scoring_weights["structure"] +
            compliance_score * self.scoring_weights["compliance"]
        ) / 100
        
        return int(weighted_score)
    
    def _calculate_completeness_score(self, data: Dict[str, Any], fields: List[TemplateField]) -> int:
        """Calculate completeness score (0-100)."""
        required_fields = [f for f in fields if f.required and f.should_show(data)]
        filled_required = sum(1 for f in required_fields if data.get(f.name))
        
        if not required_fields:
            return 100
        
        return int((filled_required / len(required_fields)) * 100)
    
    def _calculate_quality_score(self, data: Dict[str, Any], fields: List[TemplateField]) -> int:
        """Calculate quality score (0-100)."""
        quality_indicators = 0
        total_indicators = 0
        
        # Check description quality
        description = data.get("description", "")
        if description:
            total_indicators += 1
            if len(description) >= 50:
                quality_indicators += 1
        
        # Check for structured content
        structured_fields = ["requirements", "acceptance_criteria", "phases"]
        for field_name in structured_fields:
            value = data.get(field_name, "")
            if value:
                total_indicators += 1
                if any(marker in value for marker in ["-", "*", "1.", "•"]):
                    quality_indicators += 1
        
        # Check for technical details in complex tasks
        complexity = data.get("complexity_level", 0)
        if complexity >= 3:
            total_indicators += 1
            if data.get("architecture") or data.get("dependencies"):
                quality_indicators += 1
        
        return int((quality_indicators / total_indicators) * 100) if total_indicators > 0 else 50
    
    def _calculate_structure_score(self, data: Dict[str, Any], fields: List[TemplateField]) -> int:
        """Calculate structure score (0-100)."""
        structure_indicators = 0
        total_indicators = 0
        
        # Check for proper formatting
        text_fields = ["title", "description", "requirements"]
        for field_name in text_fields:
            value = data.get(field_name, "")
            if value:
                total_indicators += 1
                # Check for proper capitalization and formatting
                if value[0].isupper() and not value.endswith("."):
                    structure_indicators += 1
        
        # Check for logical organization
        if data.get("phases"):
            total_indicators += 1
            phases = data.get("phases", [])
            if isinstance(phases, list) and len(phases) > 1:
                structure_indicators += 1
        
        return int((structure_indicators / total_indicators) * 100) if total_indicators > 0 else 50
    
    def _calculate_compliance_score(self, data: Dict[str, Any], fields: List[TemplateField]) -> int:
        """Calculate compliance score (0-100)."""
        # For now, return a basic compliance score
        # This could be enhanced with more sophisticated compliance checking
        compliance_indicators = 0
        
        # Check for required elements
        if data.get("title") and data.get("description"):
            compliance_indicators += 1
        
        if data.get("acceptance_criteria"):
            compliance_indicators += 1
        
        if data.get("complexity_level", 0) >= 2:
            if data.get("dependencies") or data.get("phases"):
                compliance_indicators += 1
        
        return int((compliance_indicators / 3) * 100)
    
    def check_compliance(self, 
                        template_data: Dict[str, Any], 
                        template_type: str = "generic") -> ComplianceResult:
        """
        Check compliance with standards and best practices.
        
        Args:
            template_data: The data to check for compliance
            template_type: Type of template (spec, plan, task, etc.)
        
        Returns:
            ComplianceResult with compliance status and recommendations
        """
        violations = []
        recommendations = []
        standards = self.compliance_standards.get(template_type, [])
        
        for standard in standards:
            if standard == "user_story_format":
                if not self._check_user_story_format(template_data):
                    violations.append("User stories should follow standard format")
                    recommendations.append("Use format: 'As a [user], I want [goal] so that [benefit]'")
            
            elif standard == "acceptance_criteria_present":
                if not template_data.get("acceptance_criteria"):
                    violations.append("Acceptance criteria must be present")
                    recommendations.append("Define clear, testable acceptance criteria")
            
            elif standard == "phases_logically_ordered":
                phases = template_data.get("phases", [])
                if phases and not self._check_phases_order(phases):
                    violations.append("Implementation phases should be logically ordered")
                    recommendations.append("Order phases: Planning → Implementation → Testing → Deployment")
        
        # Calculate compliance score
        compliance_score = max(0, 100 - (len(violations) * 20))
        
        return ComplianceResult(
            compliant=len(violations) == 0,
            compliance_score=compliance_score,
            violations=violations,
            recommendations=recommendations
        )
    
    def _check_user_story_format(self, data: Dict[str, Any]) -> bool:
        """Check if user stories follow standard format."""
        user_stories = data.get("user_stories", "")
        if not user_stories:
            return True  # Not required for all templates
        
        # Basic check for user story format
        return "As a" in user_stories and "I want" in user_stories
    
    def _check_phases_order(self, phases: List[str]) -> bool:
        """Check if phases are logically ordered."""
        expected_order = ["planning", "implementation", "testing", "deployment"]
        phase_lower = [p.lower() for p in phases]
        
        # Check if phases follow expected order
        for i, expected in enumerate(expected_order):
            if i < len(phase_lower) and expected in phase_lower[i]:
                continue
            elif expected in phase_lower:
                return False
        
        return True
