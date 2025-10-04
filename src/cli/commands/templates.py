"""
Template commands for Memory Bank CLI with enhanced template system integration
"""

import argparse
import json
from pathlib import Path
from typing import Dict, Any

from ..core.config import CLIConfig
from ..core.templates.engine.template_engine import TemplateEngine
from ..core.templates.types.spec_template import SpecTemplate
from ..utils.output import OutputFormatter


class SpecCommand:
    """Enhanced specification template commands with adaptive complexity"""
    
    def __init__(self):
        self.template_engine = TemplateEngine()
    
    def execute(self, args: argparse.Namespace, config: CLIConfig, formatter: OutputFormatter) -> int:
        """Execute spec command"""
        if args.spec_action == "generate":
            return self._generate_spec(args, config, formatter)
        elif args.spec_action == "validate":
            return self._validate_spec(args, config, formatter)
        elif args.spec_action == "preview":
            return self._preview_spec(args, config, formatter)
        else:
            formatter.error(f"Unknown spec action: {args.spec_action}")
            return 1
    
    def _generate_spec(self, args: argparse.Namespace, config: CLIConfig, formatter: OutputFormatter) -> int:
        """Generate specification template with adaptive complexity"""
        try:
            formatter.info(f"📋 Generating specification for: {args.feature_name}")
            
            # Determine complexity level
            complexity_level = self._determine_complexity(args, formatter)
            
            # Generate base template
            base_template = self.template_engine.generate_template(complexity_level, "spec")
            
            # Enhance with spec-specific fields
            spec_template = SpecTemplate.enhance_template(base_template)
            
            # Create template data
            template_data = self._create_template_data(args, complexity_level)
            
            # Simple validation for compatibility
            validation_result = self._simple_validate(template_data)
            
            if not validation_result.is_valid:
                formatter.warning("⚠️ Template validation issues found:")
                for error in validation_result.errors:
                    formatter.warning(f"  - {error}")
            
            # Generate content
            content = SpecTemplate.generate_spec_content(template_data)
            
            # Save specification
            spec_file = config.get_memory_bank_path() / f"spec-{args.feature_name}.md"
            spec_file.write_text(content, encoding='utf-8')
            
            # Save template data as JSON for later editing
            data_file = config.get_memory_bank_path() / f"spec-{args.feature_name}-data.json"
            data_file.write_text(json.dumps(template_data, indent=2), encoding='utf-8')
            
            formatter.success(f"✅ Specification generated: {spec_file}")
            formatter.info(f"📊 Complexity Level: {complexity_level}")
            formatter.info(f"📊 Validation Score: {validation_result.score}/{validation_result.max_score}")
            
            if validation_result.warnings:
                formatter.warning("⚠️ Warnings:")
                for warning in validation_result.warnings:
                    formatter.warning(f"  - {warning}")
            
            return 0
            
        except Exception as e:
            formatter.error(f"❌ Failed to generate specification: {str(e)}")
            return 1
    
    def _validate_spec(self, args: argparse.Namespace, config: CLIConfig, formatter: OutputFormatter) -> int:
        """Validate existing specification"""
        try:
            spec_file = config.get_memory_bank_path() / f"spec-{args.feature_name}.md"
            data_file = config.get_memory_bank_path() / f"spec-{args.feature_name}-data.json"
            
            if not spec_file.exists():
                formatter.error(f"❌ Specification file not found: {spec_file}")
                return 1
            
            # Load template data if available
            template_data = {}
            if data_file.exists():
                template_data = json.loads(data_file.read_text(encoding='utf-8'))
            
            # Determine complexity level from data or args
            complexity_level = template_data.get("complexity_level", args.level or 1)
            
            # Generate template for validation
            base_template = self.template_engine.generate_template(complexity_level, "spec")
            spec_template = SpecTemplate.enhance_template(base_template)
            
            # Simple validation for compatibility
            validation_result = self._simple_validate(template_data)
            spec_validation = SpecTemplate.validate_spec_template(template_data)
            
            # Display results
            formatter.info(f"📊 Validation Results for: {args.feature_name}")
            formatter.info(f"📊 Overall Score: {validation_result.score}/{validation_result.max_score}")
            formatter.info(f"📊 Valid: {'✅ Yes' if validation_result.is_valid else '❌ No'}")
            
            if validation_result.errors:
                formatter.error("❌ Errors:")
                for error in validation_result.errors:
                    formatter.error(f"  - {error}")
            
            if validation_result.warnings or spec_validation["warnings"]:
                formatter.warning("⚠️ Warnings:")
                for warning in validation_result.warnings + spec_validation["warnings"]:
                    formatter.warning(f"  - {warning}")
            
            if validation_result.suggestions or spec_validation["suggestions"]:
                formatter.info("💡 Suggestions:")
                for suggestion in validation_result.suggestions + spec_validation["suggestions"]:
                    formatter.info(f"  - {suggestion}")
            
            return 0 if validation_result.is_valid else 1
            
        except Exception as e:
            formatter.error(f"❌ Failed to validate specification: {str(e)}")
            return 1
    
    def _preview_spec(self, args: argparse.Namespace, config: CLIConfig, formatter: OutputFormatter) -> int:
        """Preview specification template"""
        try:
            complexity_level = args.level or 1
            
            # Generate template preview
            preview = self.template_engine.create_template_preview(complexity_level)
            
            formatter.info(f"📋 Specification Template Preview - Level {complexity_level}")
            formatter.print_text(preview)
            
            return 0
            
        except Exception as e:
            formatter.error(f"❌ Failed to preview specification: {str(e)}")
            return 1
    
    def _determine_complexity(self, args: argparse.Namespace, formatter: OutputFormatter) -> int:
        """Determine complexity level from arguments or description"""
        if args.level:
            return args.level
        
        if args.description:
            # Use complexity detector
            complexity_level = self.template_engine.detect_complexity_and_generate(
                args.description
            ).get_complexity_level()
            
            formatter.info(f"🤖 Auto-detected complexity level: {complexity_level}")
            return complexity_level
        
        # Default to Level 1
        return 1
    
    def _create_template_data(self, args: argparse.Namespace, complexity_level: int) -> Dict[str, Any]:
        """Create template data from arguments"""
        template_data = {
            "title": args.feature_name,
            "description": args.description or f"Specification for {args.feature_name}",
            "complexity_level": complexity_level,
            "template_type": "spec"
        }
        
        # Add any additional arguments
        if hasattr(args, 'requirements') and args.requirements:
            template_data["functional_requirements"] = args.requirements
        
        if hasattr(args, 'priority') and args.priority:
            template_data["priority"] = args.priority
        
        return template_data
    
    def _simple_validate(self, data: Dict[str, Any]) -> Any:
        """Simple validation for compatibility"""
        from types import SimpleNamespace
        
        errors = []
        warnings = []
        suggestions = []
        score = 50  # Base score
        max_score = 100
        
        # Check required fields
        required_fields = ['title', 'description']
        for field in required_fields:
            if not data.get(field):
                errors.append(f"Required field '{field}' is missing")
            else:
                score += 20
        
        # Check description length
        description = data.get('description', '')
        if description and len(description) < 10:
            warnings.append("Description is too short")
        elif len(description) >= 50:
            score += 10
        
        # Check complexity-specific fields
        complexity_level = data.get('complexity_level', 1)
        if complexity_level >= 3:
            if not data.get('architecture'):
                warnings.append("Architecture section recommended for complex tasks")
            if not data.get('dependencies'):
                warnings.append("Dependencies should be identified for complex tasks")
        
        return SimpleNamespace(
            is_valid=len(errors) == 0,
            score=min(score, max_score),
            max_score=max_score,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )


# Create command instance
spec_command = SpecCommand()
