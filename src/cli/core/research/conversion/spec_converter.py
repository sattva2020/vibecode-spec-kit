"""
Spec converter for transforming research into specifications
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from ...templates.engine.template_engine import TemplateEngine
from ...templates.types.spec_template import SpecTemplate


class SpecConverter:
    """Converter for transforming research results into specifications"""
    
    def __init__(self):
        self.template_engine = TemplateEngine()
        self.conversion_rules = self._initialize_conversion_rules()
        self.field_mappings = self._initialize_field_mappings()
    
    def _initialize_conversion_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize conversion rules for different research types"""
        return {
            'technical': {
                'complexity_detection': {
                    'simple': ['tutorial', 'basic', 'simple', 'easy'],
                    'intermediate': ['intermediate', 'advanced', 'complex', 'integration'],
                    'complex': ['architecture', 'system', 'enterprise', 'scalable']
                },
                'required_fields': ['title', 'description', 'technical_requirements'],
                'optional_fields': ['architecture', 'performance', 'security', 'deployment']
            },
            'methodology': {
                'complexity_detection': {
                    'simple': ['process', 'workflow', 'procedure'],
                    'intermediate': ['framework', 'methodology', 'approach'],
                    'complex': ['transformation', 'change management', 'organizational']
                },
                'required_fields': ['title', 'description', 'process_steps'],
                'optional_fields': ['team_requirements', 'tools', 'metrics', 'timeline']
            },
            'competitive': {
                'complexity_detection': {
                    'simple': ['comparison', 'review', 'analysis'],
                    'intermediate': ['market analysis', 'competitive landscape'],
                    'complex': ['strategic analysis', 'market research', 'competitive intelligence']
                },
                'required_fields': ['title', 'description', 'competitors'],
                'optional_fields': ['market_size', 'trends', 'recommendations']
            }
        }
    
    def _initialize_field_mappings(self) -> Dict[str, Dict[str, str]]:
        """Initialize field mappings from research to specifications"""
        return {
            'technical': {
                'title': 'research_title',
                'description': 'synthesized_summary',
                'technical_requirements': 'key_insights',
                'architecture': 'architecture_analysis',
                'performance': 'performance_considerations',
                'security': 'security_considerations',
                'deployment': 'deployment_guidelines'
            },
            'methodology': {
                'title': 'research_title',
                'description': 'synthesized_summary',
                'process_steps': 'key_insights',
                'team_requirements': 'team_considerations',
                'tools': 'tool_recommendations',
                'metrics': 'success_metrics',
                'timeline': 'implementation_timeline'
            },
            'competitive': {
                'title': 'research_title',
                'description': 'synthesized_summary',
                'competitors': 'competitive_analysis',
                'market_size': 'market_analysis',
                'trends': 'market_trends',
                'recommendations': 'strategic_recommendations'
            }
        }
    
    def convert_to_spec(self, 
                       research_data: Dict[str, Any],
                       research_type: str = 'technical',
                       complexity_level: Optional[int] = None) -> Dict[str, Any]:
        """
        Convert research data to specification format
        
        Args:
            research_data: Research data to convert
            research_type: Type of research (technical, methodology, competitive)
            complexity_level: Complexity level (1-4), auto-detected if None
        
        Returns:
            Specification data
        """
        # Auto-detect complexity if not provided
        if complexity_level is None:
            complexity_level = self._detect_complexity(research_data, research_type)
        
        # Generate base specification template
        spec_template = self.template_engine.generate_template(
            complexity_level=complexity_level,
            template_type='spec'
        )
        
        # Map research data to specification fields
        spec_data = self._map_research_to_spec(research_data, research_type, spec_template)
        
        # Enhance specification with research insights
        enhanced_spec = self._enhance_specification(spec_data, research_data, research_type)
        
        # Validate and improve specification
        validated_spec = self._validate_and_improve_spec(enhanced_spec, complexity_level)
        
        return validated_spec
    
    def _detect_complexity(self, research_data: Dict[str, Any], research_type: str) -> int:
        """Detect complexity level from research data"""
        rules = self.conversion_rules.get(research_type, self.conversion_rules['technical'])
        complexity_detection = rules['complexity_detection']
        
        # Combine text for analysis
        text_parts = []
        
        if 'synthesized_summary' in research_data:
            text_parts.append(research_data['synthesized_summary'])
        
        if 'key_insights' in research_data:
            text_parts.extend(research_data['key_insights'])
        
        if 'recommendations' in research_data:
            text_parts.extend(research_data['recommendations'])
        
        combined_text = ' '.join(text_parts).lower()
        
        # Check complexity indicators
        complexity_scores = {'simple': 0, 'intermediate': 0, 'complex': 0}
        
        for level, indicators in complexity_detection.items():
            for indicator in indicators:
                if indicator in combined_text:
                    complexity_scores[level] += 1
        
        # Determine complexity level
        max_level = max(complexity_scores, key=complexity_scores.get)
        
        if max_level == 'complex':
            return 4
        elif max_level == 'intermediate':
            return 3
        else:
            return 2  # Default to level 2 for simple cases
    
    def _map_research_to_spec(self, 
                             research_data: Dict[str, Any],
                             research_type: str,
                             spec_template: Dict[str, Any]) -> Dict[str, Any]:
        """Map research data to specification fields"""
        mappings = self.field_mappings.get(research_type, self.field_mappings['technical'])
        
        spec_data = spec_template.copy()
        
        # Map fields
        for spec_field, research_field in mappings.items():
            if research_field in research_data:
                spec_data[spec_field] = research_data[research_field]
        
        # Set basic fields
        spec_data['created_at'] = datetime.now().isoformat()
        spec_data['research_type'] = research_type
        spec_data['source_research'] = research_data.get('query', 'Unknown')
        
        # Set complexity level
        spec_data['complexity_level'] = self._detect_complexity(research_data, research_type)
        
        return spec_data
    
    def _enhance_specification(self, 
                              spec_data: Dict[str, Any],
                              research_data: Dict[str, Any],
                              research_type: str) -> Dict[str, Any]:
        """Enhance specification with additional research insights"""
        
        # Add research metadata
        spec_data['research_metadata'] = {
            'source_count': len(research_data.get('sources', [])),
            'ai_analyses_count': len(research_data.get('ai_analyses', [])),
            'confidence_score': research_data.get('confidence_score', 0.0),
            'quality_score': research_data.get('quality_score', 0.0),
            'research_timestamp': research_data.get('created_at', datetime.now().isoformat())
        }
        
        # Enhance based on research type
        if research_type == 'technical':
            spec_data = self._enhance_technical_spec(spec_data, research_data)
        elif research_type == 'methodology':
            spec_data = self._enhance_methodology_spec(spec_data, research_data)
        elif research_type == 'competitive':
            spec_data = self._enhance_competitive_spec(spec_data, research_data)
        
        # Add implementation guidance
        spec_data['implementation_guidance'] = self._generate_implementation_guidance(
            spec_data, research_data, research_type
        )
        
        return spec_data
    
    def _enhance_technical_spec(self, spec_data: Dict[str, Any], research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance technical specification"""
        
        # Extract technical insights
        insights = research_data.get('key_insights', [])
        recommendations = research_data.get('recommendations', [])
        
        # Categorize insights
        technical_insights = {
            'implementation': [],
            'performance': [],
            'security': [],
            'integration': [],
            'deployment': []
        }
        
        for insight in insights:
            insight_lower = insight.lower()
            if any(word in insight_lower for word in ['implement', 'setup', 'install', 'configure']):
                technical_insights['implementation'].append(insight)
            elif any(word in insight_lower for word in ['performance', 'speed', 'efficiency', 'optimize']):
                technical_insights['performance'].append(insight)
            elif any(word in insight_lower for word in ['security', 'auth', 'encrypt', 'secure']):
                technical_insights['security'].append(insight)
            elif any(word in insight_lower for word in ['integrate', 'api', 'connect', 'interface']):
                technical_insights['integration'].append(insight)
            elif any(word in insight_lower for word in ['deploy', 'production', 'server', 'host']):
                technical_insights['deployment'].append(insight)
        
        # Add categorized insights to spec
        spec_data['technical_insights'] = technical_insights
        spec_data['implementation_recommendations'] = recommendations
        
        return spec_data
    
    def _enhance_methodology_spec(self, spec_data: Dict[str, Any], research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance methodology specification"""
        
        # Extract methodology insights
        insights = research_data.get('key_insights', [])
        recommendations = research_data.get('recommendations', [])
        
        # Categorize insights
        methodology_insights = {
            'process': [],
            'team': [],
            'tools': [],
            'metrics': [],
            'challenges': []
        }
        
        for insight in insights:
            insight_lower = insight.lower()
            if any(word in insight_lower for word in ['process', 'step', 'workflow', 'procedure']):
                methodology_insights['process'].append(insight)
            elif any(word in insight_lower for word in ['team', 'role', 'responsibility', 'collaboration']):
                methodology_insights['team'].append(insight)
            elif any(word in insight_lower for word in ['tool', 'framework', 'platform', 'software']):
                methodology_insights['tools'].append(insight)
            elif any(word in insight_lower for word in ['metric', 'measure', 'kpi', 'success']):
                methodology_insights['metrics'].append(insight)
            elif any(word in insight_lower for word in ['challenge', 'pitfall', 'risk', 'obstacle']):
                methodology_insights['challenges'].append(insight)
        
        # Add categorized insights to spec
        spec_data['methodology_insights'] = methodology_insights
        spec_data['adoption_recommendations'] = recommendations
        
        return spec_data
    
    def _enhance_competitive_spec(self, spec_data: Dict[str, Any], research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance competitive specification"""
        
        # Extract competitive insights
        insights = research_data.get('key_insights', [])
        recommendations = research_data.get('recommendations', [])
        
        # Categorize insights
        competitive_insights = {
            'market': [],
            'competitors': [],
            'features': [],
            'positioning': [],
            'trends': []
        }
        
        for insight in insights:
            insight_lower = insight.lower()
            if any(word in insight_lower for word in ['market', 'industry', 'landscape', 'ecosystem']):
                competitive_insights['market'].append(insight)
            elif any(word in insight_lower for word in ['competitor', 'rival', 'alternative', 'option']):
                competitive_insights['competitors'].append(insight)
            elif any(word in insight_lower for word in ['feature', 'capability', 'function', 'characteristic']):
                competitive_insights['features'].append(insight)
            elif any(word in insight_lower for word in ['position', 'differentiate', 'advantage', 'strength']):
                competitive_insights['positioning'].append(insight)
            elif any(word in insight_lower for word in ['trend', 'direction', 'evolution', 'future']):
                competitive_insights['trends'].append(insight)
        
        # Add categorized insights to spec
        spec_data['competitive_insights'] = competitive_insights
        spec_data['strategic_recommendations'] = recommendations
        
        return spec_data
    
    def _generate_implementation_guidance(self, 
                                        spec_data: Dict[str, Any],
                                        research_data: Dict[str, Any],
                                        research_type: str) -> Dict[str, Any]:
        """Generate implementation guidance from research"""
        
        guidance = {
            'priority': 'medium',
            'estimated_effort': 'unknown',
            'success_factors': [],
            'risk_factors': [],
            'next_steps': []
        }
        
        # Determine priority based on research insights
        insights = research_data.get('key_insights', [])
        recommendations = research_data.get('recommendations', [])
        
        # Priority indicators
        high_priority_indicators = ['critical', 'important', 'essential', 'urgent', 'priority']
        medium_priority_indicators = ['recommended', 'suggested', 'beneficial', 'valuable']
        
        combined_text = ' '.join(insights + recommendations).lower()
        
        if any(indicator in combined_text for indicator in high_priority_indicators):
            guidance['priority'] = 'high'
        elif any(indicator in combined_text for indicator in medium_priority_indicators):
            guidance['priority'] = 'medium'
        else:
            guidance['priority'] = 'low'
        
        # Estimate effort based on complexity
        complexity = spec_data.get('complexity_level', 2)
        if complexity >= 4:
            guidance['estimated_effort'] = 'high'
        elif complexity >= 3:
            guidance['estimated_effort'] = 'medium'
        else:
            guidance['estimated_effort'] = 'low'
        
        # Extract success factors
        success_indicators = ['success', 'effective', 'best practice', 'recommended', 'proven']
        for insight in insights:
            if any(indicator in insight.lower() for indicator in success_indicators):
                guidance['success_factors'].append(insight)
        
        # Extract risk factors
        risk_indicators = ['risk', 'challenge', 'difficulty', 'pitfall', 'problem', 'issue']
        for insight in insights:
            if any(indicator in insight.lower() for indicator in risk_indicators):
                guidance['risk_factors'].append(insight)
        
        # Generate next steps from recommendations
        guidance['next_steps'] = recommendations[:3]  # Top 3 recommendations
        
        return guidance
    
    def _validate_and_improve_spec(self, 
                                  spec_data: Dict[str, Any],
                                  complexity_level: int) -> Dict[str, Any]:
        """Validate and improve specification"""
        
        # Basic validation
        required_fields = ['title', 'description']
        for field in required_fields:
            if not spec_data.get(field):
                spec_data[field] = f"Generated specification (complexity level {complexity_level})"
        
        # Improve description if too short
        description = spec_data.get('description', '')
        if len(description) < 100:
            spec_data['description'] = f"{description}\n\nThis specification is based on comprehensive research and analysis."
        
        # Add validation metadata
        spec_data['validation_metadata'] = {
            'validated_at': datetime.now().isoformat(),
            'complexity_level': complexity_level,
            'validation_status': 'validated',
            'improvements_applied': [
                'Basic field validation',
                'Description enhancement',
                'Metadata addition'
            ]
        }
        
        return spec_data
