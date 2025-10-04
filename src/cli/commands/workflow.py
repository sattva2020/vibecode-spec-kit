"""
Workflow commands for Memory Bank CLI
"""

import argparse
from typing import List, Dict, Any
import json
from pathlib import Path

from ..core.config import CLIConfig
from ..core.memory_bank import MemoryBank
from ..core.workflow import ModeManager, ModeTransition
from ..utils.output import OutputFormatter


class WorkflowCommand:
    """Base class for workflow commands"""
    
    def __init__(self):
        self.memory_bank = MemoryBank()
        self.mode_manager = None
    
    def _get_mode_manager(self, config: CLIConfig) -> ModeManager:
        """Get or create mode manager"""
        if self.mode_manager is None:
            self.mode_manager = ModeManager(config, self.memory_bank)
        return self.mode_manager
    
    @staticmethod
    def execute(args: argparse.Namespace, config: CLIConfig, formatter: OutputFormatter) -> int:
        """Execute workflow command"""
        formatter.info(f"🔧 {args.command.upper()} mode operations")
        formatter.info("Workflow command placeholder - implementation coming soon")
        return 0


class VANCommand(WorkflowCommand):
    """VAN mode command with validation gates"""
    
    def execute(self, args: argparse.Namespace, config: CLIConfig, formatter: OutputFormatter) -> int:
        """Execute VAN mode with validation"""
        formatter.info("🚀 VAN Mode: Initialization and Validation")
        
        mode_manager = self._get_mode_manager(config)
        
        # Check current state
        context = self.memory_bank.get_context()
        current_mode = context.get('current_mode', 'unknown')
        
        if current_mode != 'van':
            # Validate transition to VAN mode
            validation_result = mode_manager.can_transition(current_mode, 'van')
            
            if not validation_result['is_valid']:
                formatter.error("❌ Transition to VAN mode failed validation:")
                for error in validation_result['errors']:
                    formatter.error(f"  - {error}")
                return 1
            
            if validation_result['warnings']:
                formatter.warning("⚠️  VAN mode transition warnings:")
                for warning in validation_result['warnings']:
                    formatter.warning(f"  - {warning}")
        
        # Execute VAN mode operations
        formatter.info("✅ VAN Mode: Initialization complete")
        formatter.info("📊 System ready for planning phase")
        
        return 0


class PlanCommand(WorkflowCommand):
    """PLAN mode command with spec validation"""
    
    def execute(self, args: argparse.Namespace, config: CLIConfig, formatter: OutputFormatter) -> int:
        """Execute PLAN mode with spec-driven validation"""
        formatter.info("📋 PLAN Mode: Specification-Driven Planning")
        
        mode_manager = self._get_mode_manager(config)
        
        # Validate transition to PLAN mode
        context = self.memory_bank.get_context()
        current_mode = context.get('current_mode', 'van')
        
        validation_result = mode_manager.can_transition(current_mode, 'plan')
        
        if not validation_result['is_valid']:
            formatter.error("❌ Transition to PLAN mode failed validation:")
            for error in validation_result['errors']:
                formatter.error(f"  - {error}")
            
            # Show requirements
            requirements = mode_manager.get_transition_requirements(current_mode, 'plan')
            if requirements['required_files']:
                formatter.info("📄 Required files:")
                for file_req in requirements['required_files']:
                    formatter.info(f"  - {file_req}")
            
            return 1
        
        # Execute transition
        transition_result = mode_manager.execute_transition(current_mode, 'plan')
        
        if transition_result['success']:
            formatter.success("✅ PLAN Mode: Transition successful")
            formatter.info(f"📊 Validation Score: {validation_result['overall_score']:.1f}/100")
            
            if validation_result['suggestions']:
                formatter.info("💡 Suggestions:")
                for suggestion in validation_result['suggestions']:
                    formatter.info(f"  - {suggestion}")
        else:
            formatter.error(f"❌ PLAN Mode transition failed: {transition_result['error']}")
            return 1
        
        return 0


class CreativeCommand(WorkflowCommand):
    """CREATIVE mode command with research validation"""
    
    def execute(self, args: argparse.Namespace, config: CLIConfig, formatter: OutputFormatter) -> int:
        """Execute CREATIVE mode with research validation"""
        formatter.info("🎨 CREATIVE Mode: Design and Research")
        
        mode_manager = self._get_mode_manager(config)
        
        # Validate transition to CREATIVE mode
        context = self.memory_bank.get_context()
        current_mode = context.get('current_mode', 'plan')
        
        validation_result = mode_manager.can_transition(current_mode, 'creative')
        
        if not validation_result['is_valid']:
            formatter.error("❌ Transition to CREATIVE mode failed validation:")
            for error in validation_result['errors']:
                formatter.error(f"  - {error}")
            return 1
        
        # Execute transition
        transition_result = mode_manager.execute_transition(current_mode, 'creative')
        
        if transition_result['success']:
            formatter.success("✅ CREATIVE Mode: Transition successful")
            formatter.info(f"📊 Validation Score: {validation_result['overall_score']:.1f}/100")
            
            if args.research:
                formatter.info("🔍 Research integration enabled")
                # Trigger research workflow
                self._trigger_research_workflow(formatter)
        else:
            formatter.error(f"❌ CREATIVE Mode transition failed: {transition_result['error']}")
            return 1
        
        return 0
    
    def _trigger_research_workflow(self, formatter: OutputFormatter):
        """Trigger research workflow"""
        formatter.info("🔬 Starting research workflow...")
        formatter.info("💡 Use 'memory-bank research generate' to create research templates")


class ImplementCommand(WorkflowCommand):
    """IMPLEMENT mode command with test validation"""
    
    def execute(self, args: argparse.Namespace, config: CLIConfig, formatter: OutputFormatter) -> int:
        """Execute IMPLEMENT mode with test-first validation"""
        formatter.info("🔨 IMPLEMENT Mode: Test-First Implementation")
        
        mode_manager = self._get_mode_manager(config)
        
        # Validate transition to IMPLEMENT mode
        context = self.memory_bank.get_context()
        current_mode = context.get('current_mode', 'creative')
        
        validation_result = mode_manager.can_transition(current_mode, 'implement')
        
        if not validation_result['is_valid']:
            formatter.error("❌ Transition to IMPLEMENT mode failed validation:")
            for error in validation_result['errors']:
                formatter.error(f"  - {error}")
            
            if args.test_first:
                formatter.info("🧪 Test-First approach enabled - tests required")
            
            return 1
        
        # Execute transition
        transition_result = mode_manager.execute_transition(current_mode, 'implement')
        
        if transition_result['success']:
            formatter.success("✅ IMPLEMENT Mode: Transition successful")
            formatter.info(f"📊 Validation Score: {validation_result['overall_score']:.1f}/100")
            
            if args.test_first:
                formatter.info("🧪 Test-First Implementation enabled")
            
            if args.contract_tests:
                formatter.info("📋 Contract testing enabled")
        else:
            formatter.error(f"❌ IMPLEMENT Mode transition failed: {transition_result['error']}")
            return 1
        
        return 0


class ReflectCommand(WorkflowCommand):
    """REFLECT mode command with documentation automation"""
    
    def execute(self, args: argparse.Namespace, config: CLIConfig, formatter: OutputFormatter) -> int:
        """Execute REFLECT mode with documentation automation"""
        formatter.info("🤔 REFLECT Mode: Analysis and Learning")
        
        mode_manager = self._get_mode_manager(config)
        
        # Validate transition to REFLECT mode
        context = self.memory_bank.get_context()
        current_mode = context.get('current_mode', 'implement')
        
        validation_result = mode_manager.can_transition(current_mode, 'reflect')
        
        if not validation_result['is_valid']:
            formatter.error("❌ Transition to REFLECT mode failed validation:")
            for error in validation_result['errors']:
                formatter.error(f"  - {error}")
            return 1
        
        # Execute transition
        transition_result = mode_manager.execute_transition(current_mode, 'reflect')
        
        if transition_result['success']:
            formatter.success("✅ REFLECT Mode: Transition successful")
            formatter.info(f"📊 Validation Score: {validation_result['overall_score']:.1f}/100")
            
            if args.learning:
                formatter.info("📚 Learning capture enabled")
            
            if args.documentation:
                formatter.info("📝 Documentation update enabled")
        else:
            formatter.error(f"❌ REFLECT Mode transition failed: {transition_result['error']}")
            return 1
        
        return 0


class ArchiveCommand(WorkflowCommand):
    """ARCHIVE mode command with spec validation"""
    
    def execute(self, args: argparse.Namespace, config: CLIConfig, formatter: OutputFormatter) -> int:
        """Execute ARCHIVE mode with specification validation"""
        formatter.info("📦 ARCHIVE Mode: Documentation and Archiving")
        
        mode_manager = self._get_mode_manager(config)
        
        # Validate transition to ARCHIVE mode
        context = self.memory_bank.get_context()
        current_mode = context.get('current_mode', 'reflect')
        
        validation_result = mode_manager.can_transition(current_mode, 'archive')
        
        if not validation_result['is_valid']:
            formatter.error("❌ Transition to ARCHIVE mode failed validation:")
            for error in validation_result['errors']:
                formatter.error(f"  - {error}")
            return 1
        
        # Execute transition
        transition_result = mode_manager.execute_transition(current_mode, 'archive')
        
        if transition_result['success']:
            formatter.success("✅ ARCHIVE Mode: Transition successful")
            formatter.info(f"📊 Validation Score: {validation_result['overall_score']:.1f}/100")
            
            if args.spec_docs:
                formatter.info("📋 Spec documentation archiving enabled")
            
            if args.constitutional:
                formatter.info("⚖️  Constitutional decisions archiving enabled")
        else:
            formatter.error(f"❌ ARCHIVE Mode transition failed: {transition_result['error']}")
            return 1
        
        return 0


class SyncCommand(WorkflowCommand):
    """SYNC mode command"""
    
    def execute(self, args: argparse.Namespace, config: CLIConfig, formatter: OutputFormatter) -> int:
        """Execute SYNC mode"""
        formatter.info("🔄 SYNC Mode: Multi-AI Agent Synchronization")
        
        if args.multi_ai:
            formatter.info("🤖 Multi-AI agent sync enabled")
        
        if args.documentation:
            formatter.info("📝 Documentation sync enabled")
        
        return 0


class QACommand(WorkflowCommand):
    """QA mode command with test validation"""
    
    def execute(self, args: argparse.Namespace, config: CLIConfig, formatter: OutputFormatter) -> int:
        """Execute QA mode with test validation"""
        formatter.info("🧪 QA Mode: Quality Assurance and Testing")
        
        mode_manager = self._get_mode_manager(config)
        
        # Get current mode for validation
        context = self.memory_bank.get_context()
        current_mode = context.get('current_mode', 'implement')
        
        # Validate transition to QA mode
        validation_result = mode_manager.can_transition(current_mode, 'qa')
        
        if not validation_result['is_valid']:
            formatter.error("❌ Transition to QA mode failed validation:")
            for error in validation_result['errors']:
                formatter.error(f"  - {error}")
            return 1
        
        # Execute transition
        transition_result = mode_manager.execute_transition(current_mode, 'qa')
        
        if transition_result['success']:
            formatter.success("✅ QA Mode: Transition successful")
            formatter.info(f"📊 Validation Score: {validation_result['overall_score']:.1f}/100")
            
            if args.contract_tests:
                formatter.info("📋 Contract testing enabled")
            
            if args.constitutional:
                formatter.info("⚖️  Constitutional compliance validation enabled")
        else:
            formatter.error(f"❌ QA Mode transition failed: {transition_result['error']}")
            return 1
        
        return 0


# Create command instances
van_command = VANCommand()
plan_command = PlanCommand()
creative_command = CreativeCommand()
implement_command = ImplementCommand()
reflect_command = ReflectCommand()
archive_command = ArchiveCommand()
sync_command = SyncCommand()
qa_command = QACommand()
