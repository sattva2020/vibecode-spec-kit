"""
Configuration management for Memory Bank CLI
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class CLIConfig:
    """CLI configuration settings"""
    
    # Memory Bank settings
    memory_bank_path: str = "memory-bank"
    
    # Constitutional settings
    constitutional_gates: bool = True
    constitutional_strictness: str = "recommended"  # strict, recommended, disabled
    
    # Spec-Driven settings
    spec_driven_mode: bool = True
    spec_driven_min_level: int = 2
    
    # Test-First settings
    test_first: bool = True
    test_first_min_level: int = 2
    contract_testing: bool = True
    
    # Multi-AI settings
    multi_ai_enabled: bool = True
    ai_agents: List[str] = None
    ai_coordination: str = "sequential"  # sequential, parallel, adaptive
    
    # Template settings
    template_adaptation: bool = True
    template_complexity_scaling: bool = True
    
    # Output settings
    output_format: str = "text"  # text, json, yaml
    verbosity: int = 1
    
    # Performance settings
    lazy_loading: bool = True
    conditional_validation: bool = True
    
    def __post_init__(self):
        """Initialize default values"""
        if self.ai_agents is None:
            self.ai_agents = ["github-copilot"]
    
    @classmethod
    def default(cls) -> 'CLIConfig':
        """Create default configuration"""
        return cls()
    
    @classmethod
    def from_file(cls, config_path: str) -> 'CLIConfig':
        """Load configuration from file"""
        config_file = Path(config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                if config_file.suffix.lower() == '.json':
                    data = json.load(f)
                elif config_file.suffix.lower() in ['.yml', '.yaml']:
                    data = yaml.safe_load(f)
                else:
                    raise ValueError(f"Unsupported configuration file format: {config_file.suffix}")
            
            return cls(**data)
            
        except Exception as e:
            raise ValueError(f"Failed to load configuration: {e}")
    
    def to_file(self, config_path: str, format: str = "json") -> None:
        """Save configuration to file"""
        config_file = Path(config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = asdict(self)
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                if format.lower() == 'json':
                    json.dump(data, f, indent=2, ensure_ascii=False)
                elif format.lower() in ['yml', 'yaml']:
                    yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
                else:
                    raise ValueError(f"Unsupported output format: {format}")
                    
        except Exception as e:
            raise ValueError(f"Failed to save configuration: {e}")
    
    def update(self, **kwargs) -> None:
        """Update configuration with new values"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"Unknown configuration option: {key}")
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        # Validate constitutional strictness
        if self.constitutional_strictness not in ['strict', 'recommended', 'disabled']:
            issues.append(f"Invalid constitutional_strictness: {self.constitutional_strictness}")
        
        # Validate AI coordination
        if self.ai_coordination not in ['sequential', 'parallel', 'adaptive']:
            issues.append(f"Invalid ai_coordination: {self.ai_coordination}")
        
        # Validate output format
        if self.output_format not in ['text', 'json', 'yaml']:
            issues.append(f"Invalid output_format: {self.output_format}")
        
        # Validate verbosity
        if not isinstance(self.verbosity, int) or self.verbosity < 0:
            issues.append(f"Invalid verbosity: {self.verbosity}")
        
        # Validate min levels
        if not isinstance(self.spec_driven_min_level, int) or self.spec_driven_min_level < 1 or self.spec_driven_min_level > 4:
            issues.append(f"Invalid spec_driven_min_level: {self.spec_driven_min_level}")
        
        if not isinstance(self.test_first_min_level, int) or self.test_first_min_level < 1 or self.test_first_min_level > 4:
            issues.append(f"Invalid test_first_min_level: {self.test_first_min_level}")
        
        return issues
    
    def get_memory_bank_path(self) -> Path:
        """Get Memory Bank path as Path object"""
        return Path(self.memory_bank_path).resolve()
    
    def is_constitutional_mode_enabled(self) -> bool:
        """Check if constitutional mode is enabled"""
        return self.constitutional_gates and self.constitutional_strictness != 'disabled'
    
    def is_spec_driven_enabled_for_level(self, level: int) -> bool:
        """Check if Spec-Driven mode is enabled for given complexity level"""
        return self.spec_driven_mode and level >= self.spec_driven_min_level
    
    def is_test_first_enabled_for_level(self, level: int) -> bool:
        """Check if Test-First mode is enabled for given complexity level"""
        return self.test_first and level >= self.test_first_min_level
    
    def should_use_strict_validation(self) -> bool:
        """Check if strict validation should be used"""
        return self.constitutional_strictness == 'strict'
    
    def get_enabled_ai_agents(self) -> List[str]:
        """Get list of enabled AI agents"""
        if not self.multi_ai_enabled:
            return ["github-copilot"]
        return self.ai_agents or ["github-copilot"]
