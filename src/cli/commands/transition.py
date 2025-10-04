"""
Transition management commands for Memory Bank CLI
"""

import argparse
from typing import Dict, Any

from ..core.config import CLIConfig
from ..core.memory_bank import MemoryBank
from ..core.workflow import ModeManager
from ..utils.output import OutputFormatter


class TransitionCommand:
    """Commands for managing mode transitions"""
    
    def __init__(self):
        self.memory_bank = MemoryBank()
        self.mode_manager = None
    
    def _get_mode_manager(self, config: CLIConfig) -> ModeManager:
        """Get or create mode manager"""
        if self.mode_manager is None:
            self.mode_manager = ModeManager(config, self.memory_bank)
        return self.mode_manager
    
    def execute(self, args: argparse.Namespace, config: CLIConfig, formatter: OutputFormatter) -> int:
        """Execute transition command"""
        try:
            if args.transition_action == 'check':
                return self._check_transition(args, config, formatter)
            elif args.transition_action == 'requirements':
                return self._show_requirements(args, config, formatter)
            elif args.transition_action == 'execute':
                return self._execute_transition(args, config, formatter)
            elif args.transition_action == 'list':
                return self._list_transitions(args, config, formatter)
            else:
                formatter.error(f"Unknown transition action: {args.transition_action}")
                return 1
        except Exception as e:
            formatter.error(f"Transition command failed: {e}")
            return 1
    
    def _check_transition(self, args: argparse.Namespace, config: CLIConfig, formatter: OutputFormatter) -> int:
        """Check if transition is possible"""
        mode_manager = self._get_mode_manager(config)
        
        from_mode = args.from_mode
        to_mode = args.to_mode
        
        formatter.info(f"🔍 Checking transition: {from_mode} → {to_mode}")
        
        # Validate transition
        validation_result = mode_manager.can_transition(from_mode, to_mode)
        
        if validation_result['is_valid']:
            formatter.success(f"✅ Transition {from_mode} → {to_mode} is VALID")
            formatter.info(f"📊 Overall Score: {validation_result['overall_score']:.1f}/100")
        else:
            formatter.error(f"❌ Transition {from_mode} → {to_mode} is INVALID")
        
        # Show validation details
        if validation_result['gate_results']:
            formatter.info("\n📋 Validation Gate Results:")
            for gate_result in validation_result['gate_results']:
                status = "✅" if gate_result['is_valid'] else "❌"
                formatter.info(f"  {status} {gate_result['gate_name']}: {gate_result['score']:.1f}/100")
                
                if gate_result['errors']:
                    for error in gate_result['errors']:
                        formatter.error(f"    - {error}")
                
                if gate_result['warnings']:
                    for warning in gate_result['warnings']:
                        formatter.warning(f"    - {warning}")
                
                if gate_result['suggestions']:
                    for suggestion in gate_result['suggestions']:
                        formatter.info(f"    💡 {suggestion}")
        
        # Show general warnings and suggestions
        if validation_result['warnings']:
            formatter.warning("\n⚠️  General Warnings:")
            for warning in validation_result['warnings']:
                formatter.warning(f"  - {warning}")
        
        if validation_result['suggestions']:
            formatter.info("\n💡 Suggestions:")
            for suggestion in validation_result['suggestions']:
                formatter.info(f"  - {suggestion}")
        
        return 0 if validation_result['is_valid'] else 1
    
    def _show_requirements(self, args: argparse.Namespace, config: CLIConfig, formatter: OutputFormatter) -> int:
        """Show requirements for transition"""
        mode_manager = self._get_mode_manager(config)
        
        from_mode = args.from_mode
        to_mode = args.to_mode
        
        formatter.info(f"📋 Requirements for transition: {from_mode} → {to_mode}")
        
        requirements = mode_manager.get_transition_requirements(from_mode, to_mode)
        
        if requirements['required_files']:
            formatter.info("\n📄 Required Files:")
            for file_req in requirements['required_files']:
                formatter.info(f"  - {file_req}")
        
        if requirements['required_checks']:
            formatter.info("\n✅ Required Checks:")
            for check in requirements['required_checks']:
                formatter.info(f"  - {check}")
        
        if requirements['recommended_actions']:
            formatter.info("\n💡 Recommended Actions:")
            for action in requirements['recommended_actions']:
                formatter.info(f"  - {action}")
        
        if not any([requirements['required_files'], requirements['required_checks'], requirements['recommended_actions']]):
            formatter.info("No specific requirements for this transition")
        
        return 0
    
    def _execute_transition(self, args: argparse.Namespace, config: CLIConfig, formatter: OutputFormatter) -> int:
        """Execute mode transition"""
        mode_manager = self._get_mode_manager(config)
        
        from_mode = args.from_mode
        to_mode = args.to_mode
        
        formatter.info(f"🚀 Executing transition: {from_mode} → {to_mode}")
        
        # Execute transition
        result = mode_manager.execute_transition(from_mode, to_mode)
        
        if result['success']:
            formatter.success(f"✅ Transition {from_mode} → {to_mode} executed successfully")
            formatter.info(f"📊 Validation Score: {result['validation_result']['overall_score']:.1f}/100")
            
            if 'documentation_generated' in result['validation_result']:
                formatter.info("📝 Documentation generated automatically")
        else:
            formatter.error(f"❌ Transition failed: {result['error']}")
            return 1
        
        return 0
    
    def _list_transitions(self, args: argparse.Namespace, config: CLIConfig, formatter: OutputFormatter) -> int:
        """List available transitions"""
        mode_manager = self._get_mode_manager(config)
        
        formatter.info("🔄 Available Mode Transitions:")
        
        transitions = [
            ("van", "plan", "Initialization → Planning"),
            ("plan", "creative", "Planning → Creative Design"),
            ("creative", "implement", "Creative → Implementation"),
            ("implement", "reflect", "Implementation → Reflection"),
            ("reflect", "archive", "Reflection → Archiving"),
            ("archive", "van", "Archiving → New Task"),
            ("plan", "qa", "Planning → Quality Assurance"),
            ("creative", "qa", "Creative → Quality Assurance"),
            ("implement", "qa", "Implementation → Quality Assurance")
        ]
        
        for from_mode, to_mode, description in transitions:
            # Check if transition is available
            validation_result = mode_manager.can_transition(from_mode, to_mode)
            status = "✅" if validation_result['is_valid'] else "❌"
            
            formatter.info(f"  {status} {from_mode} → {to_mode}: {description}")
            
            if not validation_result['is_valid'] and validation_result['errors']:
                for error in validation_result['errors'][:2]:  # Show first 2 errors
                    formatter.info(f"      - {error}")
        
        return 0


# Create command instance
transition_command = TransitionCommand()

__all__ = ['transition_command']
