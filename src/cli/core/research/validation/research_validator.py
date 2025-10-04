"""
Research validator for quality assessment and validation
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

from ..templates.research_template import ResearchResult, Source, AIAnalysis, ResearchType


class ResearchDepth(Enum):
    """Research depth levels"""
    SHALLOW = "shallow"
    MEDIUM = "medium"
    DEEP = "deep"
from .source_validator import SourceValidator
from .credibility_scorer import CredibilityScorer
from .freshness_checker import FreshnessChecker
from .completeness_assessor import CompletenessAssessor


class ResearchValidator:
    """Main validator for research quality assessment"""
    
    def __init__(self):
        self.source_validator = SourceValidator()
        self.credibility_scorer = CredibilityScorer()
        self.freshness_checker = FreshnessChecker()
        self.completeness_assessor = CompletenessAssessor()
        self.validation_rules = self._initialize_validation_rules()
    
    def _initialize_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize validation rules for different research types"""
        return {
            ResearchType.TECHNICAL.value: {
                'min_sources': 3,
                'min_ai_analyses': 2,
                'min_summary_length': 200,
                'min_insights': 3,
                'min_recommendations': 2,
                'min_confidence_score': 0.6,
                'min_completeness_score': 0.7,
                'min_quality_score': 0.6
            },
            ResearchType.METHODOLOGY.value: {
                'min_sources': 4,
                'min_ai_analyses': 3,
                'min_summary_length': 300,
                'min_insights': 4,
                'min_recommendations': 3,
                'min_confidence_score': 0.65,
                'min_completeness_score': 0.75,
                'min_quality_score': 0.65
            },
            ResearchType.COMPETITIVE.value: {
                'min_sources': 5,
                'min_ai_analyses': 3,
                'min_summary_length': 400,
                'min_insights': 5,
                'min_recommendations': 4,
                'min_confidence_score': 0.7,
                'min_completeness_score': 0.8,
                'min_quality_score': 0.7
            }
        }
    
    def validate_research(self, research_result: ResearchResult) -> Dict[str, Any]:
        """
        Validate research result comprehensively
        
        Args:
            research_result: Research result to validate
        
        Returns:
            Validation results with scores and recommendations
        """
        validation_result = {
            'is_valid': True,
            'overall_score': 0.0,
            'dimension_scores': {},
            'errors': [],
            'warnings': [],
            'recommendations': [],
            'validation_timestamp': datetime.now().isoformat()
        }
        
        # Get validation rules for research type
        rules = self.validation_rules.get(
            research_result.research_type.value,
            self.validation_rules[ResearchType.TECHNICAL.value]
        )
        
        # Validate sources
        source_validation = self._validate_sources(research_result.sources, rules)
        validation_result['dimension_scores']['sources'] = source_validation['score']
        validation_result['errors'].extend(source_validation['errors'])
        validation_result['warnings'].extend(source_validation['warnings'])
        
        # Validate AI analyses
        analysis_validation = self._validate_analyses(research_result.ai_analyses, rules)
        validation_result['dimension_scores']['analyses'] = analysis_validation['score']
        validation_result['errors'].extend(analysis_validation['errors'])
        validation_result['warnings'].extend(analysis_validation['warnings'])
        
        # Validate content quality
        content_validation = self._validate_content(research_result, rules)
        validation_result['dimension_scores']['content'] = content_validation['score']
        validation_result['errors'].extend(content_validation['errors'])
        validation_result['warnings'].extend(content_validation['warnings'])
        
        # Validate synthesis quality
        synthesis_validation = self._validate_synthesis(research_result, rules)
        validation_result['dimension_scores']['synthesis'] = synthesis_validation['score']
        validation_result['errors'].extend(synthesis_validation['errors'])
        validation_result['warnings'].extend(synthesis_validation['warnings'])
        
        # Calculate overall score
        validation_result['overall_score'] = self._calculate_overall_score(validation_result['dimension_scores'])
        
        # Determine validity
        if validation_result['errors']:
            validation_result['is_valid'] = False
        
        # Generate recommendations
        validation_result['recommendations'] = self._generate_recommendations(
            validation_result, research_result, rules
        )
        
        return validation_result
    
    def _validate_sources(self, sources: List[Source], rules: Dict[str, Any]) -> Dict[str, Any]:
        """Validate source quality and quantity"""
        validation = {
            'score': 0.0,
            'errors': [],
            'warnings': []
        }
        
        # Check minimum source count
        min_sources = rules['min_sources']
        if len(sources) < min_sources:
            validation['errors'].append(f"Minimum {min_sources} sources required, found {len(sources)}")
        
        # Validate individual sources
        if sources:
            source_scores = []
            for i, source in enumerate(sources):
                source_validation = self.source_validator.validate_source(source)
                source_scores.append(source_validation['score'])
                
                if source_validation['score'] < 0.6:
                    validation['warnings'].append(f"Source {i+1} has low quality score: {source_validation['score']:.2f}")
            
            validation['score'] = sum(source_scores) / len(source_scores)
        else:
            validation['score'] = 0.0
        
        return validation
    
    def _validate_analyses(self, analyses: List[AIAnalysis], rules: Dict[str, Any]) -> Dict[str, Any]:
        """Validate AI analysis quality and quantity"""
        validation = {
            'score': 0.0,
            'errors': [],
            'warnings': []
        }
        
        # Check minimum analysis count
        min_analyses = rules['min_ai_analyses']
        if len(analyses) < min_analyses:
            validation['errors'].append(f"Minimum {min_analyses} AI analyses required, found {len(analyses)}")
        
        # Validate individual analyses
        if analyses:
            analysis_scores = []
            for i, analysis in enumerate(analyses):
                analysis_score = self._validate_single_analysis(analysis)
                analysis_scores.append(analysis_score)
                
                if analysis_score < 0.6:
                    validation['warnings'].append(f"Analysis {i+1} ({analysis.agent_name}) has low quality score: {analysis_score:.2f}")
            
            validation['score'] = sum(analysis_scores) / len(analysis_scores)
        else:
            validation['score'] = 0.0
        
        return validation
    
    def _validate_single_analysis(self, analysis: AIAnalysis) -> float:
        """Validate a single AI analysis"""
        score = 0.0
        
        # Summary quality (30%)
        if analysis.summary and len(analysis.summary) >= 50:
            score += 0.3
        
        # Key findings quality (25%)
        if analysis.key_findings and len(analysis.key_findings) >= 2:
            score += 0.25
        
        # Recommendations quality (20%)
        if analysis.recommendations and len(analysis.recommendations) >= 1:
            score += 0.2
        
        # Confidence score (25%)
        score += analysis.confidence_score * 0.25
        
        return score
    
    def _validate_content(self, research_result: ResearchResult, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Validate content quality"""
        validation = {
            'score': 0.0,
            'errors': [],
            'warnings': []
        }
        
        score = 0.0
        
        # Summary length validation
        min_summary_length = rules['min_summary_length']
        if len(research_result.synthesized_summary) < min_summary_length:
            validation['warnings'].append(f"Summary too short (min {min_summary_length} characters)")
        else:
            score += 0.3
        
        # Insights validation
        min_insights = rules['min_insights']
        if len(research_result.key_insights) < min_insights:
            validation['warnings'].append(f"Too few insights (min {min_insights})")
        else:
            score += 0.3
        
        # Recommendations validation
        min_recommendations = rules['min_recommendations']
        if len(research_result.recommendations) < min_recommendations:
            validation['warnings'].append(f"Too few recommendations (min {min_recommendations})")
        else:
            score += 0.4
        
        validation['score'] = score
        return validation
    
    def _validate_synthesis(self, research_result: ResearchResult, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Validate synthesis quality"""
        validation = {
            'score': 0.0,
            'errors': [],
            'warnings': []
        }
        
        score = 0.0
        
        # Confidence score validation
        min_confidence = rules['min_confidence_score']
        if research_result.confidence_score < min_confidence:
            validation['warnings'].append(f"Low confidence score: {research_result.confidence_score:.2f} (min {min_confidence})")
        else:
            score += 0.4
        
        # Completeness score validation
        min_completeness = rules['min_completeness_score']
        if research_result.completeness_score < min_completeness:
            validation['warnings'].append(f"Low completeness score: {research_result.completeness_score:.2f} (min {min_completeness})")
        else:
            score += 0.3
        
        # Quality score validation
        min_quality = rules['min_quality_score']
        if research_result.quality_score < min_quality:
            validation['warnings'].append(f"Low quality score: {research_result.quality_score:.2f} (min {min_quality})")
        else:
            score += 0.3
        
        validation['score'] = score
        return validation
    
    def _calculate_overall_score(self, dimension_scores: Dict[str, float]) -> float:
        """Calculate overall validation score"""
        if not dimension_scores:
            return 0.0
        
        # Weighted average of dimension scores
        weights = {
            'sources': 0.25,
            'analyses': 0.25,
            'content': 0.25,
            'synthesis': 0.25
        }
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for dimension, score in dimension_scores.items():
            weight = weights.get(dimension, 0.25)
            weighted_sum += score * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _generate_recommendations(self, 
                                 validation_result: Dict[str, Any],
                                 research_result: ResearchResult,
                                 rules: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Source recommendations
        if validation_result['dimension_scores'].get('sources', 0) < 0.7:
            recommendations.append("Collect more high-quality sources from authoritative domains")
        
        # Analysis recommendations
        if validation_result['dimension_scores'].get('analyses', 0) < 0.7:
            recommendations.append("Increase number of AI analyses or improve analysis quality")
        
        # Content recommendations
        if validation_result['dimension_scores'].get('content', 0) < 0.7:
            recommendations.append("Expand summary and provide more detailed insights and recommendations")
        
        # Synthesis recommendations
        if validation_result['dimension_scores'].get('synthesis', 0) < 0.7:
            recommendations.append("Improve synthesis quality by resolving conflicts and increasing confidence")
        
        # Specific rule-based recommendations
        if len(research_result.sources) < rules['min_sources']:
            recommendations.append(f"Add at least {rules['min_sources'] - len(research_result.sources)} more sources")
        
        if len(research_result.ai_analyses) < rules['min_ai_analyses']:
            recommendations.append(f"Conduct at least {rules['min_ai_analyses'] - len(research_result.ai_analyses)} more AI analyses")
        
        if len(research_result.synthesized_summary) < rules['min_summary_length']:
            recommendations.append(f"Expand summary to at least {rules['min_summary_length']} characters")
        
        return recommendations
