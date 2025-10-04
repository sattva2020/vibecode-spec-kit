"""
Validation gates for workflow transitions
"""

from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime
import json
from pathlib import Path

from ..config import CLIConfig
from ..memory_bank import MemoryBank
# from ..constitution import ConstitutionalValidator  # May not exist yet
from ..templates.engine.template_engine import TemplateEngine
from ..research.validation.research_validator import ResearchValidator


class ValidationResult:
    """Result of validation gate check"""
    
    def __init__(self, is_valid: bool, score: float = 0.0, 
                 errors: List[str] = None, warnings: List[str] = None,
                 suggestions: List[str] = None):
        self.is_valid = is_valid
        self.score = score
        self.errors = errors or []
        self.warnings = warnings or []
        self.suggestions = suggestions or []
        self.timestamp = datetime.now().isoformat()


class ValidationGate:
    """Base class for validation gates"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
    
    def validate(self, context: Dict[str, Any]) -> ValidationResult:
        """Validate context and return result"""
        raise NotImplementedError


class SpecDrivenValidator(ValidationGate):
    """Validates specification completeness before mode transitions"""
    
    def __init__(self):
        super().__init__(
            "spec_driven_validator",
            "Validates specification completeness and quality"
        )
        self.template_engine = TemplateEngine()
    
    def validate(self, context: Dict[str, Any]) -> ValidationResult:
        """Validate specification completeness"""
        errors = []
        warnings = []
        suggestions = []
        score = 0.0
        
        # Check if specification exists
        spec_file = context.get('spec_file')
        if not spec_file or not Path(spec_file).exists():
            errors.append("No specification file found")
            return ValidationResult(False, 0.0, errors)
        
        try:
            # Load and validate specification
            with open(spec_file, 'r', encoding='utf-8') as f:
                spec_data = json.load(f)
            
            # Validate specification structure
            validation_result = self.template_engine.validate_template(spec_data)
            
            if validation_result.is_valid:
                score = validation_result.score
                
                # Check for warnings and suggestions
                warnings.extend(validation_result.warnings)
                suggestions.extend(validation_result.suggestions)
                
                # Additional spec-specific checks
                if not spec_data.get('requirements'):
                    warnings.append("No requirements specified")
                    score -= 10
                
                if not spec_data.get('acceptance_criteria'):
                    warnings.append("No acceptance criteria defined")
                    score -= 15
                
                if not spec_data.get('test_strategy'):
                    warnings.append("No test strategy defined")
                    score -= 10
                    suggestions.append("Define test strategy before implementation")
                
            else:
                errors.extend(validation_result.errors)
                score = validation_result.score
            
        except Exception as e:
            errors.append(f"Failed to load specification: {str(e)}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            score=max(0, score),
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )


class ConstitutionalGate(ValidationGate):
    """Validates constitutional compliance before mode transitions"""
    
    def __init__(self):
        super().__init__(
            "constitutional_gate",
            "Validates constitutional compliance and principles"
        )
        # self.constitutional_validator = ConstitutionalValidator()  # May not exist yet
    
    def validate(self, context: Dict[str, Any]) -> ValidationResult:
        """Validate constitutional compliance"""
        errors = []
        warnings = []
        suggestions = []
        
        # Get current mode and target mode
        current_mode = context.get('current_mode', 'unknown')
        target_mode = context.get('target_mode', 'unknown')
        
        # Validate constitutional compliance
        # compliance_result = self.constitutional_validator.validate_mode_transition(
        #     current_mode, target_mode, context
        # )
        
        # if not compliance_result.is_compliant:
        #     errors.extend(compliance_result.violations)
        #     suggestions.extend(compliance_result.recommendations)
        
        # Basic constitutional validation for now
        if target_mode in ['implement', 'creative'] and not context.get('has_specification'):
            warnings.append("Constitutional recommendation: Specification recommended for complex modes")
        
        # Mode-specific constitutional checks
        if target_mode in ['implement', 'creative']:
            if not context.get('has_specification'):
                errors.append("Constitutional requirement: Specification required for implementation")
        
        if target_mode == 'qa':
            if not context.get('has_tests'):
                warnings.append("Constitutional recommendation: Tests should be available for QA")
                suggestions.append("Implement test-first approach")
        
        score = 100.0 if len(errors) == 0 else max(0, 100 - len(errors) * 20)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            score=score,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )


class ResearchGate(ValidationGate):
    """Validates research completeness before creative phases"""
    
    def __init__(self):
        super().__init__(
            "research_gate",
            "Validates research completeness and quality"
        )
        self.research_validator = ResearchValidator()
    
    def validate(self, context: Dict[str, Any]) -> ValidationResult:
        """Validate research completeness"""
        errors = []
        warnings = []
        suggestions = []
        score = 0.0
        
        # Check if research is required for this transition
        if context.get('requires_research', False):
            research_file = context.get('research_file')
            
            if not research_file or not Path(research_file).exists():
                errors.append("Research required but no research file found")
                return ValidationResult(False, 0.0, errors)
            
            try:
                # Load and validate research
                with open(research_file, 'r', encoding='utf-8') as f:
                    research_data = json.load(f)
                
                # Validate research quality
                validation_result = self.research_validator.validate_research(research_data)
                
                score = validation_result.get('score', 0)
                warnings.extend(validation_result.get('warnings', []))
                suggestions.extend(validation_result.get('suggestions', []))
                
                if validation_result.get('is_valid', False) == False:
                    errors.extend(validation_result.get('errors', []))
                
            except Exception as e:
                errors.append(f"Failed to validate research: {str(e)}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            score=score,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )


class TestGate(ValidationGate):
    """Validates test completeness before implementation"""
    
    def __init__(self):
        super().__init__(
            "test_gate",
            "Validates test completeness and coverage"
        )
    
    def validate(self, context: Dict[str, Any]) -> ValidationResult:
        """Validate test completeness"""
        errors = []
        warnings = []
        suggestions = []
        score = 0.0
        
        # Check if tests are required for this transition
        if context.get('requires_tests', False):
            test_files = context.get('test_files', [])
            
            if not test_files:
                errors.append("Test-first approach requires test files")
                suggestions.append("Create test files before implementation")
                return ValidationResult(False, 0.0, errors, warnings, suggestions)
            
            # Check test file existence and quality
            existing_tests = []
            for test_file in test_files:
                if Path(test_file).exists():
                    existing_tests.append(test_file)
            
            if not existing_tests:
                errors.append("No test files found")
            elif len(existing_tests) < len(test_files):
                warnings.append(f"Only {len(existing_tests)}/{len(test_files)} test files exist")
                score = (len(existing_tests) / len(test_files)) * 100
            else:
                score = 100.0
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            score=score,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )
