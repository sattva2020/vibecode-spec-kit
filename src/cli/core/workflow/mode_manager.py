"""
Mode manager for workflow transitions with validation gates
"""

from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime
import json
from pathlib import Path

from ..config import CLIConfig
from ..memory_bank import MemoryBank
from .validation_gates import ValidationGate, ValidationResult, SpecDrivenValidator, ConstitutionalGate, ResearchGate, TestGate
from .documentation_automation import DocumentationAutomation


class ModeTransition:
    """Represents a mode transition with validation"""
    
    def __init__(self, from_mode: str, to_mode: str, 
                 validation_gates: List[ValidationGate] = None,
                 auto_document: bool = False):
        self.from_mode = from_mode
        self.to_mode = to_mode
        self.validation_gates = validation_gates or []
        self.auto_document = auto_document
        self.timestamp = datetime.now().isoformat()
    
    def add_validation_gate(self, gate: ValidationGate):
        """Add validation gate to transition"""
        self.validation_gates.append(gate)
    
    def validate_transition(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate transition through all gates"""
        results = {
            'transition': f"{self.from_mode} -> {self.to_mode}",
            'is_valid': True,
            'overall_score': 0.0,
            'gate_results': [],
            'errors': [],
            'warnings': [],
            'suggestions': [],
            'timestamp': self.timestamp
        }
        
        total_score = 0.0
        gate_count = len(self.validation_gates)
        
        for gate in self.validation_gates:
            gate_result = gate.validate(context)
            gate_info = {
                'gate_name': gate.name,
                'gate_description': gate.description,
                'is_valid': gate_result.is_valid,
                'score': gate_result.score,
                'errors': gate_result.errors,
                'warnings': gate_result.warnings,
                'suggestions': gate_result.suggestions
            }
            
            results['gate_results'].append(gate_info)
            
            if not gate_result.is_valid:
                results['is_valid'] = False
                results['errors'].extend(gate_result.errors)
            
            results['warnings'].extend(gate_result.warnings)
            results['suggestions'].extend(gate_result.suggestions)
            
            total_score += gate_result.score
        
        results['overall_score'] = total_score / gate_count if gate_count > 0 else 100.0
        
        return results


class ModeManager:
    """Manages Memory Bank mode transitions with validation gates"""
    
    def __init__(self, config: CLIConfig, memory_bank: MemoryBank):
        self.config = config
        self.memory_bank = memory_bank
        self.doc_automation = DocumentationAutomation(memory_bank)
        
        # Initialize validation gates
        self.spec_validator = SpecDrivenValidator()
        self.constitutional_gate = ConstitutionalGate()
        self.research_gate = ResearchGate()
        self.test_gate = TestGate()
        
        # Define mode transition rules
        self.transitions = self._setup_transitions()
    
    def _setup_transitions(self) -> Dict[str, ModeTransition]:
        """Setup mode transition rules with validation gates"""
        transitions = {}
        
        # VAN -> PLAN: Constitutional + Spec validation
        transitions['van->plan'] = ModeTransition(
            'van', 'plan',
            [self.constitutional_gate, self.spec_validator],
            auto_document=True
        )
        
        # PLAN -> CREATIVE: Constitutional + Research validation
        transitions['plan->creative'] = ModeTransition(
            'plan', 'creative',
            [self.constitutional_gate, self.research_gate],
            auto_document=True
        )
        
        # CREATIVE -> IMPLEMENT: Constitutional + Spec + Test validation
        transitions['creative->implement'] = ModeTransition(
            'creative', 'implement',
            [self.constitutional_gate, self.spec_validator, self.test_gate],
            auto_document=True
        )
        
        # IMPLEMENT -> REFLECT: Constitutional validation
        transitions['implement->reflect'] = ModeTransition(
            'implement', 'reflect',
            [self.constitutional_gate],
            auto_document=True
        )
        
        # REFLECT -> ARCHIVE: Constitutional + Spec validation
        transitions['reflect->archive'] = ModeTransition(
            'reflect', 'archive',
            [self.constitutional_gate, self.spec_validator],
            auto_document=True
        )
        
        # ARCHIVE -> VAN: Constitutional validation
        transitions['archive->van'] = ModeTransition(
            'archive', 'van',
            [self.constitutional_gate],
            auto_document=False
        )
        
        # Any -> QA: Test validation
        for mode in ['plan', 'creative', 'implement']:
            transitions[f'{mode}->qa'] = ModeTransition(
                mode, 'qa',
                [self.constitutional_gate, self.test_gate],
                auto_document=True
            )
        
        return transitions
    
    def can_transition(self, from_mode: str, to_mode: str, 
                      context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Check if mode transition is allowed"""
        transition_key = f"{from_mode}->{to_mode}"
        
        if transition_key not in self.transitions:
            return {
                'is_valid': True,
                'overall_score': 100.0,
                'gate_results': [],
                'errors': [],
                'warnings': [f"No specific validation rules for {from_mode} -> {to_mode}"],
                'suggestions': [],
                'timestamp': datetime.now().isoformat()
            }
        
        transition = self.transitions[transition_key]
        context = context or {}
        
        # Add mode information to context
        context.update({
            'current_mode': from_mode,
            'target_mode': to_mode,
            'has_specification': self._check_specification_exists(),
            'has_tests': self._check_tests_exist(),
            'requires_research': to_mode == 'creative',
            'requires_tests': to_mode == 'implement' or to_mode == 'qa'
        })
        
        return transition.validate_transition(context)
    
    def execute_transition(self, from_mode: str, to_mode: str, 
                          context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute mode transition with validation and documentation"""
        # Validate transition
        validation_result = self.can_transition(from_mode, to_mode, context)
        
        if not validation_result['is_valid']:
            return {
                'success': False,
                'error': 'Transition validation failed',
                'validation_result': validation_result
            }
        
        try:
            # Update Memory Bank state
            self.memory_bank.update_context({
                'current_mode': to_mode,
                'previous_mode': from_mode,
                'mode_transition_time': datetime.now().isoformat(),
                'transition_score': validation_result['overall_score']
            })
            
            # Auto-generate documentation if enabled
            transition_key = f"{from_mode}->{to_mode}"
            if (transition_key in self.transitions and 
                self.transitions[transition_key].auto_document):
                doc_result = self.doc_automation.generate_mode_transition_docs(
                    from_mode, to_mode, validation_result
                )
                validation_result['documentation_generated'] = doc_result
            
            return {
                'success': True,
                'validation_result': validation_result,
                'new_mode': to_mode,
                'previous_mode': from_mode
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Transition execution failed: {str(e)}',
                'validation_result': validation_result
            }
    
    def _check_specification_exists(self) -> bool:
        """Check if specification file exists"""
        spec_files = [
            'memory-bank/spec.md',
            'memory-bank/specification.md',
            'memory-bank/tasks.md'
        ]
        return any(Path(f).exists() for f in spec_files)
    
    def _check_tests_exist(self) -> bool:
        """Check if test files exist"""
        test_patterns = [
            '**/*.test.*',
            '**/*.spec.*',
            '**/tests/**/*',
            '**/test/**/*'
        ]
        
        for pattern in test_patterns:
            if list(Path('.').glob(pattern)):
                return True
        return False
    
    def get_transition_requirements(self, from_mode: str, to_mode: str) -> Dict[str, Any]:
        """Get requirements for mode transition"""
        transition_key = f"{from_mode}->{to_mode}"
        
        if transition_key not in self.transitions:
            return {
                'required_files': [],
                'required_checks': [],
                'recommended_actions': []
            }
        
        transition = self.transitions[transition_key]
        requirements = {
            'required_files': [],
            'required_checks': [],
            'recommended_actions': []
        }
        
        # Add requirements based on validation gates
        for gate in transition.validation_gates:
            if gate.name == 'spec_driven_validator':
                requirements['required_files'].append('specification.md')
                requirements['required_checks'].append('specification completeness')
            elif gate.name == 'constitutional_gate':
                requirements['required_checks'].append('constitutional compliance')
            elif gate.name == 'research_gate':
                requirements['required_files'].append('research.md')
                requirements['required_checks'].append('research completeness')
            elif gate.name == 'test_gate':
                requirements['required_files'].extend(['*.test.*', '*.spec.*'])
                requirements['required_checks'].append('test coverage')
        
        return requirements
