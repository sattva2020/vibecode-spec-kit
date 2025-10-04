"""
Check command for Memory Bank CLI
"""

import argparse
from typing import List

from ..core.config import CLIConfig
from ..core.memory_bank import MemoryBank
from ..core.constitution import ConstitutionalValidator
from ..utils.output import OutputFormatter


class CheckCommand:
    """Check Memory Bank status and health"""
    
    @staticmethod
    def execute(args: argparse.Namespace, config: CLIConfig, formatter: OutputFormatter) -> int:
        """Execute check command"""
        try:
            formatter.info("🔍 Checking Memory Bank status...")
            
            # Create Memory Bank instance
            memory_bank = MemoryBank(config.memory_bank_path)
            status = memory_bank.get_status()
            
            # Check basic structure
            if not status.initialized:
                formatter.error("❌ Memory Bank not initialized")
                for issue in status.issues:
                    formatter.error(f"  - {issue}")
                return 1
            
            formatter.success("✅ Memory Bank structure is valid")
            
            # Additional checks based on arguments
            checks_passed = True
            
            if args.constitutional:
                if not CheckCommand._check_constitutional(config, formatter):
                    checks_passed = False
            
            if args.templates:
                if not CheckCommand._check_templates(status, formatter):
                    checks_passed = False
            
            if args.ai_agents:
                if not CheckCommand._check_ai_agents(config, formatter):
                    checks_passed = False
            
            # Show detailed status if verbose
            if args.verbose:
                CheckCommand._show_detailed_status(status, formatter)
            
            return 0 if checks_passed else 1
            
        except Exception as e:
            formatter.error(f"❌ Check failed: {str(e)}")
            if args.verbose:
                formatter.debug(f"Exception details: {e}", exc_info=True)
            return 1
    
    @staticmethod
    def _check_constitutional(config: CLIConfig, formatter: OutputFormatter) -> bool:
        """Check constitutional compliance"""
        try:
            validator = ConstitutionalValidator(config.memory_bank_path)
            is_valid = validator.validate_constitution()
            
            if is_valid:
                formatter.success("✅ Constitutional compliance verified")
                return True
            else:
                formatter.warning("⚠️  Constitutional compliance issues found")
                return False
                
        except Exception as e:
            formatter.error(f"❌ Constitutional check failed: {str(e)}")
            return False
    
    @staticmethod
    def _check_templates(status, formatter: OutputFormatter) -> bool:
        """Check template files"""
        missing_templates = []
        
        for template_name, exists in status.template_files.items():
            if not exists:
                missing_templates.append(template_name)
        
        if not missing_templates:
            formatter.success("✅ All template files present")
            return True
        else:
            formatter.warning("⚠️  Missing template files:")
            for template in missing_templates:
                formatter.warning(f"  - {template}")
            return False
    
    @staticmethod
    def _check_ai_agents(config: CLIConfig, formatter: OutputFormatter) -> bool:
        """Check AI agent configuration"""
        try:
            enabled_agents = config.get_enabled_ai_agents()
            
            if enabled_agents:
                formatter.success(f"✅ AI agents configured: {', '.join(enabled_agents)}")
                return True
            else:
                formatter.warning("⚠️  No AI agents configured")
                return False
                
        except Exception as e:
            formatter.error(f"❌ AI agent check failed: {str(e)}")
            return False
    
    @staticmethod
    def _show_detailed_status(status, formatter: OutputFormatter):
        """Show detailed Memory Bank status"""
        formatter.info("📊 Detailed Memory Bank Status:")
        formatter.info(f"  📁 Path: {status.memory_bank_path}")
        
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
        
        # Constitutional file
        status_icon = "✅" if status.constitutional_file else "❌"
        formatter.info(f"  📜 Constitutional file: {status_icon}")


# Create command instance
check_command = CheckCommand()
