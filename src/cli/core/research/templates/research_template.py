"""
Base research template for Memory Bank research system
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum


class ResearchType(Enum):
    """Types of research that can be conducted"""
    TECHNICAL = "technical"
    METHODOLOGY = "methodology"
    COMPETITIVE = "competitive"
    MARKET = "market"
    ARCHITECTURE = "architecture"
    PERFORMANCE = "performance"
    SECURITY = "security"
    COMPLIANCE = "compliance"


class ResearchStatus(Enum):
    """Status of research process"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VALIDATED = "validated"
    FAILED = "failed"


@dataclass
class Source:
    """Represents a research source"""
    url: str
    title: str
    domain: str
    content: str
    credibility_score: float
    freshness_score: float
    relevance_score: float
    accessed_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AIAnalysis:
    """Represents AI analysis results"""
    agent_name: str
    analysis_type: str
    summary: str
    key_findings: List[str]
    confidence_score: float
    recommendations: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResearchResult:
    """Complete research result"""
    query: str
    research_type: ResearchType
    status: ResearchStatus
    sources: List[Source]
    ai_analyses: List[AIAnalysis]
    synthesized_summary: str
    key_insights: List[str]
    recommendations: List[str]
    confidence_score: float
    completeness_score: float
    quality_score: float
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class ResearchTemplate:
    """Base template for research operations"""
    
    def __init__(self, research_type: ResearchType):
        self.research_type = research_type
        self.required_fields = self._get_required_fields()
        self.optional_fields = self._get_optional_fields()
        self.validation_rules = self._get_validation_rules()
    
    def _get_required_fields(self) -> List[str]:
        """Get list of required fields for this research type"""
        base_fields = [
            'query',
            'research_type',
            'sources',
            'summary',
            'key_findings'
        ]
        
        # Add type-specific required fields
        if self.research_type == ResearchType.TECHNICAL:
            base_fields.extend(['technical_details', 'implementation_notes'])
        elif self.research_type == ResearchType.METHODOLOGY:
            base_fields.extend(['methodology_overview', 'best_practices'])
        elif self.research_type == ResearchType.COMPETITIVE:
            base_fields.extend(['competitors', 'comparison_matrix'])
        
        return base_fields
    
    def _get_optional_fields(self) -> List[str]:
        """Get list of optional fields for this research type"""
        return [
            'assumptions',
            'limitations',
            'future_research',
            'related_topics',
            'references'
        ]
    
    def _get_validation_rules(self) -> Dict[str, Any]:
        """Get validation rules for this research type"""
        return {
            'min_sources': 3,
            'min_summary_length': 100,
            'min_key_findings': 3,
            'max_sources': 20,
            'min_confidence_score': 0.6
        }
    
    def validate_research(self, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate research data against template rules"""
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'score': 0
        }
        
        # Check required fields
        for field in self.required_fields:
            if field not in research_data or not research_data[field]:
                validation_result['errors'].append(f"Required field '{field}' is missing")
                validation_result['is_valid'] = False
        
        # Check source count
        sources = research_data.get('sources', [])
        min_sources = self.validation_rules['min_sources']
        max_sources = self.validation_rules['max_sources']
        
        if len(sources) < min_sources:
            validation_result['warnings'].append(f"Minimum {min_sources} sources recommended")
        elif len(sources) > max_sources:
            validation_result['warnings'].append(f"Too many sources ({len(sources)}), consider filtering")
        
        # Check summary length
        summary = research_data.get('summary', '')
        min_length = self.validation_rules['min_summary_length']
        if len(summary) < min_length:
            validation_result['warnings'].append(f"Summary too short (min {min_length} characters)")
        
        # Check key findings
        key_findings = research_data.get('key_findings', [])
        min_findings = self.validation_rules['min_key_findings']
        if len(key_findings) < min_findings:
            validation_result['warnings'].append(f"At least {min_findings} key findings recommended")
        
        # Calculate score
        validation_result['score'] = self._calculate_validation_score(research_data)
        
        return validation_result
    
    def generate_template(self, topic: str, depth) -> Dict[str, Any]:
        """Generate research template"""
        from ..validation.research_validator import ResearchDepth
        
        template_data = {
            "topic": topic,
            "depth": depth.value if hasattr(depth, 'value') else str(depth),
            "status": "template_generated",
            "created_at": datetime.now().isoformat(),
            "research_fields": self.get_research_fields(),
            "validation_rules": self.get_validation_rules(),
            "metadata": {
                "template_type": "base_research",
                "version": "1.0.0",
                "generated_by": "research_engine"
            }
        }
        
        return template_data
    
    def get_research_fields(self) -> Dict[str, Any]:
        """Get research fields structure"""
        return {
            "overview": {
                "description": "Research overview and objectives",
                "required": True,
                "type": "text"
            },
            "methodology": {
                "description": "Research methodology and approach",
                "required": True,
                "type": "text"
            },
            "sources": {
                "description": "Research sources and references",
                "required": True,
                "type": "list"
            },
            "findings": {
                "description": "Key research findings",
                "required": True,
                "type": "text"
            },
            "recommendations": {
                "description": "Research recommendations and next steps",
                "required": False,
                "type": "text"
            }
        }
    
    def get_validation_rules(self) -> Dict[str, Any]:
        """Get validation rules for research"""
        return {
            "required_fields": ["overview", "methodology", "sources", "findings"],
            "min_source_count": 3,
            "min_finding_length": 100,
            "max_research_age_days": 365
        }
    
    def _calculate_validation_score(self, research_data: Dict[str, Any]) -> float:
        """Calculate validation score based on completeness and quality"""
        score = 0.0
        max_score = 100.0
        
        # Required fields completeness (40 points)
        required_completeness = len([f for f in self.required_fields if f in research_data and research_data[f]]) / len(self.required_fields)
        score += required_completeness * 40
        
        # Source quality (30 points)
        sources = research_data.get('sources', [])
        if sources:
            avg_credibility = sum(s.get('credibility_score', 0) for s in sources) / len(sources)
            score += avg_credibility * 30
        
        # Content quality (20 points)
        summary = research_data.get('summary', '')
        if len(summary) >= self.validation_rules['min_summary_length']:
            score += 20
        
        # Key findings quality (10 points)
        key_findings = research_data.get('key_findings', [])
        if len(key_findings) >= self.validation_rules['min_key_findings']:
            score += 10
        
        return min(score, max_score)
    
    def generate_research_outline(self, query: str) -> Dict[str, Any]:
        """Generate research outline based on query and type"""
        outline = {
            'query': query,
            'research_type': self.research_type.value,
            'sections': self._get_research_sections(),
            'estimated_time': self._estimate_research_time(),
            'suggested_sources': self._get_suggested_sources(),
            'key_questions': self._get_key_questions(query)
        }
        
        return outline
    
    def _get_research_sections(self) -> List[str]:
        """Get research sections based on type"""
        base_sections = [
            'Executive Summary',
            'Key Findings',
            'Detailed Analysis',
            'Recommendations',
            'References'
        ]
        
        if self.research_type == ResearchType.TECHNICAL:
            base_sections.insert(2, 'Technical Implementation')
            base_sections.insert(3, 'Performance Considerations')
        elif self.research_type == ResearchType.METHODOLOGY:
            base_sections.insert(2, 'Methodology Overview')
            base_sections.insert(3, 'Best Practices')
        elif self.research_type == ResearchType.COMPETITIVE:
            base_sections.insert(2, 'Competitive Landscape')
            base_sections.insert(3, 'Comparison Analysis')
        
        return base_sections
    
    def _estimate_research_time(self) -> str:
        """Estimate research time based on type"""
        estimates = {
            ResearchType.TECHNICAL: "2-4 hours",
            ResearchType.METHODOLOGY: "3-6 hours", 
            ResearchType.COMPETITIVE: "4-8 hours",
            ResearchType.MARKET: "6-12 hours",
            ResearchType.ARCHITECTURE: "4-8 hours",
            ResearchType.PERFORMANCE: "2-4 hours",
            ResearchType.SECURITY: "3-6 hours",
            ResearchType.COMPLIANCE: "4-8 hours"
        }
        
        return estimates.get(self.research_type, "2-6 hours")
    
    def _get_suggested_sources(self) -> List[str]:
        """Get suggested source types based on research type"""
        source_types = {
            ResearchType.TECHNICAL: [
                "Official documentation",
                "GitHub repositories",
                "Technical blogs",
                "Stack Overflow",
                "Academic papers"
            ],
            ResearchType.METHODOLOGY: [
                "Industry reports",
                "Case studies",
                "Best practice guides",
                "Expert interviews",
                "Professional forums"
            ],
            ResearchType.COMPETITIVE: [
                "Company websites",
                "Product documentation",
                "User reviews",
                "Industry analysis",
                "Financial reports"
            ]
        }
        
        return source_types.get(self.research_type, [
            "Official documentation",
            "Industry reports",
            "Expert analysis",
            "User feedback",
            "Case studies"
        ])
    
    def _get_key_questions(self, query: str) -> List[str]:
        """Generate key questions based on query and research type"""
        base_questions = [
            f"What are the key aspects of {query}?",
            f"What are the current trends and developments?",
            f"What are the main challenges and limitations?",
            f"What are the best practices and recommendations?"
        ]
        
        if self.research_type == ResearchType.TECHNICAL:
            base_questions.extend([
                f"How is {query} implemented technically?",
                f"What are the performance characteristics?",
                f"What are the security considerations?"
            ])
        elif self.research_type == ResearchType.METHODOLOGY:
            base_questions.extend([
                f"What methodologies are used for {query}?",
                f"What are the pros and cons of different approaches?",
                f"How do you measure success in {query}?"
            ])
        elif self.research_type == ResearchType.COMPETITIVE:
            base_questions.extend([
                f"Who are the main competitors in {query}?",
                f"What are the competitive advantages?",
                f"How do they differentiate themselves?"
            ])
        
        return base_questions
