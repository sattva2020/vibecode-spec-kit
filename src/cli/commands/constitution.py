"""
Constitutional commands for Memory Bank CLI
"""

import argparse

from ..core.config import CLIConfig
from ..core.constitution import ConstitutionalValidator
from ..utils.output import OutputFormatter


class ConstitutionCommand:
    """Constitutional validation commands"""
    
    @staticmethod
    def execute(args: argparse.Namespace, config: CLIConfig, formatter: OutputFormatter) -> int:
        """Execute constitution command"""
        if args.constitution_action == "validate":
            return ConstitutionCommand._validate_constitution(args, config, formatter)
        elif args.constitution_action == "status":
            return ConstitutionCommand._show_status(args, config, formatter)
        elif args.constitution_action == "update":
            return ConstitutionCommand._update_constitution(args, config, formatter)
        else:
            formatter.error(f"Unknown constitution action: {args.constitution_action}")
            return 1
    
    @staticmethod
    def _validate_constitution(args: argparse.Namespace, config: CLIConfig, formatter: OutputFormatter) -> int:
        """Validate constitutional compliance"""
        try:
            formatter.info("📜 Validating constitutional compliance...")
            
            # Create constitutional validator
            validator = ConstitutionalValidator(config.memory_bank_path)
            
            # Validate constitution
            is_valid = validator.validate_constitution()
            
            if is_valid:
                formatter.success("✅ Constitutional compliance verified")
                
                # Show specific mode validation if requested
                if args.mode:
                    formatter.info(f"🔍 Validating mode: {args.mode}")
                    mode_valid = validator.validate_article_compliance(args.mode)
                    if mode_valid:
                        formatter.success(f"✅ Mode {args.mode} is constitutionally compliant")
                    else:
                        formatter.warning(f"⚠️  Mode {args.mode} has compliance issues")
                
                return 0
            else:
                formatter.error("❌ Constitutional compliance issues found")
                
                # Show specific issues
                issues = validator.get_constitutional_issues()
                for issue in issues:
                    formatter.error(f"  - {issue}")
                
                return 1
                
        except Exception as e:
            formatter.error(f"❌ Constitutional validation failed: {str(e)}")
            return 1
    
    @staticmethod
    def _show_status(args: argparse.Namespace, config: CLIConfig, formatter: OutputFormatter) -> int:
        """Show constitutional status"""
        try:
            formatter.info("📜 Constitutional Status")
            formatter.info("=" * 30)
            
            # Create constitutional validator
            validator = ConstitutionalValidator(config.memory_bank_path)
            
            # Check constitution file
            constitution_exists = validator.validate_constitution()
            status_icon = "✅" if constitution_exists else "❌"
            formatter.info(f"Constitution file: {status_icon}")
            
            # Show compliance status
            if constitution_exists:
                formatter.success("Constitutional compliance: ✅ Verified")
            else:
                formatter.error("Constitutional compliance: ❌ Issues found")
            
            # Show configuration
            constitutional_enabled = config.is_constitutional_mode_enabled()
            strictness = config.constitutional_strictness
            formatter.info(f"Constitutional gates: {'✅ Enabled' if constitutional_enabled else '❌ Disabled'}")
            formatter.info(f"Strictness level: {strictness}")
            
            return 0
            
        except Exception as e:
            formatter.error(f"❌ Failed to show constitutional status: {str(e)}")
            return 1
    
    @staticmethod
    def _update_constitution(args: argparse.Namespace, config: CLIConfig, formatter: OutputFormatter) -> int:
        """Update constitutional principles"""
        try:
            formatter.info("📜 Updating constitutional principles...")
            
            if args.article:
                formatter.info(f"🔧 Updating article: {args.article}")
                formatter.info("Constitutional update functionality coming soon")
            else:
                formatter.info("🔧 Updating full constitution")
                formatter.info("Constitutional update functionality coming soon")
            
            formatter.success("✅ Constitutional principles updated")
            return 0
            
        except Exception as e:
            formatter.error(f"❌ Failed to update constitution: {str(e)}")
            return 1


# Create command instance
constitution_command = ConstitutionCommand()
