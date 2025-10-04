"""
Template generator for creating research-based templates
"""

from typing import Dict, List, Any, Optional
from datetime import datetime


class TemplateGenerator:
    """Generator for creating templates based on research results"""
    
    def __init__(self):
        self.template_categories = self._initialize_template_categories()
        self.generation_rules = self._initialize_generation_rules()
        self.field_extractors = self._initialize_field_extractors()
    
    def _initialize_template_categories(self) -> Dict[str, Dict[str, Any]]:
        """Initialize template categories and their structures"""
        return {
            'technical_implementation': {
                'description': 'Template for technical implementation projects',
                'required_fields': ['title', 'description', 'technical_requirements', 'architecture'],
                'optional_fields': ['performance_requirements', 'security_requirements', 'deployment_requirements'],
                'complexity_levels': [2, 3, 4]
            },
            'methodology_adoption': {
                'description': 'Template for methodology adoption projects',
                'required_fields': ['title', 'description', 'current_state', 'target_state', 'process_steps'],
                'optional_fields': ['team_requirements', 'training_needs', 'success_metrics'],
                'complexity_levels': [2, 3, 4]
            },
            'competitive_analysis': {
                'description': 'Template for competitive analysis projects',
                'required_fields': ['title', 'description', 'market_scope', 'competitors', 'analysis_framework'],
                'optional_fields': ['market_size', 'trends', 'recommendations'],
                'complexity_levels': [2, 3, 4]
            },
            'research_summary': {
                'description': 'Template for research summary documentation',
                'required_fields': ['title', 'summary', 'key_findings', 'recommendations'],
                'optional_fields': ['methodology', 'sources', 'limitations', 'future_research'],
                'complexity_levels': [1, 2, 3]
            }
        }
    
    def _initialize_generation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize rules for template generation"""
        return {
            'field_extraction': {
                'title': {
                    'sources': ['research_title', 'query'],
                    'transformation': 'title_case',
                    'max_length': 100
                },
                'description': {
                    'sources': ['synthesized_summary'],
                    'transformation': 'first_paragraph',
                    'min_length': 100
                },
                'technical_requirements': {
                    'sources': ['key_insights'],
                    'filter_keywords': ['requirement', 'need', 'must', 'should'],
                    'transformation': 'extract_requirements'
                },
                'architecture': {
                    'sources': ['key_insights', 'recommendations'],
                    'filter_keywords': ['architecture', 'design', 'structure', 'component'],
                    'transformation': 'extract_architecture'
                }
            },
            'content_enhancement': {
                'min_word_count': 50,
                'max_word_count': 500,
                'include_examples': True,
                'include_references': True
            }
        }
    
    def _initialize_field_extractors(self) -> Dict[str, Any]:
        """Initialize field extraction functions"""
        return {
            'title_case': self._to_title_case,
            'first_paragraph': self._extract_first_paragraph,
            'extract_requirements': self._extract_requirements,
            'extract_architecture': self._extract_architecture,
            'extract_insights': self._extract_insights,
            'extract_recommendations': self._extract_recommendations
        }
    
    def generate_template(self, 
                         research_data: Dict[str, Any],
                         template_category: str = 'research_summary',
                         complexity_level: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate template based on research data
        
        Args:
            research_data: Research data to use for template generation
            template_category: Category of template to generate
            complexity_level: Complexity level (1-4), auto-detected if None
        
        Returns:
            Generated template data
        """
        # Validate template category
        if template_category not in self.template_categories:
            raise ValueError(f"Unknown template category: {template_category}")
        
        category_config = self.template_categories[template_category]
        
        # Auto-detect complexity if not provided
        if complexity_level is None:
            complexity_level = self._detect_complexity(research_data, template_category)
        
        # Validate complexity level for category
        if complexity_level not in category_config['complexity_levels']:
            complexity_level = min(category_config['complexity_levels'])
        
        # Generate template
        template = {
            'template_metadata': {
                'category': template_category,
                'complexity_level': complexity_level,
                'generated_at': datetime.now().isoformat(),
                'source_research': research_data.get('query', 'Unknown'),
                'template_version': '1.0'
            }
        }
        
        # Generate required fields
        for field in category_config['required_fields']:
            template[field] = self._generate_field_content(field, research_data, category_config)
        
        # Generate optional fields
        for field in category_config['optional_fields']:
            content = self._generate_field_content(field, research_data, category_config)
            if content:  # Only include if content was generated
                template[field] = content
        
        # Add complexity-specific enhancements
        template = self._add_complexity_enhancements(template, complexity_level, research_data)
        
        # Validate and enhance template
        template = self._validate_and_enhance_template(template, category_config)
        
        return template
    
    def _detect_complexity(self, research_data: Dict[str, Any], template_category: str) -> int:
        """Detect appropriate complexity level for template"""
        insights = research_data.get('key_insights', [])
        recommendations = research_data.get('recommendations', [])
        
        combined_text = ' '.join(insights + recommendations).lower()
        
        # Complexity indicators
        high_complexity_indicators = ['architecture', 'system', 'enterprise', 'complex', 'advanced']
        medium_complexity_indicators = ['integration', 'framework', 'methodology', 'process']
        
        if any(indicator in combined_text for indicator in high_complexity_indicators):
            return 4
        elif any(indicator in combined_text for indicator in medium_complexity_indicators):
            return 3
        else:
            return 2
    
    def _generate_field_content(self, 
                               field_name: str,
                               research_data: Dict[str, Any],
                               category_config: Dict[str, Any]) -> str:
        """Generate content for a specific field"""
        generation_rules = self.generation_rules['field_extraction']
        field_rules = generation_rules.get(field_name, {})
        
        # Get source data
        sources = field_rules.get('sources', [field_name])
        source_data = []
        
        for source in sources:
            if source in research_data:
                source_data.append(research_data[source])
        
        if not source_data:
            return self._generate_default_content(field_name, category_config)
        
        # Apply transformation
        transformation = field_rules.get('transformation', 'extract_insights')
        if transformation in self.field_extractors:
            content = self.field_extractors[transformation](source_data, field_rules)
        else:
            content = self._extract_insights(source_data, field_rules)
        
        # Apply length constraints
        max_length = field_rules.get('max_length', 500)
        min_length = field_rules.get('min_length', 10)
        
        if len(content) > max_length:
            content = content[:max_length] + "..."
        
        if len(content) < min_length:
            content = self._enhance_content_length(content, min_length, field_name)
        
        return content
    
    def _generate_default_content(self, field_name: str, category_config: Dict[str, Any]) -> str:
        """Generate default content for a field when no research data is available"""
        defaults = {
            'title': f"Generated {category_config['description'].lower()}",
            'description': f"This is a generated template for {category_config['description'].lower()}.",
            'technical_requirements': "Technical requirements will be defined during implementation planning.",
            'architecture': "System architecture will be designed based on requirements analysis.",
            'current_state': "Current state assessment will be conducted during project initiation.",
            'target_state': "Target state will be defined based on business objectives.",
            'process_steps': "Process steps will be detailed during implementation planning.",
            'market_scope': "Market scope will be defined based on business strategy.",
            'competitors': "Competitor analysis will be conducted during research phase.",
            'analysis_framework': "Analysis framework will be established based on business needs.",
            'summary': "Research summary will be compiled from findings.",
            'key_findings': "Key findings will be extracted from research analysis.",
            'recommendations': "Recommendations will be developed based on research insights."
        }
        
        return defaults.get(field_name, f"Content for {field_name} field.")
    
    def _to_title_case(self, data: List[Any], rules: Dict[str, Any]) -> str:
        """Convert text to title case"""
        if not data:
            return ""
        
        text = str(data[0])
        return text.title()
    
    def _extract_first_paragraph(self, data: List[Any], rules: Dict[str, Any]) -> str:
        """Extract first paragraph from text"""
        if not data:
            return ""
        
        text = str(data[0])
        # Split by paragraphs and take first one
        paragraphs = text.split('\n\n')
        first_paragraph = paragraphs[0] if paragraphs else text
        
        return first_paragraph.strip()
    
    def _extract_requirements(self, data: List[Any], rules: Dict[str, Any]) -> str:
        """Extract requirements from insights"""
        if not data:
            return ""
        
        # Combine all data
        combined_text = ' '.join(str(item) for item in data)
        
        # Look for requirement-related content
        requirement_keywords = rules.get('filter_keywords', ['requirement', 'need', 'must', 'should'])
        sentences = combined_text.split('.')
        
        requirement_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if any(keyword in sentence.lower() for keyword in requirement_keywords):
                requirement_sentences.append(sentence)
        
        if requirement_sentences:
            return '. '.join(requirement_sentences[:3]) + '.'  # Limit to 3 sentences
        else:
            return "Requirements will be defined based on business needs and technical constraints."
    
    def _extract_architecture(self, data: List[Any], rules: Dict[str, Any]) -> str:
        """Extract architecture-related content"""
        if not data:
            return ""
        
        # Combine all data
        combined_text = ' '.join(str(item) for item in data)
        
        # Look for architecture-related content
        architecture_keywords = rules.get('filter_keywords', ['architecture', 'design', 'structure', 'component'])
        sentences = combined_text.split('.')
        
        architecture_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if any(keyword in sentence.lower() for keyword in architecture_keywords):
                architecture_sentences.append(sentence)
        
        if architecture_sentences:
            return '. '.join(architecture_sentences[:3]) + '.'  # Limit to 3 sentences
        else:
            return "System architecture will be designed to meet functional and non-functional requirements."
    
    def _extract_insights(self, data: List[Any], rules: Dict[str, Any]) -> str:
        """Extract insights from research data"""
        if not data:
            return ""
        
        # Handle different data types
        if isinstance(data[0], list):
            # If it's a list of insights
            insights = data[0]
            if insights:
                return '. '.join(insights[:3]) + '.'  # Limit to 3 insights
        else:
            # If it's a single text field
            text = str(data[0])
            if len(text) > 200:
                return text[:200] + "..."
            return text
        
        return "Key insights will be documented based on research findings."
    
    def _extract_recommendations(self, data: List[Any], rules: Dict[str, Any]) -> str:
        """Extract recommendations from research data"""
        if not data:
            return ""
        
        # Handle different data types
        if isinstance(data[0], list):
            # If it's a list of recommendations
            recommendations = data[0]
            if recommendations:
                return '. '.join(recommendations[:3]) + '.'  # Limit to 3 recommendations
        else:
            # If it's a single text field
            text = str(data[0])
            if len(text) > 200:
                return text[:200] + "..."
            return text
        
        return "Recommendations will be developed based on research analysis."
    
    def _enhance_content_length(self, content: str, min_length: int, field_name: str) -> str:
        """Enhance content to meet minimum length requirements"""
        if len(content) >= min_length:
            return content
        
        # Add contextual information
        enhancements = {
            'technical_requirements': " These requirements will guide the implementation approach and system design.",
            'architecture': " This architecture will ensure scalability, maintainability, and performance.",
            'process_steps': " These steps will be refined during detailed planning and implementation.",
            'competitors': " This analysis will inform strategic positioning and competitive differentiation.",
            'key_findings': " These findings provide the foundation for decision-making and implementation planning.",
            'recommendations': " These recommendations should be prioritized based on business impact and feasibility."
        }
        
        enhancement = enhancements.get(field_name, " This information will be refined during project execution.")
        enhanced_content = content + enhancement
        
        return enhanced_content if len(enhanced_content) >= min_length else content
    
    def _add_complexity_enhancements(self, 
                                   template: Dict[str, Any],
                                   complexity_level: int,
                                   research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add complexity-specific enhancements to template"""
        
        if complexity_level >= 4:
            # High complexity enhancements
            template['complexity_notes'] = "High complexity project requiring expert team and detailed planning."
            template['risk_considerations'] = "High complexity increases risk of scope creep and implementation challenges."
            template['resource_requirements'] = "Requires experienced team with specialized skills and extended timeline."
            
        elif complexity_level >= 3:
            # Medium-high complexity enhancements
            template['complexity_notes'] = "Medium-high complexity project requiring careful planning and experienced team."
            template['coordination_requirements'] = "Requires effective coordination between multiple team members and stakeholders."
            
        elif complexity_level >= 2:
            # Medium complexity enhancements
            template['complexity_notes'] = "Medium complexity project with standard implementation requirements."
            template['team_requirements'] = "Requires competent team with relevant domain knowledge."
        
        # Add research-based enhancements
        if research_data.get('confidence_score', 0) < 0.7:
            template['research_limitations'] = "Research findings have moderate confidence level. Additional validation recommended."
        
        if research_data.get('quality_score', 0) < 0.7:
            template['quality_considerations'] = "Research quality is below optimal. Consider additional research sources."
        
        return template
    
    def _validate_and_enhance_template(self, 
                                     template: Dict[str, Any],
                                     category_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance generated template"""
        
        # Validate required fields
        missing_fields = []
        for field in category_config['required_fields']:
            if field not in template or not template[field]:
                missing_fields.append(field)
                template[field] = self._generate_default_content(field, category_config)
        
        # Add validation metadata
        template['validation_metadata'] = {
            'validated_at': datetime.now().isoformat(),
            'missing_fields_filled': missing_fields,
            'template_completeness': len([f for f in category_config['required_fields'] if f in template and template[f]]) / len(category_config['required_fields']),
            'enhancements_applied': [
                'Field validation',
                'Content enhancement',
                'Metadata addition'
            ]
        }
        
        return template
    
    def generate_multiple_templates(self, 
                                  research_data: Dict[str, Any],
                                  template_categories: List[str],
                                  complexity_levels: Optional[List[int]] = None) -> Dict[str, Dict[str, Any]]:
        """Generate multiple templates from the same research data"""
        
        if complexity_levels is None:
            complexity_levels = [2, 3, 4]  # Default complexity levels
        
        templates = {}
        
        for category in template_categories:
            for complexity in complexity_levels:
                if complexity in self.template_categories[category]['complexity_levels']:
                    key = f"{category}_level_{complexity}"
                    try:
                        templates[key] = self.generate_template(
                            research_data=research_data,
                            template_category=category,
                            complexity_level=complexity
                        )
                    except Exception as e:
                        print(f"Warning: Could not generate template {key}: {e}")
        
        return templates
