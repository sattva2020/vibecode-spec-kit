"""
Technology research template for technical analysis and evaluation
"""

from typing import Dict, List, Any
from .research_template import ResearchTemplate, ResearchType


class TechResearchTemplate(ResearchTemplate):
    """Specialized template for technology research"""
    
    def __init__(self):
        super().__init__(ResearchType.TECHNICAL)
        self.technical_fields = self._get_technical_fields()
        self.evaluation_criteria = self._get_evaluation_criteria()
    
    def _get_technical_fields(self) -> List[str]:
        """Get technology-specific fields"""
        return [
            'technology_overview',
            'architecture_analysis',
            'performance_metrics',
            'security_analysis',
            'scalability_assessment',
            'integration_requirements',
            'deployment_considerations',
            'cost_analysis',
            'learning_curve',
            'community_support',
            'documentation_quality',
            'licensing_terms',
            'maintenance_overhead',
            'migration_complexity'
        ]
    
    def _get_evaluation_criteria(self) -> Dict[str, Dict[str, Any]]:
        """Get evaluation criteria for technology assessment"""
        return {
            'performance': {
                'weight': 0.25,
                'metrics': ['speed', 'memory_usage', 'throughput', 'latency'],
                'scale': 'numeric'
            },
            'security': {
                'weight': 0.20,
                'metrics': ['vulnerability_history', 'encryption_support', 'access_control', 'audit_capabilities'],
                'scale': 'qualitative'
            },
            'scalability': {
                'weight': 0.15,
                'metrics': ['horizontal_scaling', 'vertical_scaling', 'load_handling', 'resource_efficiency'],
                'scale': 'qualitative'
            },
            'ease_of_use': {
                'weight': 0.15,
                'metrics': ['learning_curve', 'documentation', 'community_support', 'tooling'],
                'scale': 'qualitative'
            },
            'integration': {
                'weight': 0.10,
                'metrics': ['api_quality', 'compatibility', 'deployment_options', 'migration_path'],
                'scale': 'qualitative'
            },
            'cost': {
                'weight': 0.10,
                'metrics': ['licensing_cost', 'infrastructure_cost', 'maintenance_cost', 'training_cost'],
                'scale': 'monetary'
            },
            'reliability': {
                'weight': 0.05,
                'metrics': ['uptime', 'error_handling', 'recovery_capabilities', 'testing_coverage'],
                'scale': 'qualitative'
            }
        }
    
    def generate_technology_assessment(self, tech_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive technology assessment"""
        assessment = {
            'technology_name': tech_data.get('name', 'Unknown'),
            'overall_score': self._calculate_overall_score(tech_data),
            'category_scores': self._calculate_category_scores(tech_data),
            'strengths': self._identify_strengths(tech_data),
            'weaknesses': self._identify_weaknesses(tech_data),
            'recommendations': self._generate_recommendations(tech_data),
            'risk_assessment': self._assess_risks(tech_data),
            'adoption_readiness': self._assess_adoption_readiness(tech_data)
        }
        
        return assessment
    
    def _calculate_overall_score(self, tech_data: Dict[str, Any]) -> float:
        """Calculate overall technology score"""
        total_score = 0.0
        total_weight = 0.0
        
        for category, criteria in self.evaluation_criteria.items():
            category_score = self._calculate_category_score(tech_data, category, criteria)
            total_score += category_score * criteria['weight']
            total_weight += criteria['weight']
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _calculate_category_score(self, tech_data: Dict[str, Any], category: str, criteria: Dict[str, Any]) -> float:
        """Calculate score for a specific category"""
        metrics = criteria['metrics']
        scores = []
        
        for metric in metrics:
            metric_key = f"{category}_{metric}"
            if metric_key in tech_data:
                score = tech_data[metric_key]
                if isinstance(score, (int, float)):
                    scores.append(score)
                elif isinstance(score, str):
                    # Convert qualitative scores to numeric
                    qualitative_map = {
                        'excellent': 5, 'very_good': 4, 'good': 3, 'fair': 2, 'poor': 1
                    }
                    scores.append(qualitative_map.get(score.lower(), 3))
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _calculate_category_scores(self, tech_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate scores for all categories"""
        category_scores = {}
        
        for category, criteria in self.evaluation_criteria.items():
            category_scores[category] = self._calculate_category_score(tech_data, category, criteria)
        
        return category_scores
    
    def _identify_strengths(self, tech_data: Dict[str, Any]) -> List[str]:
        """Identify technology strengths"""
        strengths = []
        category_scores = self._calculate_category_scores(tech_data)
        
        for category, score in category_scores.items():
            if score >= 4.0:
                strengths.append(f"Strong {category} capabilities")
        
        # Add specific strengths based on data
        if tech_data.get('performance_speed', 0) >= 4:
            strengths.append("High performance")
        if tech_data.get('security_vulnerability_history', 'low') == 'low':
            strengths.append("Good security track record")
        if tech_data.get('ease_of_use_learning_curve', 'easy') in ['easy', 'moderate']:
            strengths.append("Easy to learn and use")
        if tech_data.get('integration_api_quality', 'good') in ['excellent', 'very_good']:
            strengths.append("Well-designed APIs")
        
        return strengths
    
    def _identify_weaknesses(self, tech_data: Dict[str, Any]) -> List[str]:
        """Identify technology weaknesses"""
        weaknesses = []
        category_scores = self._calculate_category_scores(tech_data)
        
        for category, score in category_scores.items():
            if score <= 2.0:
                weaknesses.append(f"Limited {category} capabilities")
        
        # Add specific weaknesses based on data
        if tech_data.get('performance_speed', 0) <= 2:
            weaknesses.append("Performance concerns")
        if tech_data.get('security_vulnerability_history', 'low') == 'high':
            weaknesses.append("Security vulnerabilities")
        if tech_data.get('ease_of_use_learning_curve', 'easy') == 'difficult':
            weaknesses.append("Steep learning curve")
        if tech_data.get('cost_licensing_cost', 'low') == 'high':
            weaknesses.append("High licensing costs")
        
        return weaknesses
    
    def _generate_recommendations(self, tech_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on assessment"""
        recommendations = []
        overall_score = self._calculate_overall_score(tech_data)
        
        if overall_score >= 4.0:
            recommendations.append("Strong candidate for adoption")
            recommendations.append("Consider pilot implementation")
        elif overall_score >= 3.0:
            recommendations.append("Suitable with proper planning")
            recommendations.append("Address identified weaknesses")
        else:
            recommendations.append("Not recommended for current needs")
            recommendations.append("Consider alternatives")
        
        # Specific recommendations based on weaknesses
        weaknesses = self._identify_weaknesses(tech_data)
        if "Performance concerns" in weaknesses:
            recommendations.append("Implement performance monitoring")
        if "Security vulnerabilities" in weaknesses:
            recommendations.append("Develop security mitigation plan")
        if "Steep learning curve" in weaknesses:
            recommendations.append("Plan comprehensive training program")
        
        return recommendations
    
    def _assess_risks(self, tech_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess adoption risks"""
        risks = {
            'technical_risks': [],
            'business_risks': [],
            'operational_risks': [],
            'overall_risk_level': 'medium'
        }
        
        # Technical risks
        if tech_data.get('performance_speed', 0) <= 2:
            risks['technical_risks'].append("Performance limitations may impact user experience")
        if tech_data.get('scalability_horizontal_scaling', 'limited') == 'limited':
            risks['technical_risks'].append("Limited horizontal scaling capabilities")
        
        # Business risks
        if tech_data.get('cost_licensing_cost', 'low') == 'high':
            risks['business_risks'].append("High licensing costs may impact budget")
        if tech_data.get('community_support', 'limited') == 'limited':
            risks['business_risks'].append("Limited community support may slow development")
        
        # Operational risks
        if tech_data.get('ease_of_use_learning_curve', 'easy') == 'difficult':
            risks['operational_risks'].append("Training requirements may impact timeline")
        if tech_data.get('maintenance_overhead', 'high') == 'high':
            risks['operational_risks'].append("High maintenance requirements")
        
        # Calculate overall risk level
        total_risks = len(risks['technical_risks']) + len(risks['business_risks']) + len(risks['operational_risks'])
        if total_risks >= 4:
            risks['overall_risk_level'] = 'high'
        elif total_risks <= 1:
            risks['overall_risk_level'] = 'low'
        
        return risks
    
    def _assess_adoption_readiness(self, tech_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess readiness for technology adoption"""
        readiness = {
            'readiness_score': 0.0,
            'readiness_level': 'not_ready',
            'requirements': [],
            'timeline': 'unknown'
        }
        
        # Calculate readiness score
        factors = {
            'documentation_quality': tech_data.get('documentation_quality', 3),
            'community_support': tech_data.get('community_support', 3),
            'learning_curve': 5 - tech_data.get('ease_of_use_learning_curve', 3),  # Inverted
            'integration_complexity': 5 - tech_data.get('integration_deployment_options', 3),  # Inverted
            'migration_complexity': 5 - tech_data.get('migration_complexity', 3)  # Inverted
        }
        
        readiness['readiness_score'] = sum(factors.values()) / len(factors)
        
        # Determine readiness level
        if readiness['readiness_score'] >= 4.0:
            readiness['readiness_level'] = 'ready'
            readiness['timeline'] = '1-2 months'
        elif readiness['readiness_score'] >= 3.0:
            readiness['readiness_level'] = 'mostly_ready'
            readiness['timeline'] = '2-4 months'
        elif readiness['readiness_score'] >= 2.0:
            readiness['readiness_level'] = 'preparation_needed'
            readiness['timeline'] = '4-6 months'
        else:
            readiness['readiness_level'] = 'not_ready'
            readiness['timeline'] = '6+ months'
        
        # Generate requirements based on readiness
        if readiness['readiness_score'] < 4.0:
            readiness['requirements'].append("Improve documentation quality")
        if tech_data.get('community_support', 3) < 4:
            readiness['requirements'].append("Build internal expertise")
        if tech_data.get('ease_of_use_learning_curve', 3) > 3:
            readiness['requirements'].append("Develop training materials")
        
        return readiness
