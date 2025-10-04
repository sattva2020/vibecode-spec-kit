"""
Init command for Memory Bank CLI
"""

import argparse
from pathlib import Path
from typing import Optional

from ..core.config import CLIConfig
from ..core.memory_bank import MemoryBank
from ..utils.output import OutputFormatter


class InitCommand:
    """Initialize Memory Bank structure"""
    
    @staticmethod
    def execute(args: argparse.Namespace, config: CLIConfig, formatter: OutputFormatter) -> int:
        """Execute init command"""
        try:
            formatter.info("🔧 Initializing Memory Bank...")
            
            # Create Memory Bank instance
            memory_bank = MemoryBank(config.memory_bank_path)
            
            # Check if already initialized
            status = memory_bank.get_status()
            if status.initialized and not args.force:
                formatter.warning("Memory Bank already initialized. Use --force to overwrite.")
                return 0
            
            # Initialize with options
            result = memory_bank.initialize(
                with_constitution=args.constitution,
                with_templates=args.templates,
                with_ai_agents=args.ai_agents
            )
            
            if result.is_healthy():
                formatter.success("✅ Memory Bank initialized successfully")
                
                # Show what was created
                if args.verbose:
                    formatter.info(f"📁 Memory Bank path: {result.memory_bank_path}")
                    
                    if result.constitutional_file:
                        formatter.info("📋 Constitutional file created")
                    
                    template_count = sum(1 for exists in result.template_files.values() if exists)
                    if template_count > 0:
                        formatter.info(f"📄 {template_count} template files created")
                    
                    if args.ai_agents:
                        formatter.info("🤖 AI agent configuration created")
                
                return 0
            else:
                formatter.error("❌ Memory Bank initialization failed")
                for issue in result.issues:
                    formatter.error(f"  - {issue}")
                return 1
                
        except Exception as e:
            formatter.error(f"❌ Initialization failed: {str(e)}")
            if args.verbose:
                formatter.debug(f"Exception details: {e}", exc_info=True)
            return 1


# Create command instance
init_command = InitCommand()
