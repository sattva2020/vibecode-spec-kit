"""
Status command for Memory Bank CLI
"""

import argparse
import json
from pathlib import Path

from ..core.config import CLIConfig
from ..core.memory_bank import MemoryBank
from ..utils.output import OutputFormatter


class StatusCommand:
    """Show Memory Bank status overview"""
    
    @staticmethod
    def execute(args: argparse.Namespace, config: CLIConfig, formatter: OutputFormatter) -> int:
        """Execute status command"""
        try:
            # Create Memory Bank instance
            memory_bank = MemoryBank(config.memory_bank_path)
            status = memory_bank.get_status()
            
            if args.json:
                # Output in JSON format
                status_data = {
                    "initialized": status.initialized,
                    "memory_bank_path": str(status.memory_bank_path),
                    "essential_files": status.essential_files,
                    "subdirectories": status.subdirectories,
                    "template_files": status.template_files,
                    "constitutional_file": status.constitutional_file,
                    "issues": status.issues,
                    "health_status": status.is_healthy()
                }
                formatter.output(json.dumps(status_data, indent=2))
                return 0
            
            # Regular text output
            formatter.info("📊 Memory Bank Status")
            formatter.info("=" * 40)
            
            if status.memory_bank_path.exists():
                formatter.info(f"📁 Memory Bank: {status.memory_bank_path}")
                
                # Health status
                health_icon = "✅" if status.is_healthy() else "❌"
                health_text = "Healthy" if status.is_healthy() else "Issues Found"
                formatter.info(f"🏥 Health: {health_icon} {health_text}")
                
                # Essential files count
                essential_count = sum(1 for exists in status.essential_files.values() if exists)
                total_essential = len(status.essential_files)
                formatter.info(f"📄 Essential files: {essential_count}/{total_essential}")
                
                # Subdirectories count
                subdir_count = sum(1 for exists in status.subdirectories.values() if exists)
                total_subdirs = len(status.subdirectories)
                formatter.info(f"📁 Subdirectories: {subdir_count}/{total_subdirs}")
                
                # Template files count
                template_count = sum(1 for exists in status.template_files.values() if exists)
                total_templates = len(status.template_files)
                formatter.info(f"📋 Template files: {template_count}/{total_templates}")
                
                # Constitutional file
                constitution_icon = "✅" if status.constitutional_file else "❌"
                formatter.info(f"📜 Constitutional file: {constitution_icon}")
                
                # Show detailed information if requested
                if args.detailed:
                    StatusCommand._show_detailed_status(status, formatter)
                
                # Show issues if any
                if status.issues:
                    formatter.warning("⚠️  Issues found:")
                    for issue in status.issues:
                        formatter.warning(f"  - {issue}")
                
                # Show AI agents
                enabled_agents = config.get_enabled_ai_agents()
                formatter.info(f"🤖 AI agents: {', '.join(enabled_agents)}")
                
                # Show configuration summary
                if args.detailed:
                    StatusCommand._show_configuration_summary(config, formatter)
                
            else:
                formatter.error("❌ Memory Bank not found")
                formatter.info("Run 'memory-bank init' to initialize")
                return 1
            
            return 0
            
        except Exception as e:
            formatter.error(f"❌ Status check failed: {str(e)}")
            if args.verbose:
                formatter.debug(f"Exception details: {e}", exc_info=True)
            return 1
    
    @staticmethod
    def _show_detailed_status(status, formatter: OutputFormatter):
        """Show detailed status information"""
        formatter.info("\n📋 Detailed Status:")
        
        # Essential files
        formatter.info("  📄 Essential files:")
        for file_name, exists in status.essential_files.items():
            status_icon = "✅" if exists else "❌"
            formatter.info(f"    {status_icon} {file_name}")
        
        # Subdirectories
        formatter.info("  📁 Subdirectories:")
        for subdir, exists in status.subdirectories.items():
            status_icon = "✅" if exists else "❌"
            formatter.info(f"    {status_icon} {subdir}/")
        
        # Template files
        formatter.info("  📋 Template files:")
        for template_name, exists in status.template_files.items():
            status_icon = "✅" if exists else "❌"
            formatter.info(f"    {status_icon} {template_name}")
    
    @staticmethod
    def _show_configuration_summary(config: CLIConfig, formatter: OutputFormatter):
        """Show configuration summary"""
        formatter.info("\n⚙️  Configuration Summary:")
        
        # Constitutional settings
        constitutional_status = "Enabled" if config.is_constitutional_mode_enabled() else "Disabled"
        formatter.info(f"  📜 Constitutional gates: {constitutional_status}")
        if config.is_constitutional_mode_enabled():
            formatter.info(f"    Strictness: {config.constitutional_strictness}")
        
        # Spec-Driven settings
        spec_status = "Enabled" if config.spec_driven_mode else "Disabled"
        formatter.info(f"  📋 Spec-Driven mode: {spec_status}")
        if config.spec_driven_mode:
            formatter.info(f"    Min level: {config.spec_driven_min_level}")
        
        # Test-First settings
        test_status = "Enabled" if config.test_first else "Disabled"
        formatter.info(f"  🧪 Test-First mode: {test_status}")
        if config.test_first:
            formatter.info(f"    Min level: {config.test_first_min_level}")
        
        # Multi-AI settings
        ai_status = "Enabled" if config.multi_ai_enabled else "Disabled"
        formatter.info(f"  🤖 Multi-AI support: {ai_status}")
        if config.multi_ai_enabled:
            formatter.info(f"    Coordination: {config.ai_coordination}")
        
        # Performance settings
        formatter.info(f"  ⚡ Lazy loading: {'Enabled' if config.lazy_loading else 'Disabled'}")
        formatter.info(f"  🔄 Conditional validation: {'Enabled' if config.conditional_validation else 'Disabled'}")


# Create command instance
status_command = StatusCommand()
