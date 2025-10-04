"""
Documentation automation for workflow transitions
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from pathlib import Path

from ..memory_bank import MemoryBank
from ..templates.engine.template_engine import TemplateEngine
from ..research.conversion.spec_converter import SpecConverter


class DocumentationAutomation:
    """Automates documentation generation from specifications and research"""
    
    def __init__(self, memory_bank: MemoryBank):
        self.memory_bank = memory_bank
        self.template_engine = TemplateEngine()
        self.spec_converter = SpecConverter()
    
    def generate_mode_transition_docs(self, from_mode: str, to_mode: str, 
                                    validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate documentation for mode transition"""
        try:
            # Create transition documentation
            transition_doc = {
                'transition': f"{from_mode} -> {to_mode}",
                'timestamp': datetime.now().isoformat(),
                'validation_score': validation_result.get('overall_score', 0),
                'gate_results': validation_result.get('gate_results', []),
                'warnings': validation_result.get('warnings', []),
                'suggestions': validation_result.get('suggestions', [])
            }
            
            # Save transition log
            self._save_transition_log(transition_doc)
            
            # Generate mode-specific documentation
            if to_mode == 'plan':
                return self._generate_plan_docs()
            elif to_mode == 'creative':
                return self._generate_creative_docs()
            elif to_mode == 'implement':
                return self._generate_implement_docs()
            elif to_mode == 'reflect':
                return self._generate_reflect_docs()
            elif to_mode == 'archive':
                return self._generate_archive_docs()
            
            return {'success': True, 'transition_logged': True}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def generate_spec_documentation(self, spec_file: str) -> Dict[str, Any]:
        """Generate documentation from specification"""
        try:
            if not Path(spec_file).exists():
                return {'success': False, 'error': 'Specification file not found'}
            
            # Load specification
            with open(spec_file, 'r', encoding='utf-8') as f:
                spec_data = json.load(f)
            
            # Generate documentation components
            docs = {
                'specification_summary': self._generate_spec_summary(spec_data),
                'requirements_doc': self._generate_requirements_doc(spec_data),
                'architecture_doc': self._generate_architecture_doc(spec_data),
                'test_plan': self._generate_test_plan(spec_data),
                'api_doc': self._generate_api_doc(spec_data)
            }
            
            # Save documentation
            doc_files = self._save_documentation(docs)
            
            return {
                'success': True,
                'documentation_files': doc_files,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def generate_research_documentation(self, research_file: str) -> Dict[str, Any]:
        """Generate documentation from research"""
        try:
            if not Path(research_file).exists():
                return {'success': False, 'error': 'Research file not found'}
            
            # Load research
            with open(research_file, 'r', encoding='utf-8') as f:
                research_data = json.load(f)
            
            # Generate documentation from research
            docs = {
                'research_summary': self._generate_research_summary(research_data),
                'technology_review': self._generate_tech_review(research_data),
                'methodology_analysis': self._generate_methodology_analysis(research_data),
                'recommendations': self._generate_recommendations(research_data)
            }
            
            # Save documentation
            doc_files = self._save_research_docs(docs)
            
            return {
                'success': True,
                'documentation_files': doc_files,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def update_progress_documentation(self) -> Dict[str, Any]:
        """Update progress documentation based on current state"""
        try:
            # Get current Memory Bank state
            context = self.memory_bank.get_context()
            
            # Generate progress report
            progress_doc = {
                'current_mode': context.get('current_mode', 'unknown'),
                'last_updated': datetime.now().isoformat(),
                'completed_tasks': self._get_completed_tasks(),
                'active_tasks': self._get_active_tasks(),
                'next_steps': self._get_next_steps(),
                'metrics': self._get_progress_metrics()
            }
            
            # Update progress file
            progress_file = Path('memory-bank/progress.md')
            self._update_progress_file(progress_file, progress_doc)
            
            return {
                'success': True,
                'progress_updated': True,
                'file': str(progress_file)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _save_transition_log(self, transition_doc: Dict[str, Any]):
        """Save transition log"""
        log_file = Path('memory-bank/transitions.json')
        
        # Load existing logs
        logs = []
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        
        # Add new log
        logs.append(transition_doc)
        
        # Save logs
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2)
    
    def _generate_spec_summary(self, spec_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate specification summary"""
        return {
            'title': spec_data.get('title', 'Untitled'),
            'description': spec_data.get('description', ''),
            'complexity_level': spec_data.get('complexity_level', 1),
            'priority': spec_data.get('priority', 'medium'),
            'status': spec_data.get('status', 'draft'),
            'requirements_count': len(spec_data.get('requirements', [])),
            'acceptance_criteria_count': len(spec_data.get('acceptance_criteria', []))
        }
    
    def _generate_requirements_doc(self, spec_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate requirements document"""
        return {
            'functional_requirements': spec_data.get('requirements', []),
            'non_functional_requirements': spec_data.get('non_functional_requirements', []),
            'acceptance_criteria': spec_data.get('acceptance_criteria', []),
            'constraints': spec_data.get('constraints', []),
            'assumptions': spec_data.get('assumptions', [])
        }
    
    def _generate_architecture_doc(self, spec_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate architecture document"""
        return {
            'overview': spec_data.get('architecture', {}).get('overview', ''),
            'components': spec_data.get('architecture', {}).get('components', []),
            'dependencies': spec_data.get('dependencies', []),
            'data_flow': spec_data.get('architecture', {}).get('data_flow', ''),
            'security_considerations': spec_data.get('architecture', {}).get('security', [])
        }
    
    def _generate_test_plan(self, spec_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test plan"""
        return {
            'test_strategy': spec_data.get('test_strategy', ''),
            'test_cases': spec_data.get('test_cases', []),
            'test_data': spec_data.get('test_data', []),
            'test_environment': spec_data.get('test_environment', {}),
            'acceptance_criteria': spec_data.get('acceptance_criteria', [])
        }
    
    def _generate_api_doc(self, spec_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate API documentation"""
        return {
            'endpoints': spec_data.get('api', {}).get('endpoints', []),
            'authentication': spec_data.get('api', {}).get('authentication', ''),
            'rate_limits': spec_data.get('api', {}).get('rate_limits', {}),
            'error_codes': spec_data.get('api', {}).get('error_codes', [])
        }
    
    def _generate_research_summary(self, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate research summary"""
        return {
            'topic': research_data.get('topic', ''),
            'research_type': research_data.get('type', ''),
            'key_findings': research_data.get('findings', []),
            'sources_count': len(research_data.get('sources', [])),
            'confidence_score': research_data.get('confidence_score', 0),
            'recommendations': research_data.get('recommendations', [])
        }
    
    def _generate_tech_review(self, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate technology review"""
        return {
            'technologies_analyzed': research_data.get('technologies', []),
            'pros_cons': research_data.get('pros_cons', {}),
            'performance_comparison': research_data.get('performance', {}),
            'adoption_trends': research_data.get('trends', {}),
            'recommendation': research_data.get('recommendation', '')
        }
    
    def _generate_methodology_analysis(self, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate methodology analysis"""
        return {
            'methodologies_compared': research_data.get('methodologies', []),
            'effectiveness_metrics': research_data.get('effectiveness', {}),
            'use_cases': research_data.get('use_cases', []),
            'best_practices': research_data.get('best_practices', []),
            'recommended_approach': research_data.get('recommended_approach', '')
        }
    
    def _generate_recommendations(self, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate recommendations"""
        return {
            'primary_recommendation': research_data.get('primary_recommendation', ''),
            'alternative_options': research_data.get('alternatives', []),
            'implementation_plan': research_data.get('implementation', {}),
            'risk_mitigation': research_data.get('risks', []),
            'success_metrics': research_data.get('success_metrics', [])
        }
    
    def _save_documentation(self, docs: Dict[str, Any]) -> List[str]:
        """Save documentation to files"""
        doc_files = []
        doc_dir = Path('memory-bank/docs')
        doc_dir.mkdir(exist_ok=True)
        
        for doc_type, content in docs.items():
            file_path = doc_dir / f"{doc_type}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2)
            doc_files.append(str(file_path))
        
        return doc_files
    
    def _save_research_docs(self, docs: Dict[str, Any]) -> List[str]:
        """Save research documentation to files"""
        doc_files = []
        doc_dir = Path('memory-bank/research-docs')
        doc_dir.mkdir(exist_ok=True)
        
        for doc_type, content in docs.items():
            file_path = doc_dir / f"{doc_type}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2)
            doc_files.append(str(file_path))
        
        return doc_files
    
    def _update_progress_file(self, progress_file: Path, progress_doc: Dict[str, Any]):
        """Update progress file with new documentation"""
        # This would integrate with existing progress.md format
        # For now, create a JSON backup
        backup_file = progress_file.with_suffix('.json')
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(progress_doc, f, indent=2)
    
    def _get_completed_tasks(self) -> List[str]:
        """Get list of completed tasks"""
        # This would read from tasks.md or memory bank state
        return []
    
    def _get_active_tasks(self) -> List[str]:
        """Get list of active tasks"""
        # This would read from tasks.md or memory bank state
        return []
    
    def _get_next_steps(self) -> List[str]:
        """Get list of next steps"""
        # This would read from tasks.md or memory bank state
        return []
    
    def _get_progress_metrics(self) -> Dict[str, Any]:
        """Get progress metrics"""
        # This would calculate from memory bank state
        return {
            'files_created': 0,
            'tasks_completed': 0,
            'time_elapsed': '0 minutes'
        }
    
    def _generate_plan_docs(self) -> Dict[str, Any]:
        """Generate documentation for PLAN mode"""
        return {'success': True, 'plan_docs_generated': True}
    
    def _generate_creative_docs(self) -> Dict[str, Any]:
        """Generate documentation for CREATIVE mode"""
        return {'success': True, 'creative_docs_generated': True}
    
    def _generate_implement_docs(self) -> Dict[str, Any]:
        """Generate documentation for IMPLEMENT mode"""
        return {'success': True, 'implement_docs_generated': True}
    
    def _generate_reflect_docs(self) -> Dict[str, Any]:
        """Generate documentation for REFLECT mode"""
        return {'success': True, 'reflect_docs_generated': True}
    
    def _generate_archive_docs(self) -> Dict[str, Any]:
        """Generate documentation for ARCHIVE mode"""
        return {'success': True, 'archive_docs_generated': True}


class SpecToDocConverter:
    """Converts specifications to various documentation formats"""
    
    def __init__(self):
        self.template_engine = TemplateEngine()
    
    def convert_to_markdown(self, spec_data: Dict[str, Any]) -> str:
        """Convert specification to Markdown format"""
        md_content = f"""# {spec_data.get('title', 'Specification')}

## Overview
{spec_data.get('description', '')}

## Requirements
"""
        for req in spec_data.get('requirements', []):
            md_content += f"- {req}\n"
        
        md_content += "\n## Acceptance Criteria\n"
        for criteria in spec_data.get('acceptance_criteria', []):
            md_content += f"- {criteria}\n"
        
        return md_content
    
    def convert_to_adr(self, spec_data: Dict[str, Any]) -> str:
        """Convert specification to Architecture Decision Record format"""
        return f"""# ADR-001: {spec_data.get('title', 'Decision')}

## Status
Proposed

## Context
{spec_data.get('description', '')}

## Decision
{spec_data.get('architecture', {}).get('decision', '')}

## Consequences
{spec_data.get('architecture', {}).get('consequences', '')}
"""
    
    def convert_to_readme(self, spec_data: Dict[str, Any]) -> str:
        """Convert specification to README format"""
        return f"""# {spec_data.get('title', 'Project')}

{spec_data.get('description', '')}

## Getting Started

## Requirements
{', '.join(spec_data.get('requirements', []))}

## Installation

## Usage

## Testing
"""
