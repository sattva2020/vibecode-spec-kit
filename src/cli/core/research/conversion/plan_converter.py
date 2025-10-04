"""
Plan converter for transforming research into implementation plans
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta


class PlanConverter:
    """Converter for transforming research results into implementation plans"""
    
    def __init__(self):
        self.planning_templates = self._initialize_planning_templates()
        self.phase_generators = self._initialize_phase_generators()
        self.timeline_estimators = self._initialize_timeline_estimators()
    
    def _initialize_planning_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize planning templates for different research types"""
        return {
            'technical': {
                'phases': ['Analysis', 'Design', 'Implementation', 'Testing', 'Deployment'],
                'default_duration': {'Analysis': 2, 'Design': 3, 'Implementation': 8, 'Testing': 3, 'Deployment': 2},
                'complexity_multipliers': {1: 0.5, 2: 1.0, 3: 1.5, 4: 2.0}
            },
            'methodology': {
                'phases': ['Assessment', 'Planning', 'Implementation', 'Training', 'Monitoring'],
                'default_duration': {'Assessment': 1, 'Planning': 2, 'Implementation': 4, 'Training': 2, 'Monitoring': 3},
                'complexity_multipliers': {1: 0.7, 2: 1.0, 3: 1.3, 4: 1.8}
            },
            'competitive': {
                'phases': ['Research', 'Analysis', 'Strategy Development', 'Implementation', 'Review'],
                'default_duration': {'Research': 2, 'Analysis': 3, 'Strategy Development': 4, 'Implementation': 6, 'Review': 2},
                'complexity_multipliers': {1: 0.8, 2: 1.0, 3: 1.4, 4: 1.9}
            }
        }
    
    def _initialize_phase_generators(self) -> Dict[str, Dict[str, Any]]:
        """Initialize phase generators for different types of plans"""
        return {
            'technical': {
                'Analysis': ['Requirements gathering', 'Technology assessment', 'Architecture review'],
                'Design': ['System design', 'API design', 'Database design', 'Security design'],
                'Implementation': ['Core development', 'Integration', 'Testing setup', 'Documentation'],
                'Testing': ['Unit testing', 'Integration testing', 'Performance testing', 'Security testing'],
                'Deployment': ['Environment setup', 'Deployment automation', 'Monitoring setup', 'Go-live']
            },
            'methodology': {
                'Assessment': ['Current state analysis', 'Gap identification', 'Stakeholder interviews'],
                'Planning': ['Methodology selection', 'Resource planning', 'Timeline development'],
                'Implementation': ['Process rollout', 'Tool configuration', 'Team training'],
                'Training': ['User training', 'Administrator training', 'Documentation creation'],
                'Monitoring': ['Performance tracking', 'Feedback collection', 'Continuous improvement']
            },
            'competitive': {
                'Research': ['Market analysis', 'Competitor identification', 'Feature comparison'],
                'Analysis': ['SWOT analysis', 'Market positioning', 'Gap analysis'],
                'Strategy Development': ['Competitive strategy', 'Differentiation plan', 'Go-to-market strategy'],
                'Implementation': ['Strategy execution', 'Marketing campaigns', 'Product development'],
                'Review': ['Performance analysis', 'Strategy adjustment', 'Market feedback']
            }
        }
    
    def _initialize_timeline_estimators(self) -> Dict[str, Dict[str, Any]]:
        """Initialize timeline estimation logic"""
        return {
            'complexity_factors': {
                'simple': {'duration_multiplier': 0.7, 'team_size': 2, 'risk_level': 'low'},
                'intermediate': {'duration_multiplier': 1.0, 'team_size': 4, 'risk_level': 'medium'},
                'complex': {'duration_multiplier': 1.5, 'team_size': 6, 'risk_level': 'high'}
            },
            'team_experience_factors': {
                'novice': {'efficiency': 0.6, 'learning_time': 1.2},
                'intermediate': {'efficiency': 1.0, 'learning_time': 1.0},
                'expert': {'efficiency': 1.3, 'learning_time': 0.8}
            },
            'resource_constraints': {
                'limited': {'duration_multiplier': 1.3, 'parallel_work': 0.7},
                'adequate': {'duration_multiplier': 1.0, 'parallel_work': 1.0},
                'abundant': {'duration_multiplier': 0.8, 'parallel_work': 1.3}
            }
        }
    
    def convert_to_plan(self, 
                       research_data: Dict[str, Any],
                       research_type: str = 'technical',
                       complexity_level: Optional[int] = None,
                       constraints: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Convert research data to implementation plan
        
        Args:
            research_data: Research data to convert
            research_type: Type of research (technical, methodology, competitive)
            complexity_level: Complexity level (1-4), auto-detected if None
            constraints: Project constraints (timeline, resources, team)
        
        Returns:
            Implementation plan data
        """
        # Auto-detect complexity if not provided
        if complexity_level is None:
            complexity_level = self._detect_complexity(research_data, research_type)
        
        # Get planning template
        template = self.planning_templates.get(research_type, self.planning_templates['technical'])
        
        # Generate plan phases
        phases = self._generate_phases(research_data, research_type, complexity_level, template)
        
        # Estimate timeline
        timeline = self._estimate_timeline(phases, complexity_level, constraints)
        
        # Generate resource requirements
        resources = self._estimate_resources(phases, complexity_level, constraints)
        
        # Generate risk assessment
        risks = self._assess_risks(research_data, complexity_level, constraints)
        
        # Create implementation plan
        plan = {
            'plan_metadata': {
                'created_at': datetime.now().isoformat(),
                'research_type': research_type,
                'complexity_level': complexity_level,
                'source_research': research_data.get('query', 'Unknown'),
                'plan_version': '1.0'
            },
            'phases': phases,
            'timeline': timeline,
            'resources': resources,
            'risks': risks,
            'success_metrics': self._generate_success_metrics(research_data, research_type),
            'monitoring_plan': self._generate_monitoring_plan(research_type, complexity_level)
        }
        
        return plan
    
    def _detect_complexity(self, research_data: Dict[str, Any], research_type: str) -> int:
        """Detect complexity level from research data"""
        # Similar to SpecConverter but focused on implementation complexity
        insights = research_data.get('key_insights', [])
        recommendations = research_data.get('recommendations', [])
        
        combined_text = ' '.join(insights + recommendations).lower()
        
        # Complexity indicators
        high_complexity_indicators = ['architecture', 'system', 'enterprise', 'scalable', 'complex']
        medium_complexity_indicators = ['integration', 'advanced', 'multiple', 'framework']
        
        if any(indicator in combined_text for indicator in high_complexity_indicators):
            return 4
        elif any(indicator in combined_text for indicator in medium_complexity_indicators):
            return 3
        else:
            return 2
    
    def _generate_phases(self, 
                        research_data: Dict[str, Any],
                        research_type: str,
                        complexity_level: int,
                        template: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate implementation phases"""
        phases = []
        phase_names = template['phases']
        default_durations = template['default_duration']
        complexity_multiplier = template['complexity_multipliers'][complexity_level]
        
        # Get phase generators
        generators = self.phase_generators.get(research_type, self.phase_generators['technical'])
        
        for phase_name in phase_names:
            # Calculate duration
            base_duration = default_durations.get(phase_name, 2)
            adjusted_duration = int(base_duration * complexity_multiplier)
            
            # Generate tasks
            tasks = self._generate_phase_tasks(phase_name, research_data, generators)
            
            # Create phase
            phase = {
                'name': phase_name,
                'description': f"{phase_name} phase for {research_type} implementation",
                'duration_weeks': adjusted_duration,
                'tasks': tasks,
                'deliverables': self._generate_phase_deliverables(phase_name, research_type),
                'dependencies': self._get_phase_dependencies(phase_name, phase_names),
                'success_criteria': self._generate_phase_success_criteria(phase_name, research_type)
            }
            
            phases.append(phase)
        
        return phases
    
    def _generate_phase_tasks(self, 
                             phase_name: str,
                             research_data: Dict[str, Any],
                             generators: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Generate tasks for a specific phase"""
        base_tasks = generators.get(phase_name, [])
        tasks = []
        
        for i, task_name in enumerate(base_tasks):
            # Enhance task with research insights
            enhanced_description = self._enhance_task_with_research(task_name, research_data)
            
            task = {
                'name': task_name,
                'description': enhanced_description,
                'estimated_hours': self._estimate_task_hours(task_name, phase_name),
                'priority': self._determine_task_priority(task_name, phase_name),
                'assignee_role': self._suggest_assignee_role(task_name, phase_name),
                'dependencies': []  # Could be enhanced with task dependencies
            }
            
            tasks.append(task)
        
        return tasks
    
    def _enhance_task_with_research(self, task_name: str, research_data: Dict[str, Any]) -> str:
        """Enhance task description with research insights"""
        base_description = task_name
        
        # Find relevant insights
        insights = research_data.get('key_insights', [])
        relevant_insights = []
        
        task_lower = task_name.lower()
        for insight in insights:
            # Simple keyword matching for relevance
            if any(word in insight.lower() for word in task_lower.split()):
                relevant_insights.append(insight)
        
        if relevant_insights:
            base_description += f"\n\nKey considerations: {'; '.join(relevant_insights[:2])}"
        
        return base_description
    
    def _estimate_task_hours(self, task_name: str, phase_name: str) -> int:
        """Estimate task duration in hours"""
        # Base estimates by phase and task type
        base_hours = {
            'Analysis': {'Requirements gathering': 16, 'Technology assessment': 12, 'Architecture review': 20},
            'Design': {'System design': 24, 'API design': 16, 'Database design': 20, 'Security design': 12},
            'Implementation': {'Core development': 40, 'Integration': 24, 'Testing setup': 16, 'Documentation': 12},
            'Testing': {'Unit testing': 20, 'Integration testing': 24, 'Performance testing': 16, 'Security testing': 12},
            'Deployment': {'Environment setup': 12, 'Deployment automation': 16, 'Monitoring setup': 8, 'Go-live': 8}
        }
        
        phase_tasks = base_hours.get(phase_name, {})
        return phase_tasks.get(task_name, 16)  # Default 16 hours
    
    def _determine_task_priority(self, task_name: str, phase_name: str) -> str:
        """Determine task priority"""
        high_priority_tasks = ['Requirements gathering', 'Core development', 'Go-live']
        medium_priority_tasks = ['System design', 'Integration', 'Testing setup']
        
        if task_name in high_priority_tasks:
            return 'high'
        elif task_name in medium_priority_tasks:
            return 'medium'
        else:
            return 'low'
    
    def _suggest_assignee_role(self, task_name: str, phase_name: str) -> str:
        """Suggest assignee role for task"""
        role_mapping = {
            'Requirements gathering': 'Business Analyst',
            'Technology assessment': 'Technical Architect',
            'Architecture review': 'Technical Architect',
            'System design': 'Solution Architect',
            'API design': 'Backend Developer',
            'Database design': 'Database Developer',
            'Security design': 'Security Engineer',
            'Core development': 'Developer',
            'Integration': 'Integration Developer',
            'Testing setup': 'QA Engineer',
            'Documentation': 'Technical Writer',
            'Unit testing': 'Developer',
            'Integration testing': 'QA Engineer',
            'Performance testing': 'Performance Engineer',
            'Security testing': 'Security Engineer',
            'Environment setup': 'DevOps Engineer',
            'Deployment automation': 'DevOps Engineer',
            'Monitoring setup': 'DevOps Engineer',
            'Go-live': 'Release Manager'
        }
        
        return role_mapping.get(task_name, 'Team Member')
    
    def _generate_phase_deliverables(self, phase_name: str, research_type: str) -> List[str]:
        """Generate deliverables for a phase"""
        deliverables_map = {
            'Analysis': ['Requirements document', 'Technical assessment report', 'Architecture review'],
            'Design': ['System design document', 'API specification', 'Database schema', 'Security plan'],
            'Implementation': ['Working software', 'Integration tests', 'Documentation', 'Deployment scripts'],
            'Testing': ['Test results', 'Performance report', 'Security assessment', 'User acceptance'],
            'Deployment': ['Production environment', 'Monitoring dashboard', 'Deployment guide', 'Go-live checklist']
        }
        
        return deliverables_map.get(phase_name, [f"{phase_name} deliverables"])
    
    def _get_phase_dependencies(self, phase_name: str, all_phases: List[str]) -> List[str]:
        """Get phase dependencies"""
        dependencies_map = {
            'Design': ['Analysis'],
            'Implementation': ['Design'],
            'Testing': ['Implementation'],
            'Deployment': ['Testing']
        }
        
        phase_index = all_phases.index(phase_name)
        return dependencies_map.get(phase_name, [])
    
    def _generate_phase_success_criteria(self, phase_name: str, research_type: str) -> List[str]:
        """Generate success criteria for a phase"""
        criteria_map = {
            'Analysis': ['All requirements captured', 'Technical feasibility confirmed', 'Stakeholder approval'],
            'Design': ['Design approved by stakeholders', 'Technical review completed', 'Implementation plan ready'],
            'Implementation': ['All features implemented', 'Code review completed', 'Unit tests passing'],
            'Testing': ['All tests passing', 'Performance requirements met', 'Security requirements met'],
            'Deployment': ['Successfully deployed to production', 'Monitoring active', 'User acceptance confirmed']
        }
        
        return criteria_map.get(phase_name, [f"{phase_name} objectives met"])
    
    def _estimate_timeline(self, 
                          phases: List[Dict[str, Any]],
                          complexity_level: int,
                          constraints: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Estimate project timeline"""
        total_duration = sum(phase['duration_weeks'] for phase in phases)
        
        # Adjust for constraints
        if constraints:
            if 'timeline_limit' in constraints:
                timeline_limit = constraints['timeline_limit']
                if total_duration > timeline_limit:
                    total_duration = timeline_limit
        
        # Calculate start and end dates
        start_date = datetime.now()
        end_date = start_date + timedelta(weeks=total_duration)
        
        # Generate milestone dates
        milestones = []
        current_date = start_date
        
        for phase in phases:
            phase_end = current_date + timedelta(weeks=phase['duration_weeks'])
            milestones.append({
                'phase': phase['name'],
                'end_date': phase_end.isoformat(),
                'duration_weeks': phase['duration_weeks']
            })
            current_date = phase_end
        
        return {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'total_duration_weeks': total_duration,
            'milestones': milestones,
            'complexity_level': complexity_level
        }
    
    def _estimate_resources(self, 
                           phases: List[Dict[str, Any]],
                           complexity_level: int,
                           constraints: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Estimate resource requirements"""
        # Base team size by complexity
        team_size_map = {1: 2, 2: 4, 3: 6, 4: 8}
        base_team_size = team_size_map.get(complexity_level, 4)
        
        # Adjust for constraints
        if constraints and 'team_size_limit' in constraints:
            base_team_size = min(base_team_size, constraints['team_size_limit'])
        
        # Calculate total effort
        total_hours = sum(
            sum(task['estimated_hours'] for task in phase['tasks'])
            for phase in phases
        )
        
        # Estimate roles needed
        roles = {}
        for phase in phases:
            for task in phase['tasks']:
                role = task['assignee_role']
                if role not in roles:
                    roles[role] = 0
                roles[role] += task['estimated_hours']
        
        return {
            'team_size': base_team_size,
            'total_hours': total_hours,
            'estimated_cost': total_hours * 100,  # $100/hour placeholder
            'roles_needed': roles,
            'resource_constraints': constraints.get('resources', {}) if constraints else {}
        }
    
    def _assess_risks(self, 
                     research_data: Dict[str, Any],
                     complexity_level: int,
                     constraints: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess project risks"""
        risks = []
        
        # Complexity-based risks
        if complexity_level >= 4:
            risks.append({
                'type': 'Technical Risk',
                'description': 'High complexity may lead to implementation challenges',
                'probability': 'high',
                'impact': 'high',
                'mitigation': 'Break down into smaller components and ensure expert team'
            })
        
        # Research-based risks
        confidence_score = research_data.get('confidence_score', 0.5)
        if confidence_score < 0.6:
            risks.append({
                'type': 'Information Risk',
                'description': 'Low confidence in research findings may affect implementation',
                'probability': 'medium',
                'impact': 'medium',
                'mitigation': 'Validate findings with additional research or expert consultation'
            })
        
        # Constraint-based risks
        if constraints:
            if 'timeline_limit' in constraints and constraints['timeline_limit'] < 8:
                risks.append({
                    'type': 'Schedule Risk',
                    'description': 'Aggressive timeline may impact quality',
                    'probability': 'high',
                    'impact': 'medium',
                    'mitigation': 'Prioritize features and consider phased delivery'
                })
            
            if 'team_size_limit' in constraints and constraints['team_size_limit'] < 4:
                risks.append({
                    'type': 'Resource Risk',
                    'description': 'Limited team size may slow down implementation',
                    'probability': 'medium',
                    'impact': 'high',
                    'mitigation': 'Consider external resources or extend timeline'
                })
        
        return {
            'identified_risks': risks,
            'risk_level': self._calculate_overall_risk_level(risks),
            'risk_mitigation_strategy': 'Continuous monitoring and adaptive planning'
        }
    
    def _calculate_overall_risk_level(self, risks: List[Dict[str, Any]]) -> str:
        """Calculate overall risk level"""
        if not risks:
            return 'low'
        
        high_risks = [r for r in risks if r['probability'] == 'high' and r['impact'] == 'high']
        if len(high_risks) >= 2:
            return 'high'
        elif len(high_risks) >= 1:
            return 'medium'
        else:
            return 'low'
    
    def _generate_success_metrics(self, research_data: Dict[str, Any], research_type: str) -> List[str]:
        """Generate success metrics based on research"""
        metrics = [
            'Project completed on time and within budget',
            'All functional requirements met',
            'Quality standards achieved',
            'Stakeholder satisfaction confirmed'
        ]
        
        # Add type-specific metrics
        if research_type == 'technical':
            metrics.extend([
                'Performance requirements met',
                'Security standards compliance',
                'Code quality metrics achieved'
            ])
        elif research_type == 'methodology':
            metrics.extend([
                'Process adoption rate > 80%',
                'User satisfaction > 4.0/5.0',
                'Efficiency improvements demonstrated'
            ])
        elif research_type == 'competitive':
            metrics.extend([
                'Market position improved',
                'Competitive advantage achieved',
                'Strategic objectives met'
            ])
        
        return metrics
    
    def _generate_monitoring_plan(self, research_type: str, complexity_level: int) -> Dict[str, Any]:
        """Generate monitoring and tracking plan"""
        return {
            'monitoring_frequency': 'weekly' if complexity_level >= 3 else 'bi-weekly',
            'key_metrics': [
                'Progress against timeline',
                'Budget utilization',
                'Quality metrics',
                'Risk status'
            ],
            'reporting_schedule': 'weekly',
            'escalation_triggers': [
                'Timeline deviation > 10%',
                'Budget overrun > 15%',
                'High-risk issues identified',
                'Stakeholder concerns raised'
            ]
        }
