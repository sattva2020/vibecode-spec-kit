"""
Methodology research template for process and approach analysis
"""

from typing import Dict, List, Any
from .research_template import ResearchTemplate, ResearchType


class MethodologyTemplate(ResearchTemplate):
    """Specialized template for methodology research"""
    
    def __init__(self):
        super().__init__(ResearchType.METHODOLOGY)
        self.methodology_fields = self._get_methodology_fields()
        self.evaluation_framework = self._get_evaluation_framework()
    
    def _get_methodology_fields(self) -> List[str]:
        """Get methodology-specific fields"""
        return [
            'methodology_overview',
            'process_steps',
            'best_practices',
            'common_pitfalls',
            'success_metrics',
            'implementation_guidelines',
            'tool_recommendations',
            'team_requirements',
            'time_estimates',
            'resource_requirements',
            'quality_assurance',
            'continuous_improvement',
            'scalability_considerations',
            'risk_mitigation'
        ]
    
    def _get_evaluation_framework(self) -> Dict[str, Dict[str, Any]]:
        """Get evaluation framework for methodology assessment"""
        return {
            'effectiveness': {
                'weight': 0.30,
                'criteria': ['success_rate', 'quality_improvement', 'efficiency_gains'],
                'scale': 'percentage'
            },
            'adoption': {
                'weight': 0.25,
                'criteria': ['learning_curve', 'team_acceptance', 'implementation_ease'],
                'scale': 'qualitative'
            },
            'sustainability': {
                'weight': 0.20,
                'criteria': ['maintenance_effort', 'continuous_improvement', 'long_term_viability'],
                'scale': 'qualitative'
            },
            'flexibility': {
                'weight': 0.15,
                'criteria': ['adaptability', 'customization_options', 'scalability'],
                'scale': 'qualitative'
            },
            'cost_benefit': {
                'weight': 0.10,
                'criteria': ['implementation_cost', 'roi', 'resource_efficiency'],
                'scale': 'monetary'
            }
        }
    
    def generate_methodology_analysis(self, methodology_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive methodology analysis"""
        analysis = {
            'methodology_name': methodology_data.get('name', 'Unknown'),
            'overall_rating': self._calculate_overall_rating(methodology_data),
            'dimension_scores': self._calculate_dimension_scores(methodology_data),
            'strengths': self._identify_methodology_strengths(methodology_data),
            'weaknesses': self._identify_methodology_weaknesses(methodology_data),
            'applicability': self._assess_applicability(methodology_data),
            'implementation_roadmap': self._create_implementation_roadmap(methodology_data),
            'success_factors': self._identify_success_factors(methodology_data)
        }
        
        return analysis
    
    def _calculate_overall_rating(self, methodology_data: Dict[str, Any]) -> float:
        """Calculate overall methodology rating"""
        total_rating = 0.0
        total_weight = 0.0
        
        for dimension, framework in self.evaluation_framework.items():
            dimension_score = self._calculate_dimension_score(methodology_data, dimension, framework)
            total_rating += dimension_score * framework['weight']
            total_weight += framework['weight']
        
        return total_rating / total_weight if total_weight > 0 else 0.0
    
    def _calculate_dimension_score(self, methodology_data: Dict[str, Any], dimension: str, framework: Dict[str, Any]) -> float:
        """Calculate score for a specific dimension"""
        criteria = framework['criteria']
        scores = []
        
        for criterion in criteria:
            criterion_key = f"{dimension}_{criterion}"
            if criterion_key in methodology_data:
                score = methodology_data[criterion_key]
                if isinstance(score, (int, float)):
                    scores.append(score)
                elif isinstance(score, str):
                    # Convert qualitative scores to numeric
                    qualitative_map = {
                        'excellent': 5, 'very_good': 4, 'good': 3, 'fair': 2, 'poor': 1
                    }
                    scores.append(qualitative_map.get(score.lower(), 3))
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _calculate_dimension_scores(self, methodology_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate scores for all dimensions"""
        dimension_scores = {}
        
        for dimension, framework in self.evaluation_framework.items():
            dimension_scores[dimension] = self._calculate_dimension_score(methodology_data, dimension, framework)
        
        return dimension_scores
    
    def _identify_methodology_strengths(self, methodology_data: Dict[str, Any]) -> List[str]:
        """Identify methodology strengths"""
        strengths = []
        dimension_scores = self._calculate_dimension_scores(methodology_data)
        
        for dimension, score in dimension_scores.items():
            if score >= 4.0:
                strengths.append(f"Strong {dimension} performance")
        
        # Add specific strengths based on data
        if methodology_data.get('effectiveness_success_rate', 0) >= 80:
            strengths.append("High success rate")
        if methodology_data.get('adoption_learning_curve', 'easy') in ['easy', 'moderate']:
            strengths.append("Easy to learn and adopt")
        if methodology_data.get('sustainability_maintenance_effort', 'low') == 'low':
            strengths.append("Low maintenance overhead")
        if methodology_data.get('flexibility_adaptability', 'high') in ['high', 'very_high']:
            strengths.append("Highly adaptable")
        
        return strengths
    
    def _identify_methodology_weaknesses(self, methodology_data: Dict[str, Any]) -> List[str]:
        """Identify methodology weaknesses"""
        weaknesses = []
        dimension_scores = self._calculate_dimension_scores(methodology_data)
        
        for dimension, score in dimension_scores.items():
            if score <= 2.0:
                weaknesses.append(f"Limited {dimension} capabilities")
        
        # Add specific weaknesses based on data
        if methodology_data.get('effectiveness_success_rate', 0) <= 50:
            weaknesses.append("Low success rate")
        if methodology_data.get('adoption_learning_curve', 'easy') == 'difficult':
            weaknesses.append("Steep learning curve")
        if methodology_data.get('sustainability_maintenance_effort', 'low') == 'high':
            weaknesses.append("High maintenance requirements")
        if methodology_data.get('flexibility_adaptability', 'high') == 'low':
            weaknesses.append("Limited flexibility")
        
        return weaknesses
    
    def _assess_applicability(self, methodology_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess methodology applicability for different contexts"""
        applicability = {
            'contexts': {
                'small_teams': self._assess_small_team_applicability(methodology_data),
                'large_teams': self._assess_large_team_applicability(methodology_data),
                'startups': self._assess_startup_applicability(methodology_data),
                'enterprise': self._assess_enterprise_applicability(methodology_data)
            },
            'recommended_contexts': [],
            'not_recommended_contexts': []
        }
        
        # Determine recommended contexts
        for context, score in applicability['contexts'].items():
            if score >= 4.0:
                applicability['recommended_contexts'].append(context)
            elif score <= 2.0:
                applicability['not_recommended_contexts'].append(context)
        
        return applicability
    
    def _assess_small_team_applicability(self, methodology_data: Dict[str, Any]) -> float:
        """Assess applicability for small teams"""
        factors = {
            'team_requirements': 5 - methodology_data.get('team_requirements', 3),  # Inverted
            'resource_requirements': 5 - methodology_data.get('resource_requirements', 3),  # Inverted
            'learning_curve': 5 - methodology_data.get('adoption_learning_curve', 3),  # Inverted
            'flexibility': methodology_data.get('flexibility_adaptability', 3)
        }
        
        return sum(factors.values()) / len(factors)
    
    def _assess_large_team_applicability(self, methodology_data: Dict[str, Any]) -> float:
        """Assess applicability for large teams"""
        factors = {
            'scalability': methodology_data.get('scalability_considerations', 3),
            'structure': methodology_data.get('process_steps', 3),
            'governance': methodology_data.get('quality_assurance', 3),
            'coordination': methodology_data.get('implementation_guidelines', 3)
        }
        
        return sum(factors.values()) / len(factors)
    
    def _assess_startup_applicability(self, methodology_data: Dict[str, Any]) -> float:
        """Assess applicability for startups"""
        factors = {
            'speed': methodology_data.get('time_estimates', 3),
            'cost': 5 - methodology_data.get('cost_benefit_implementation_cost', 3),  # Inverted
            'flexibility': methodology_data.get('flexibility_adaptability', 3),
            'learning_curve': 5 - methodology_data.get('adoption_learning_curve', 3)  # Inverted
        }
        
        return sum(factors.values()) / len(factors)
    
    def _assess_enterprise_applicability(self, methodology_data: Dict[str, Any]) -> float:
        """Assess applicability for enterprise"""
        factors = {
            'governance': methodology_data.get('quality_assurance', 3),
            'scalability': methodology_data.get('scalability_considerations', 3),
            'documentation': methodology_data.get('implementation_guidelines', 3),
            'risk_mitigation': methodology_data.get('risk_mitigation', 3)
        }
        
        return sum(factors.values()) / len(factors)
    
    def _create_implementation_roadmap(self, methodology_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create implementation roadmap"""
        roadmap = {
            'phases': [],
            'timeline': methodology_data.get('time_estimates', 'Unknown'),
            'resources': methodology_data.get('resource_requirements', 'Unknown'),
            'success_metrics': methodology_data.get('success_metrics', []),
            'milestones': []
        }
        
        # Generate phases based on methodology data
        process_steps = methodology_data.get('process_steps', [])
        if process_steps:
            for i, step in enumerate(process_steps, 1):
                roadmap['phases'].append({
                    'phase': i,
                    'name': step,
                    'duration': f"1-2 weeks",
                    'deliverables': [f"Completed {step}"],
                    'success_criteria': [f"Successfully implemented {step}"]
                })
        
        # Generate milestones
        if roadmap['phases']:
            roadmap['milestones'] = [
                "Initial setup and team training",
                "Pilot implementation",
                "Full rollout",
                "Continuous improvement"
            ]
        
        return roadmap
    
    def _identify_success_factors(self, methodology_data: Dict[str, Any]) -> List[str]:
        """Identify key success factors"""
        success_factors = []
        
        # Based on best practices
        best_practices = methodology_data.get('best_practices', [])
        if best_practices:
            success_factors.extend(best_practices[:3])  # Top 3 best practices
        
        # Based on common pitfalls (inverted)
        common_pitfalls = methodology_data.get('common_pitfalls', [])
        if common_pitfalls:
            success_factors.extend([
                f"Avoid: {pitfall}" for pitfall in common_pitfalls[:2]
            ])
        
        # Generic success factors based on methodology type
        if methodology_data.get('team_requirements', 0) > 3:
            success_factors.append("Ensure proper team composition and training")
        if methodology_data.get('resource_requirements', 0) > 3:
            success_factors.append("Secure adequate resources and budget")
        if methodology_data.get('quality_assurance', 0) > 3:
            success_factors.append("Implement robust quality assurance processes")
        
        return success_factors[:5]  # Limit to top 5 factors
