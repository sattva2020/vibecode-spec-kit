"""
AI Agent commands for Memory Bank CLI
"""

import argparse

from ..core.config import CLIConfig
from ..core.ai_agents import AIAgentManager
from ..utils.output import OutputFormatter


class AICommand:
    """AI agent management commands"""
    
    @staticmethod
    def execute(args: argparse.Namespace, config: CLIConfig, formatter: OutputFormatter) -> int:
        """Execute AI command"""
        if args.ai_action == "list":
            return AICommand._list_agents(args, config, formatter)
        elif args.ai_action == "config":
            return AICommand._config_agent(args, config, formatter)
        elif args.ai_action == "test":
            return AICommand._test_agent(args, config, formatter)
        else:
            formatter.error(f"Unknown AI action: {args.ai_action}")
            return 1
    
    @staticmethod
    def _list_agents(args: argparse.Namespace, config: CLIConfig, formatter: OutputFormatter) -> int:
        """List available AI agents"""
        try:
            formatter.info("🤖 Available AI Agents:")
            
            # Create AI agent manager
            ai_manager = AIAgentManager(config.memory_bank_path)
            
            # Get all agents and enabled status
            all_agents = ai_manager.list_agents()
            enabled_agents = ai_manager.get_enabled_agents()
            
            # Display agents
            for agent in all_agents:
                status = "✅ Enabled" if agent in enabled_agents else "❌ Disabled"
                formatter.info(f"  {agent}: {status}")
            
            return 0
            
        except Exception as e:
            formatter.error(f"❌ Failed to list agents: {str(e)}")
            return 1
    
    @staticmethod
    def _config_agent(args: argparse.Namespace, config: CLIConfig, formatter: OutputFormatter) -> int:
        """Configure AI agent"""
        try:
            formatter.info(f"⚙️  Configuring AI agent: {args.agent_name}")
            
            # Create AI agent manager
            ai_manager = AIAgentManager(config.memory_bank_path)
            
            # Enable or disable agent
            if args.enable:
                success = ai_manager.enable_agent(args.agent_name)
                action = "enabled"
            elif args.disable:
                success = ai_manager.disable_agent(args.agent_name)
                action = "disabled"
            else:
                formatter.error("❌ Must specify --enable or --disable")
                return 1
            
            if success:
                formatter.success(f"✅ Agent {args.agent_name} {action} successfully")
                return 0
            else:
                formatter.error(f"❌ Failed to {action} agent {args.agent_name}")
                return 1
                
        except Exception as e:
            formatter.error(f"❌ Failed to configure agent: {str(e)}")
            return 1
    
    @staticmethod
    def _test_agent(args: argparse.Namespace, config: CLIConfig, formatter: OutputFormatter) -> int:
        """Test AI agent integration"""
        try:
            formatter.info(f"🧪 Testing AI agent: {args.agent_name}")
            
            # Create AI agent manager
            ai_manager = AIAgentManager(config.memory_bank_path)
            
            # Check if agent is available
            available_agents = ai_manager.list_agents()
            if args.agent_name not in available_agents:
                formatter.error(f"❌ Agent {args.agent_name} is not available")
                return 1
            
            # Check if agent is enabled
            enabled_agents = ai_manager.get_enabled_agents()
            if args.agent_name not in enabled_agents:
                formatter.warning(f"⚠️  Agent {args.agent_name} is not enabled")
                formatter.info("Run 'memory-bank ai config <agent> --enable' to enable it")
                return 1
            
            # Placeholder test
            formatter.success(f"✅ Agent {args.agent_name} is properly configured")
            formatter.info("Note: Full integration testing requires VS Code environment")
            
            return 0
            
        except Exception as e:
            formatter.error(f"❌ Failed to test agent: {str(e)}")
            return 1


# Create command instance
ai_command = AICommand()
