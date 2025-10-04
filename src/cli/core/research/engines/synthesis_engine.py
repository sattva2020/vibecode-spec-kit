"""
Synthesis engine for combining and analyzing research results
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import Counter, defaultdict

from ..templates.research_template import AIAnalysis, ResearchType, Source


class SynthesisEngine:
    """Engine for synthesizing research results from multiple sources"""
    
    def __init__(self):
        self.synthesis_strategies = self._initialize_synthesis_strategies()
        self.conflict_resolution_methods = self._initialize_conflict_resolution()
        self.quality_metrics = self._initialize_quality_metrics()
    
    def _initialize_synthesis_strategies(self) -> Dict[ResearchType, Dict[str, Any]]:
        """Initialize synthesis strategies for different research types"""
        return {
            ResearchType.TECHNICAL: {
                'approach': 'technical_consensus',
                'focus_areas': [
                    'implementation_approaches',
                    'performance_characteristics', 
                    'security_considerations',
                    'integration_requirements',
                    'best_practices'
                ],
                'consolidation_method': 'merge_technical_details',
                'priority_weighting': {
                    'github_copilot': 0.3,
                    'claude_code': 0.25,
                    'gemini_cli': 0.2,
                    'cursor': 0.25
                }
            },
            ResearchType.METHODOLOGY: {
                'approach': 'methodological_consensus',
                'focus_areas': [
                    'process_steps',
                    'best_practices',
                    'success_factors',
                    'common_pitfalls',
                    'implementation_guidelines'
                ],
                'consolidation_method': 'merge_methodological_insights',
                'priority_weighting': {
                    'claude_code': 0.35,
                    'gemini_cli': 0.3,
                    'cursor': 0.2,
                    'github_copilot': 0.15
                }
            },
            ResearchType.COMPETITIVE: {
                'approach': 'market_consensus',
                'focus_areas': [
                    'market_landscape',
                    'competitive_positioning',
                    'key_differentiators',
                    'market_trends',
                    'strategic_recommendations'
                ],
                'consolidation_method': 'merge_competitive_intelligence',
                'priority_weighting': {
                    'gemini_cli': 0.4,
                    'claude_code': 0.3,
                    'cursor': 0.2,
                    'github_copilot': 0.1
                }
            }
        }
    
    def _initialize_conflict_resolution(self) -> Dict[str, Dict[str, Any]]:
        """Initialize conflict resolution methods"""
        return {
            'consensus_based': {
                'description': 'Use majority consensus when conflicts arise',
                'threshold': 0.6,  # 60% agreement required
                'fallback': 'expert_weighted'
            },
            'expert_weighted': {
                'description': 'Weight opinions based on agent expertise',
                'agent_weights': {
                    'github_copilot': {'technical': 0.9, 'methodology': 0.6, 'competitive': 0.4},
                    'claude_code': {'technical': 0.8, 'methodology': 0.9, 'competitive': 0.7},
                    'gemini_cli': {'technical': 0.7, 'methodology': 0.8, 'competitive': 0.9},
                    'cursor': {'technical': 0.8, 'methodology': 0.7, 'competitive': 0.6}
                }
            },
            'confidence_weighted': {
                'description': 'Weight opinions based on confidence scores',
                'min_confidence': 0.6,
                'confidence_multiplier': 1.5
            },
            'source_backed': {
                'description': 'Prefer opinions backed by multiple sources',
                'source_threshold': 2,
                'source_multiplier': 1.2
            }
        }
    
    def _initialize_quality_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Initialize quality assessment metrics"""
        return {
            'completeness': {
                'weight': 0.3,
                'factors': ['coverage_breadth', 'detail_depth', 'missing_areas'],
                'thresholds': {'good': 0.8, 'acceptable': 0.6, 'poor': 0.4}
            },
            'consistency': {
                'weight': 0.25,
                'factors': ['internal_consistency', 'cross_source_agreement', 'contradiction_resolution'],
                'thresholds': {'good': 0.85, 'acceptable': 0.7, 'poor': 0.5}
            },
            'credibility': {
                'weight': 0.25,
                'factors': ['source_quality', 'expert_consensus', 'evidence_strength'],
                'thresholds': {'good': 0.8, 'acceptable': 0.6, 'poor': 0.4}
            },
            'actionability': {
                'weight': 0.2,
                'factors': ['practical_recommendations', 'implementation_guidance', 'clear_next_steps'],
                'thresholds': {'good': 0.8, 'acceptable': 0.6, 'poor': 0.4}
            }
        }
    
    def synthesize_research(self, 
                           analyses: List[AIAnalysis],
                           sources: List[Source],
                           research_type: ResearchType) -> Dict[str, Any]:
        """
        Synthesize research from multiple AI analyses and sources
        
        Args:
            analyses: List of AI analyses to synthesize
            sources: List of sources used in research
            research_type: Type of research being conducted
        
        Returns:
            Synthesized research results
        """
        if not analyses:
            return self._create_empty_synthesis()
        
        # Get synthesis strategy
        strategy = self.synthesis_strategies.get(research_type, self.synthesis_strategies[ResearchType.TECHNICAL])
        
        # Extract and process findings
        findings_data = self._extract_findings_data(analyses)
        
        # Consolidate findings by focus area
        consolidated_findings = self._consolidate_findings(findings_data, strategy)
        
        # Resolve conflicts
        resolved_findings = self._resolve_conflicts(consolidated_findings, analyses, research_type)
        
        # Generate insights
        insights = self._generate_insights(resolved_findings, research_type)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(analyses, sources, research_type)
        
        # Assess synthesis quality
        quality_assessment = self._assess_synthesis_quality(analyses, sources, resolved_findings)
        
        # Create executive summary
        executive_summary = self._create_executive_summary(
            research_type, insights, recommendations, quality_assessment
        )
        
        return {
            'executive_summary': executive_summary,
            'insights': insights,
            'recommendations': recommendations,
            'findings': resolved_findings,
            'quality_assessment': quality_assessment,
            'synthesis_metadata': {
                'research_type': research_type.value,
                'analysis_count': len(analyses),
                'source_count': len(sources),
                'synthesis_strategy': strategy['approach'],
                'synthesis_timestamp': datetime.now().isoformat()
            }
        }
    
    def _extract_findings_data(self, analyses: List[AIAnalysis]) -> Dict[str, List[Any]]:
        """Extract and categorize findings from analyses"""
        findings_data = {
            'summaries': [],
            'key_findings': [],
            'recommendations': [],
            'confidence_scores': [],
            'agent_contributions': {}
        }
        
        for analysis in analyses:
            findings_data['summaries'].append(analysis.summary)
            findings_data['key_findings'].extend(analysis.key_findings)
            findings_data['recommendations'].extend(analysis.recommendations)
            findings_data['confidence_scores'].append(analysis.confidence_score)
            findings_data['agent_contributions'][analysis.agent_name] = {
                'findings_count': len(analysis.key_findings),
                'recommendations_count': len(analysis.recommendations),
                'confidence': analysis.confidence_score,
                'metadata': analysis.metadata
            }
        
        return findings_data
    
    def _consolidate_findings(self, 
                             findings_data: Dict[str, List[Any]], 
                             strategy: Dict[str, Any]) -> Dict[str, List[str]]:
        """Consolidate findings by focus areas"""
        consolidated = {area: [] for area in strategy['focus_areas']}
        
        # Categorize findings by focus area
        for finding in findings_data['key_findings']:
            finding_lower = finding.lower()
            
            for area in strategy['focus_areas']:
                area_keywords = self._get_area_keywords(area)
                
                if any(keyword in finding_lower for keyword in area_keywords):
                    consolidated[area].append(finding)
        
        # Handle uncategorized findings
        all_categorized = set()
        for area_findings in consolidated.values():
            all_categorized.update(area_findings)
        
        uncategorized = [f for f in findings_data['key_findings'] if f not in all_categorized]
        if uncategorized:
            consolidated['general_insights'] = uncategorized
        
        return consolidated
    
    def _get_area_keywords(self, area: str) -> List[str]:
        """Get keywords for identifying focus areas"""
        keyword_map = {
            'implementation_approaches': ['implementation', 'approach', 'method', 'technique', 'strategy'],
            'performance_characteristics': ['performance', 'speed', 'efficiency', 'optimization', 'scalability'],
            'security_considerations': ['security', 'vulnerability', 'protection', 'authentication', 'authorization'],
            'integration_requirements': ['integration', 'api', 'interface', 'connection', 'compatibility'],
            'best_practices': ['best practice', 'recommendation', 'guideline', 'standard', 'pattern'],
            'process_steps': ['process', 'step', 'phase', 'stage', 'workflow'],
            'success_factors': ['success', 'factor', 'key', 'critical', 'important'],
            'common_pitfalls': ['pitfall', 'mistake', 'error', 'problem', 'issue'],
            'implementation_guidelines': ['guideline', 'instruction', 'procedure', 'protocol'],
            'market_landscape': ['market', 'industry', 'landscape', 'ecosystem', 'environment'],
            'competitive_positioning': ['competitor', 'positioning', 'differentiation', 'advantage'],
            'key_differentiators': ['differentiator', 'unique', 'distinctive', 'special', 'advantage'],
            'market_trends': ['trend', 'direction', 'evolution', 'change', 'future'],
            'strategic_recommendations': ['strategic', 'recommendation', 'suggestion', 'advice']
        }
        
        return keyword_map.get(area, [area.replace('_', ' ')])
    
    def _resolve_conflicts(self, 
                          consolidated_findings: Dict[str, List[str]],
                          analyses: List[AIAnalysis],
                          research_type: ResearchType) -> Dict[str, List[str]]:
        """Resolve conflicts in consolidated findings"""
        resolved = {}
        
        for area, findings in consolidated_findings.items():
            if not findings:
                resolved[area] = []
                continue
            
            # Find conflicting findings
            conflicts = self._identify_conflicts(findings)
            
            if not conflicts:
                resolved[area] = findings
                continue
            
            # Resolve conflicts using consensus-based approach
            resolved_findings = self._resolve_area_conflicts(
                findings, conflicts, analyses, research_type
            )
            
            resolved[area] = resolved_findings
        
        return resolved
    
    def _identify_conflicts(self, findings: List[str]) -> List[tuple]:
        """Identify potentially conflicting findings"""
        conflicts = []
        
        # Simple conflict detection based on keyword analysis
        negative_keywords = ['not', 'avoid', 'don\'t', 'shouldn\'t', 'never', 'impossible', 'unable']
        positive_keywords = ['should', 'recommend', 'best', 'good', 'effective', 'successful']
        
        for i, finding1 in enumerate(findings):
            for j, finding2 in enumerate(findings[i+1:], i+1):
                finding1_lower = finding1.lower()
                finding2_lower = finding2.lower()
                
                # Check for direct contradictions
                has_negative1 = any(neg in finding1_lower for neg in negative_keywords)
                has_negative2 = any(neg in finding2_lower for neg in negative_keywords)
                has_positive1 = any(pos in finding1_lower for pos in positive_keywords)
                has_positive2 = any(pos in finding2_lower for pos in positive_keywords)
                
                if (has_negative1 and has_positive2) or (has_positive1 and has_negative2):
                    conflicts.append((i, j))
        
        return conflicts
    
    def _resolve_area_conflicts(self, 
                               findings: List[str],
                               conflicts: List[tuple],
                               analyses: List[AIAnalysis],
                               research_type: ResearchType) -> List[str]:
        """Resolve conflicts in a specific area"""
        if not conflicts:
            return findings
        
        resolved = []
        conflicted_indices = set()
        
        for conflict in conflicts:
            i, j = conflict
            conflicted_indices.add(i)
            conflicted_indices.add(j)
            
            # Use consensus-based resolution
            resolution = self._consensus_resolve_conflict(
                findings[i], findings[j], analyses, research_type
            )
            
            resolved.append(resolution)
        
        # Add non-conflicting findings
        for i, finding in enumerate(findings):
            if i not in conflicted_indices:
                resolved.append(finding)
        
        return resolved
    
    def _consensus_resolve_conflict(self, 
                                   finding1: str,
                                   finding2: str,
                                   analyses: List[AIAnalysis],
                                   research_type: ResearchType) -> str:
        """Resolve conflict using consensus approach"""
        
        # Count supporting analyses for each finding
        support1 = 0
        support2 = 0
        
        for analysis in analyses:
            findings_lower = [f.lower() for f in analysis.key_findings]
            
            if any(word in finding1.lower() for word in findings_lower):
                support1 += analysis.confidence_score
            
            if any(word in finding2.lower() for word in findings_lower):
                support2 += analysis.confidence_score
        
        # Choose finding with higher support
        if support1 > support2:
            return finding1
        elif support2 > support1:
            return finding2
        else:
            # Equal support - combine findings
            return f"{finding1} However, {finding2.lower()}"
    
    def _generate_insights(self, 
                          resolved_findings: Dict[str, List[str]],
                          research_type: ResearchType) -> List[str]:
        """Generate high-level insights from resolved findings"""
        insights = []
        
        # Count findings by area
        area_counts = {area: len(findings) for area, findings in resolved_findings.items()}
        
        # Generate insights based on most covered areas
        top_areas = sorted(area_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        for area, count in top_areas:
            if count > 0:
                area_insights = resolved_findings[area][:2]  # Top 2 findings per area
                insights.extend(area_insights)
        
        # Add general insights if available
        if 'general_insights' in resolved_findings:
            insights.extend(resolved_findings['general_insights'][:2])
        
        return insights[:5]  # Limit to top 5 insights
    
    def _generate_recommendations(self, 
                                analyses: List[AIAnalysis],
                                sources: List[Source],
                                research_type: ResearchType) -> List[str]:
        """Generate actionable recommendations"""
        all_recommendations = []
        
        # Collect recommendations from analyses
        for analysis in analyses:
            all_recommendations.extend(analysis.recommendations)
        
        # Remove duplicates and rank by frequency
        recommendation_counts = Counter(all_recommendations)
        
        # Sort by frequency and confidence
        ranked_recommendations = []
        for rec, count in recommendation_counts.most_common():
            # Find average confidence for this recommendation
            confidences = []
            for analysis in analyses:
                if rec in analysis.recommendations:
                    confidences.append(analysis.confidence_score)
            
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5
            
            # Weight by frequency and confidence
            score = count * avg_confidence
            ranked_recommendations.append((rec, score))
        
        # Sort by weighted score
        ranked_recommendations.sort(key=lambda x: x[1], reverse=True)
        
        return [rec for rec, score in ranked_recommendations[:5]]
    
    def _assess_synthesis_quality(self, 
                                 analyses: List[AIAnalysis],
                                 sources: List[Source],
                                 resolved_findings: Dict[str, List[str]]) -> Dict[str, Any]:
        """Assess the quality of the synthesis"""
        quality_scores = {}
        
        # Completeness assessment
        total_findings = sum(len(findings) for findings in resolved_findings.values())
        completeness_score = min(1.0, total_findings / 15)  # Expect ~15 findings
        quality_scores['completeness'] = completeness_score
        
        # Consistency assessment
        avg_confidence = sum(analysis.confidence_score for analysis in analyses) / len(analyses)
        quality_scores['consistency'] = avg_confidence
        
        # Credibility assessment
        if sources:
            avg_source_credibility = sum(source.credibility_score for source in sources) / len(sources)
            quality_scores['credibility'] = avg_source_credibility
        else:
            quality_scores['credibility'] = 0.5
        
        # Actionability assessment (based on recommendation quality)
        recommendation_count = sum(len(analysis.recommendations) for analysis in analyses)
        actionability_score = min(1.0, recommendation_count / 10)  # Expect ~10 recommendations
        quality_scores['actionability'] = actionability_score
        
        # Calculate overall quality
        weights = self.quality_metrics
        overall_score = (
            quality_scores['completeness'] * weights['completeness']['weight'] +
            quality_scores['consistency'] * weights['consistency']['weight'] +
            quality_scores['credibility'] * weights['credibility']['weight'] +
            quality_scores['actionability'] * weights['actionability']['weight']
        )
        
        return {
            'overall_score': overall_score,
            'dimension_scores': quality_scores,
            'quality_level': self._determine_quality_level(overall_score),
            'assessment_metadata': {
                'analysis_count': len(analyses),
                'source_count': len(sources),
                'finding_count': total_findings,
                'assessment_timestamp': datetime.now().isoformat()
            }
        }
    
    def _determine_quality_level(self, overall_score: float) -> str:
        """Determine quality level based on overall score"""
        if overall_score >= 0.8:
            return 'high'
        elif overall_score >= 0.6:
            return 'medium'
        else:
            return 'low'
    
    def _create_executive_summary(self, 
                                 research_type: ResearchType,
                                 insights: List[str],
                                 recommendations: List[str],
                                 quality_assessment: Dict[str, Any]) -> str:
        """Create executive summary of the synthesis"""
        
        quality_level = quality_assessment['quality_level']
        overall_score = quality_assessment['overall_score']
        
        summary = f"""
        Executive Summary: {research_type.value.title()} Research Synthesis
        
        This comprehensive analysis synthesizes insights from multiple AI agents and sources 
        to provide a {quality_level}-quality assessment of the research topic.
        
        Overall Quality Score: {overall_score:.2f}/1.0
        
        Key Insights:
        {chr(10).join(f"• {insight}" for insight in insights[:3])}
        
        Top Recommendations:
        {chr(10).join(f"• {rec}" for rec in recommendations[:3])}
        
        The synthesis provides actionable guidance based on consensus from multiple expert 
        analyses and validated sources.
        """.strip()
        
        return summary
    
    def _create_empty_synthesis(self) -> Dict[str, Any]:
        """Create empty synthesis when no analyses are available"""
        return {
            'executive_summary': 'No analyses available for synthesis.',
            'insights': [],
            'recommendations': [],
            'findings': {},
            'quality_assessment': {
                'overall_score': 0.0,
                'dimension_scores': {
                    'completeness': 0.0,
                    'consistency': 0.0,
                    'credibility': 0.0,
                    'actionability': 0.0
                },
                'quality_level': 'low'
            },
            'synthesis_metadata': {
                'analysis_count': 0,
                'source_count': 0,
                'synthesis_timestamp': datetime.now().isoformat()
            }
        }
