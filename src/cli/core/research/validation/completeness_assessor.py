"""
Completeness assessor for evaluating research coverage and thoroughness
"""

from typing import Dict, List, Any, Optional
from collections import Counter


class CompletenessAssessor:
    """Assessor for evaluating research completeness and coverage"""
    
    def __init__(self):
        self.coverage_indicators = self._initialize_coverage_indicators()
        self.thoroughness_metrics = self._initialize_thoroughness_metrics()
        self.completeness_thresholds = self._initialize_completeness_thresholds()
    
    def _initialize_coverage_indicators(self) -> Dict[str, List[str]]:
        """Initialize coverage indicators for different research types"""
        return {
            'technical': {
                'implementation': ['implementation', 'setup', 'installation', 'configuration', 'deployment'],
                'usage': ['usage', 'example', 'tutorial', 'guide', 'how to'],
                'api': ['api', 'interface', 'endpoint', 'method', 'function'],
                'performance': ['performance', 'speed', 'efficiency', 'optimization', 'scalability'],
                'security': ['security', 'authentication', 'authorization', 'encryption', 'vulnerability'],
                'testing': ['testing', 'test', 'validation', 'verification', 'quality assurance'],
                'troubleshooting': ['troubleshooting', 'debug', 'error', 'issue', 'problem', 'fix']
            },
            'methodology': {
                'overview': ['overview', 'introduction', 'summary', 'description', 'definition'],
                'process': ['process', 'steps', 'workflow', 'procedure', 'methodology'],
                'best_practices': ['best practice', 'recommendation', 'guideline', 'standard', 'principle'],
                'tools': ['tool', 'framework', 'platform', 'software', 'system'],
                'team': ['team', 'role', 'responsibility', 'collaboration', 'communication'],
                'metrics': ['metric', 'measurement', 'kpi', 'indicator', 'success'],
                'challenges': ['challenge', 'pitfall', 'obstacle', 'difficulty', 'risk']
            },
            'competitive': {
                'market': ['market', 'industry', 'landscape', 'ecosystem', 'environment'],
                'competitors': ['competitor', 'rival', 'alternative', 'option', 'solution'],
                'features': ['feature', 'capability', 'function', 'characteristic', 'attribute'],
                'pricing': ['pricing', 'cost', 'price', 'fee', 'subscription'],
                'positioning': ['positioning', 'differentiation', 'advantage', 'strength', 'weakness'],
                'trends': ['trend', 'direction', 'evolution', 'change', 'future'],
                'analysis': ['analysis', 'comparison', 'evaluation', 'assessment', 'review']
            }
        }
    
    def _initialize_thoroughness_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Initialize thoroughness assessment metrics"""
        return {
            'depth': {
                'weight': 0.3,
                'indicators': ['detailed', 'comprehensive', 'in-depth', 'thorough', 'extensive'],
                'thresholds': {'excellent': 5, 'good': 3, 'adequate': 2, 'poor': 1}
            },
            'breadth': {
                'weight': 0.25,
                'indicators': ['multiple', 'various', 'different', 'range', 'spectrum'],
                'thresholds': {'excellent': 4, 'good': 3, 'adequate': 2, 'poor': 1}
            },
            'accuracy': {
                'weight': 0.2,
                'indicators': ['accurate', 'precise', 'correct', 'validated', 'verified'],
                'thresholds': {'excellent': 4, 'good': 3, 'adequate': 2, 'poor': 1}
            },
            'relevance': {
                'weight': 0.15,
                'indicators': ['relevant', 'applicable', 'pertinent', 'appropriate', 'suitable'],
                'thresholds': {'excellent': 4, 'good': 3, 'adequate': 2, 'poor': 1}
            },
            'actionability': {
                'weight': 0.1,
                'indicators': ['actionable', 'practical', 'implementable', 'usable', 'applicable'],
                'thresholds': {'excellent': 4, 'good': 3, 'adequate': 2, 'poor': 1}
            }
        }
    
    def _initialize_completeness_thresholds(self) -> Dict[str, Dict[str, Any]]:
        """Initialize completeness assessment thresholds"""
        return {
            'coverage': {
                'excellent': 0.9,
                'good': 0.75,
                'adequate': 0.6,
                'poor': 0.4
            },
            'thoroughness': {
                'excellent': 0.9,
                'good': 0.75,
                'adequate': 0.6,
                'poor': 0.4
            },
            'overall': {
                'excellent': 0.9,
                'good': 0.75,
                'adequate': 0.6,
                'poor': 0.4
            }
        }
    
    def assess_completeness(self, 
                           research_result: Any,
                           research_type: str = 'technical') -> Dict[str, Any]:
        """
        Assess research completeness and coverage
        
        Args:
            research_result: Research result to assess
            research_type: Type of research being assessed
        
        Returns:
            Completeness assessment results
        """
        assessment = {
            'overall_score': 0.0,
            'coverage_score': 0.0,
            'thoroughness_score': 0.0,
            'missing_areas': [],
            'strengths': [],
            'weaknesses': [],
            'recommendations': [],
            'details': {}
        }
        
        # Assess coverage
        coverage_assessment = self._assess_coverage(research_result, research_type)
        assessment['coverage_score'] = coverage_assessment['score']
        assessment['missing_areas'] = coverage_assessment['missing_areas']
        assessment['strengths'].extend(coverage_assessment['strengths'])
        assessment['weaknesses'].extend(coverage_assessment['weaknesses'])
        
        # Assess thoroughness
        thoroughness_assessment = self._assess_thoroughness(research_result)
        assessment['thoroughness_score'] = thoroughness_assessment['score']
        assessment['strengths'].extend(thoroughness_assessment['strengths'])
        assessment['weaknesses'].extend(thoroughness_assessment['weaknesses'])
        
        # Calculate overall score
        assessment['overall_score'] = (assessment['coverage_score'] * 0.6 + 
                                     assessment['thoroughness_score'] * 0.4)
        
        # Generate recommendations
        assessment['recommendations'] = self._generate_completeness_recommendations(assessment)
        
        # Add detailed analysis
        assessment['details'] = {
            'coverage_details': coverage_assessment['details'],
            'thoroughness_details': thoroughness_assessment['details'],
            'research_type': research_type,
            'assessment_timestamp': '2024-01-01T00:00:00'  # Would use datetime.now() in real implementation
        }
        
        return assessment
    
    def _assess_coverage(self, research_result: Any, research_type: str) -> Dict[str, Any]:
        """Assess coverage of different research areas"""
        coverage_result = {
            'score': 0.0,
            'missing_areas': [],
            'strengths': [],
            'weaknesses': [],
            'details': {}
        }
        
        # Get coverage indicators for research type
        indicators = self.coverage_indicators.get(research_type, self.coverage_indicators['technical'])
        
        # Combine all content for analysis
        content = self._extract_content(research_result)
        content_lower = content.lower()
        
        # Check coverage of each area
        area_scores = {}
        for area, keywords in indicators.items():
            keyword_matches = sum(1 for keyword in keywords if keyword in content_lower)
            coverage_ratio = keyword_matches / len(keywords)
            area_scores[area] = coverage_ratio
            
            if coverage_ratio >= 0.8:
                coverage_result['strengths'].append(f"Strong coverage of {area}")
            elif coverage_ratio >= 0.5:
                coverage_result['strengths'].append(f"Good coverage of {area}")
            elif coverage_ratio >= 0.3:
                coverage_result['weaknesses'].append(f"Limited coverage of {area}")
            else:
                coverage_result['missing_areas'].append(area)
                coverage_result['weaknesses'].append(f"Missing coverage of {area}")
        
        # Calculate overall coverage score
        if area_scores:
            coverage_result['score'] = sum(area_scores.values()) / len(area_scores)
        else:
            coverage_result['score'] = 0.0
        
        coverage_result['details'] = {
            'area_scores': area_scores,
            'total_areas': len(indicators),
            'covered_areas': len([area for area, score in area_scores.items() if score > 0.3]),
            'coverage_percentage': coverage_result['score'] * 100
        }
        
        return coverage_result
    
    def _assess_thoroughness(self, research_result: Any) -> Dict[str, Any]:
        """Assess thoroughness of research"""
        thoroughness_result = {
            'score': 0.0,
            'strengths': [],
            'weaknesses': [],
            'details': {}
        }
        
        content = self._extract_content(research_result)
        content_lower = content.lower()
        
        # Assess each thoroughness dimension
        dimension_scores = {}
        for dimension, config in self.thoroughness_metrics.items():
            weight = config['weight']
            indicators = config['indicators']
            thresholds = config['thresholds']
            
            # Count indicator matches
            indicator_matches = sum(1 for indicator in indicators if indicator in content_lower)
            
            # Score based on thresholds
            if indicator_matches >= thresholds['excellent']:
                score = 1.0
                thoroughness_result['strengths'].append(f"Excellent {dimension}")
            elif indicator_matches >= thresholds['good']:
                score = 0.75
                thoroughness_result['strengths'].append(f"Good {dimension}")
            elif indicator_matches >= thresholds['adequate']:
                score = 0.5
            else:
                score = 0.25
                thoroughness_result['weaknesses'].append(f"Limited {dimension}")
            
            dimension_scores[dimension] = score
        
        # Calculate weighted overall score
        weighted_sum = sum(score * self.thoroughness_metrics[dim]['weight'] 
                          for dim, score in dimension_scores.items())
        total_weight = sum(config['weight'] for config in self.thoroughness_metrics.values())
        
        thoroughness_result['score'] = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        thoroughness_result['details'] = {
            'dimension_scores': dimension_scores,
            'indicator_counts': {dim: sum(1 for indicator in config['indicators'] 
                                        if indicator in content_lower)
                               for dim, config in self.thoroughness_metrics.items()}
        }
        
        return thoroughness_result
    
    def _extract_content(self, research_result: Any) -> str:
        """Extract content from research result for analysis"""
        content_parts = []
        
        # Extract from various fields
        if hasattr(research_result, 'synthesized_summary'):
            content_parts.append(research_result.synthesized_summary)
        
        if hasattr(research_result, 'key_insights'):
            content_parts.extend(research_result.key_insights)
        
        if hasattr(research_result, 'recommendations'):
            content_parts.extend(research_result.recommendations)
        
        if hasattr(research_result, 'sources'):
            for source in research_result.sources:
                if hasattr(source, 'content'):
                    content_parts.append(source.content)
                if hasattr(source, 'title'):
                    content_parts.append(source.title)
        
        if hasattr(research_result, 'ai_analyses'):
            for analysis in research_result.ai_analyses:
                if hasattr(analysis, 'summary'):
                    content_parts.append(analysis.summary)
                if hasattr(analysis, 'key_findings'):
                    content_parts.extend(analysis.key_findings)
                if hasattr(analysis, 'recommendations'):
                    content_parts.extend(analysis.recommendations)
        
        return ' '.join(content_parts)
    
    def _generate_completeness_recommendations(self, assessment: Dict[str, Any]) -> List[str]:
        """Generate recommendations for improving completeness"""
        recommendations = []
        
        overall_score = assessment['overall_score']
        coverage_score = assessment['coverage_score']
        thoroughness_score = assessment['thoroughness_score']
        
        # Overall recommendations
        if overall_score < 0.6:
            recommendations.append("Research completeness is below acceptable threshold, significant improvement needed")
        elif overall_score < 0.75:
            recommendations.append("Research completeness is adequate but could be improved")
        
        # Coverage recommendations
        if coverage_score < 0.6:
            recommendations.append("Research coverage is insufficient, expand into missing areas")
            if assessment['missing_areas']:
                recommendations.append(f"Focus on missing areas: {', '.join(assessment['missing_areas'][:3])}")
        
        # Thoroughness recommendations
        if thoroughness_score < 0.6:
            recommendations.append("Research depth is insufficient, provide more detailed analysis")
        
        # Specific recommendations based on weaknesses
        weaknesses = assessment.get('weaknesses', [])
        if len(weaknesses) > 3:
            recommendations.append("Multiple research gaps identified, consider comprehensive review")
        
        # Positive recommendations
        if overall_score >= 0.9:
            recommendations.append("Research completeness is excellent, comprehensive coverage achieved")
        elif overall_score >= 0.75:
            recommendations.append("Research completeness is good, minor improvements could be made")
        
        return recommendations
    
    def assess_source_diversity(self, sources: List[Any]) -> Dict[str, Any]:
        """Assess diversity of research sources"""
        if not sources:
            return {
                'diversity_score': 0.0,
                'domain_distribution': {},
                'source_types': {},
                'recommendations': ['No sources available for diversity assessment']
            }
        
        # Analyze domain distribution
        domains = []
        for source in sources:
            if hasattr(source, 'domain') and source.domain:
                domains.append(source.domain)
        
        domain_counter = Counter(domains)
        unique_domains = len(domain_counter)
        total_sources = len(sources)
        
        # Calculate diversity score
        if total_sources == 0:
            diversity_score = 0.0
        else:
            # Higher score for more unique domains relative to total sources
            diversity_score = min(1.0, unique_domains / max(1, total_sources / 2))
        
        # Analyze source types
        source_types = {}
        for source in sources:
            if hasattr(source, 'domain'):
                domain = source.domain
                if '.edu' in domain:
                    source_types['academic'] = source_types.get('academic', 0) + 1
                elif '.gov' in domain:
                    source_types['government'] = source_types.get('government', 0) + 1
                elif '.org' in domain:
                    source_types['organization'] = source_types.get('organization', 0) + 1
                else:
                    source_types['commercial'] = source_types.get('commercial', 0) + 1
        
        # Generate recommendations
        recommendations = []
        if diversity_score < 0.5:
            recommendations.append("Low source diversity, consider sources from different domains")
        
        if unique_domains < 3:
            recommendations.append("Limited domain coverage, expand to more authoritative sources")
        
        if not any(stype in source_types for stype in ['academic', 'government']):
            recommendations.append("Consider adding academic or government sources for higher credibility")
        
        return {
            'diversity_score': diversity_score,
            'domain_distribution': dict(domain_counter),
            'source_types': source_types,
            'unique_domains': unique_domains,
            'total_sources': total_sources,
            'recommendations': recommendations
        }
