"""
AI Agent management for Memory Bank CLI
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional


class AIAgentManager:
    """Manages AI agent configurations"""
    
    def __init__(self, memory_bank_path: str = "memory-bank"):
        self.memory_bank_path = Path(memory_bank_path)
        self.config_file = self.memory_bank_path / "ai-agents.json"
    
    def list_agents(self) -> List[str]:
        """List available AI agents"""
        return ["github-copilot", "claude-code", "gemini-cli", "cursor"]
    
    def get_enabled_agents(self) -> List[str]:
        """Get list of enabled agents"""
        config = self._load_config()
        return config.get("enabled_agents", ["github-copilot"])
    
    def enable_agent(self, agent_name: str) -> bool:
        """Enable an AI agent"""
        config = self._load_config()
        if agent_name not in config.get("enabled_agents", []):
            config.setdefault("enabled_agents", []).append(agent_name)
            return self._save_config(config)
        return True
    
    def disable_agent(self, agent_name: str) -> bool:
        """Disable an AI agent"""
        config = self._load_config()
        if agent_name in config.get("enabled_agents", []):
            config["enabled_agents"].remove(agent_name)
            return self._save_config(config)
        return True
    
    def _load_config(self) -> Dict[str, Any]:
        """Load AI agent configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Default configuration
        return {
            "enabled_agents": ["github-copilot"],
            "agent_configs": {
                "github-copilot": {"enabled": True, "priority": 1},
                "claude-code": {"enabled": False, "priority": 2},
                "gemini-cli": {"enabled": False, "priority": 3},
                "cursor": {"enabled": False, "priority": 4}
            }
        }
    
    def _save_config(self, config: Dict[str, Any]) -> bool:
        """Save AI agent configuration"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False
