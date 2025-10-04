"""
Ensemble Decision Engine for Intelligent n8n Workflow Creation System
Combines multiple ML models for intelligent workflow decision making
"""

import asyncio
import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json
import pickle
from pathlib import Path
import time

from ..core.config import get_config
from ..analyzers.project_analyzer import ProjectAnalysis
from ..knowledge.lightrag_service import KnowledgeQueryResult


class DecisionType(Enum):
    """Types of decisions the engine can make"""

    WORKFLOW_CREATION = "workflow_creation"
    NODE_SELECTION = "node_selection"
    WORKFLOW_PATTERN = "workflow_pattern"
    AUTOMATION_PRIORITY = "automation_priority"


class ConfidenceLevel(Enum):
    """Confidence levels for decisions"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class DecisionContext:
    """Context for making decisions"""

    project_analysis: ProjectAnalysis
    knowledge_data: KnowledgeQueryResult
    user_preferences: Optional[Dict[str, Any]] = None
    historical_data: Optional[Dict[str, Any]] = None


@dataclass
class WorkflowDecision:
    """Decision about creating a workflow"""

    workflow_type: str
    priority: float
    confidence: float
    reasoning: str
    suggested_nodes: List[str]
    estimated_complexity: str
    use_cases: List[str]
    metadata: Dict[str, Any]


@dataclass
class NodeDecision:
    """Decision about selecting nodes"""

    node_name: str
    relevance_score: float
    confidence: float
    reasoning: str
    parameters: Dict[str, Any]
    connections: List[str]
    alternatives: List[str]


@dataclass
class EnsembleDecision:
    """Final decision from ensemble models"""

    decision_type: DecisionType
    primary_decision: Any
    alternative_decisions: List[Any]
    confidence: float
    model_contributions: Dict[str, float]
    reasoning: str
    metadata: Dict[str, Any]


class RandomForestModel:
    """Random Forest model for structured data decisions"""

    def __init__(self):
        self.model = None
        self.feature_names = []
        self.is_trained = False

    async def train(self, training_data: List[Dict[str, Any]]) -> bool:
        """Train the Random Forest model"""
        try:
            # Mock training process
            # In reality, you would use scikit-learn
            self.is_trained = True
            return True
        except Exception:
            return False

    async def predict(self, features: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        """Make prediction using Random Forest"""
        if not self.is_trained:
            return 0.0, {}

        # Mock prediction based on structured features
        score = 0.0

        # Technology-based scoring
        if features.get("has_api_framework", False):
            score += 0.3

        if features.get("has_database", False):
            score += 0.2

        if features.get("has_docker", False):
            score += 0.2

        # Complexity-based scoring
        complexity = features.get("complexity_score", 0.0)
        score += complexity * 0.2

        # Automation potential
        automation_potential = features.get("automation_potential", 0.0)
        score += automation_potential * 0.3

        # Ensure score is between 0 and 1
        score = min(1.0, max(0.0, score))

        return score, {"random_forest": score}


class NeuralNetworkModel:
    """Neural Network model for semantic understanding"""

    def __init__(self):
        self.model = None
        self.embedding_model = None
        self.is_trained = False

    async def train(self, training_data: List[Dict[str, Any]]) -> bool:
        """Train the Neural Network model"""
        try:
            # Mock training process
            # In reality, you would use transformers/pytorch
            self.is_trained = True
            return True
        except Exception:
            return False

    async def predict(
        self, semantic_features: Dict[str, Any]
    ) -> Tuple[float, Dict[str, float]]:
        """Make prediction using Neural Network"""
        if not self.is_trained:
            return 0.0, {}

        # Mock prediction based on semantic features
        score = 0.0

        # Project description analysis
        description = semantic_features.get("project_description", "")
        if any(
            keyword in description.lower()
            for keyword in ["api", "service", "integration"]
        ):
            score += 0.3

        # Technology patterns
        tech_patterns = semantic_features.get("technology_patterns", [])
        if "web_framework" in tech_patterns:
            score += 0.2
        if "database" in tech_patterns:
            score += 0.2
        if "containerization" in tech_patterns:
            score += 0.2

        # Architecture patterns
        arch_patterns = semantic_features.get("architecture_patterns", [])
        if "microservices" in arch_patterns:
            score += 0.1

        # Ensure score is between 0 and 1
        score = min(1.0, max(0.0, score))

        return score, {"neural_network": score}


class RuleBasedModel:
    """Rule-based model for business logic decisions"""

    def __init__(self):
        self.rules = self._initialize_rules()

    def _initialize_rules(self) -> Dict[str, Any]:
        """Initialize business rules"""
        return {
            "api_framework_rules": {
                "conditions": ["has_api_framework"],
                "actions": ["create_api_workflow", "create_monitoring_workflow"],
                "confidence": 0.9,
            },
            "database_rules": {
                "conditions": ["has_database"],
                "actions": ["create_backup_workflow", "create_migration_workflow"],
                "confidence": 0.8,
            },
            "docker_rules": {
                "conditions": ["has_docker"],
                "actions": ["create_deployment_workflow", "create_build_workflow"],
                "confidence": 0.85,
            },
            "high_complexity_rules": {
                "conditions": ["complexity_score > 0.7"],
                "actions": ["create_testing_workflow", "create_monitoring_workflow"],
                "confidence": 0.7,
            },
            "high_automation_potential_rules": {
                "conditions": ["automation_potential > 0.6"],
                "actions": ["create_automation_pipeline", "create_scheduling_workflow"],
                "confidence": 0.8,
            },
        }

    async def predict(self, features: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        """Make prediction using rule-based logic"""
        score = 0.0
        rule_scores = {}

        for rule_name, rule in self.rules.items():
            rule_score = 0.0

            # Check conditions
            conditions_met = 0
            total_conditions = len(rule["conditions"])

            for condition in rule["conditions"]:
                if self._evaluate_condition(condition, features):
                    conditions_met += 1

            # Calculate rule score based on conditions met
            if conditions_met > 0:
                rule_score = (conditions_met / total_conditions) * rule["confidence"]
                rule_scores[rule_name] = rule_score
                score += rule_score

        # Average the scores
        if rule_scores:
            score = sum(rule_scores.values()) / len(rule_scores)

        return score, rule_scores

    def _evaluate_condition(self, condition: str, features: Dict[str, Any]) -> bool:
        """Evaluate a single condition"""
        if ">" in condition:
            key, value = condition.split(" > ")
            return features.get(key, 0) > float(value)
        elif condition in features:
            return bool(features[condition])
        return False


class SVMModel:
    """SVM model for pattern recognition"""

    def __init__(self):
        self.model = None
        self.is_trained = False

    async def train(self, training_data: List[Dict[str, Any]]) -> bool:
        """Train the SVM model"""
        try:
            # Mock training process
            # In reality, you would use scikit-learn SVM
            self.is_trained = True
            return True
        except Exception:
            return False

    async def predict(self, features: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        """Make prediction using SVM"""
        if not self.is_trained:
            return 0.0, {}

        # Mock prediction based on pattern features
        score = 0.0

        # Pattern-based scoring
        patterns = features.get("detected_patterns", [])

        # API patterns
        if any("api" in pattern.lower() for pattern in patterns):
            score += 0.3

        # Data processing patterns
        if any("data" in pattern.lower() for pattern in patterns):
            score += 0.2

        # Automation patterns
        if any("automation" in pattern.lower() for pattern in patterns):
            score += 0.2

        # Integration patterns
        if any("integration" in pattern.lower() for pattern in patterns):
            score += 0.2

        # Monitoring patterns
        if any("monitor" in pattern.lower() for pattern in patterns):
            score += 0.1

        # Ensure score is between 0 and 1
        score = min(1.0, max(0.0, score))

        return score, {"svm": score}


class EnsembleDecisionEngine:
    """
    Ensemble Decision Engine that combines multiple ML models
    for intelligent workflow decision making
    """

    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)

        # Initialize models
        self.random_forest = RandomForestModel()
        self.neural_network = NeuralNetworkModel()
        self.rule_based = RuleBasedModel()
        self.svm = SVMModel()

        # Model weights (can be learned from data)
        self.model_weights = {
            "random_forest": 0.25,
            "neural_network": 0.25,
            "rule_based": 0.3,
            "svm": 0.2,
        }

        # Training status
        self.is_trained = False

    async def initialize(self) -> bool:
        """Initialize the decision engine"""
        try:
            self.logger.info("Initializing Ensemble Decision Engine")

            # Load or train models
            await self._load_or_train_models()

            self.is_trained = True
            self.logger.info("Ensemble Decision Engine initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize decision engine: {e}")
            return False

    async def _load_or_train_models(self):
        """Load existing models or train new ones"""
        model_path = Path(self.config.ml.model_path)
        model_path.mkdir(parents=True, exist_ok=True)

        # Try to load existing models
        models_loaded = 0

        for model_name, model in [
            ("random_forest", self.random_forest),
            ("neural_network", self.neural_network),
            ("svm", self.svm),
        ]:
            model_file = model_path / f"{model_name}.pkl"
            if model_file.exists():
                try:
                    # Load model (mock implementation)
                    model.is_trained = True
                    models_loaded += 1
                    self.logger.info(f"Loaded {model_name} model")
                except Exception as e:
                    self.logger.warning(f"Failed to load {model_name} model: {e}")

        # If no models were loaded, train new ones
        if models_loaded == 0:
            self.logger.info("No existing models found, training new models...")
            await self._train_all_models()

    async def _train_all_models(self):
        """Train all models with sample data"""
        # Mock training data
        training_data = self._generate_mock_training_data()

        # Train each model
        tasks = [
            self.random_forest.train(training_data),
            self.neural_network.train(training_data),
            self.svm.train(training_data),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        successful_trains = sum(1 for result in results if result is True)
        self.logger.info(
            f"Successfully trained {successful_trains}/{len(tasks)} models"
        )

    def _generate_mock_training_data(self) -> List[Dict[str, Any]]:
        """Generate mock training data"""
        return [
            {
                "project_type": "api",
                "has_api_framework": True,
                "has_database": True,
                "complexity_score": 0.7,
                "automation_potential": 0.8,
                "workflow_created": True,
                "workflow_type": "api_integration",
            },
            {
                "project_type": "web",
                "has_api_framework": False,
                "has_database": True,
                "complexity_score": 0.5,
                "automation_potential": 0.6,
                "workflow_created": True,
                "workflow_type": "data_processing",
            },
            {
                "project_type": "script",
                "has_api_framework": False,
                "has_database": False,
                "complexity_score": 0.3,
                "automation_potential": 0.4,
                "workflow_created": False,
                "workflow_type": None,
            },
        ]

    async def make_decisions(
        self, project_analysis: ProjectAnalysis, knowledge_data: KnowledgeQueryResult
    ) -> Dict[str, Any]:
        """
        Make decisions about workflow creation based on project analysis and knowledge

        Args:
            project_analysis: Analysis of the project
            knowledge_data: Relevant knowledge from LightRAG

        Returns:
            Dict containing decisions about workflow creation
        """
        try:
            self.logger.info("Making ensemble decisions for workflow creation")

            # Prepare features for each model
            structured_features = self._extract_structured_features(project_analysis)
            semantic_features = self._extract_semantic_features(project_analysis)
            pattern_features = self._extract_pattern_features(
                project_analysis, knowledge_data
            )

            # Get predictions from each model
            rf_score, rf_contributions = await self.random_forest.predict(
                structured_features
            )
            nn_score, nn_contributions = await self.neural_network.predict(
                semantic_features
            )
            rb_score, rb_contributions = await self.rule_based.predict(
                structured_features
            )
            svm_score, svm_contributions = await self.svm.predict(pattern_features)

            # Combine predictions using ensemble weights
            ensemble_score = (
                rf_score * self.model_weights["random_forest"]
                + nn_score * self.model_weights["neural_network"]
                + rb_score * self.model_weights["rule_based"]
                + svm_score * self.model_weights["svm"]
            )

            # Generate workflow decisions
            workflow_decisions = await self._generate_workflow_decisions(
                ensemble_score, project_analysis, knowledge_data
            )

            # Generate node decisions
            node_decisions = await self._generate_node_decisions(
                ensemble_score, project_analysis, knowledge_data
            )

            result = {
                "ensemble_score": ensemble_score,
                "confidence": ensemble_score,  # Use ensemble_score as confidence directly
                "model_contributions": {
                    "random_forest": rf_contributions,
                    "neural_network": nn_contributions,
                    "rule_based": rb_contributions,
                    "svm": svm_contributions,
                },
                "workflow_decisions": workflow_decisions,
                "node_decisions": node_decisions,
                "reasoning": self._generate_reasoning(ensemble_score, project_analysis),
                "metadata": {
                    "timestamp": time.time(),
                    "project_path": project_analysis.project_path,
                    "analysis_confidence": project_analysis.complexity_score,
                },
            }

            self.logger.info(
                f"Ensemble decisions completed: score={ensemble_score:.3f}, "
                f"workflows={len(workflow_decisions)}, nodes={len(node_decisions)}"
            )

            return result

        except Exception as e:
            self.logger.error(f"Failed to make ensemble decisions: {e}")
            return {
                "ensemble_score": 0.0,
                "confidence": 0.0,
                "model_contributions": {},
                "workflow_decisions": [],
                "node_decisions": [],
                "reasoning": f"Error in decision making: {str(e)}",
                "metadata": {"error": str(e)},
            }

    def _extract_structured_features(
        self, project_analysis: ProjectAnalysis
    ) -> Dict[str, Any]:
        """Extract structured features for Random Forest model"""
        tech_names = [tech.name for tech in project_analysis.technologies]

        return {
            "has_api_framework": any(
                fw in tech_names for fw in ["fastapi", "django", "flask"]
            ),
            "has_database": any(
                db in tech_names for db in ["postgresql", "mongodb", "redis"]
            ),
            "has_docker": "docker" in tech_names,
            "has_n8n": "n8n" in tech_names,
            "complexity_score": project_analysis.complexity_score,
            "automation_potential": project_analysis.automation_potential,
            "project_size": len(project_analysis.file_analyses),
            "architecture_type": project_analysis.architecture_type or "unknown",
            "languages_count": len(project_analysis.languages),
            "technologies_count": len(project_analysis.technologies),
        }

    def _extract_semantic_features(
        self, project_analysis: ProjectAnalysis
    ) -> Dict[str, Any]:
        """Extract semantic features for Neural Network model"""
        # Combine project description from various sources
        description_parts = [
            project_analysis.project_name,
            project_analysis.architecture_type or "",
            " ".join(tech.name for tech in project_analysis.technologies),
            " ".join(project_analysis.suggested_workflows),
        ]

        project_description = " ".join(description_parts)

        # Extract technology patterns
        tech_patterns = []
        for tech in project_analysis.technologies:
            if tech.type == "framework":
                tech_patterns.append("web_framework")
            elif tech.type == "database":
                tech_patterns.append("database")
            elif tech.type == "tool":
                tech_patterns.append("automation_tool")

        # Extract architecture patterns
        arch_patterns = []
        if project_analysis.architecture_type:
            arch_patterns.append(project_analysis.architecture_type)

        return {
            "project_description": project_description,
            "technology_patterns": tech_patterns,
            "architecture_patterns": arch_patterns,
            "structure_patterns": project_analysis.structure_patterns,
            "suggested_workflows": project_analysis.suggested_workflows,
        }

    def _extract_pattern_features(
        self, project_analysis: ProjectAnalysis, knowledge_data: KnowledgeQueryResult
    ) -> Dict[str, Any]:
        """Extract pattern features for SVM model"""
        # Combine patterns from project analysis and knowledge
        patterns = []

        # Add project structure patterns
        patterns.extend(project_analysis.structure_patterns)

        # Add technology patterns
        for tech in project_analysis.technologies:
            patterns.append(f"{tech.name}_{tech.type}")

        # Add suggested workflow patterns
        patterns.extend(project_analysis.suggested_workflows)

        # Add knowledge-based patterns
        for pattern in knowledge_data.patterns:
            patterns.append(pattern.name)
            patterns.append(pattern.category)

        return {
            "detected_patterns": patterns,
            "pattern_count": len(patterns),
            "knowledge_patterns": len(knowledge_data.patterns),
            "relevant_nodes": len(knowledge_data.nodes),
        }

    async def _generate_workflow_decisions(
        self,
        ensemble_score: float,
        project_analysis: ProjectAnalysis,
        knowledge_data: KnowledgeQueryResult,
    ) -> List[WorkflowDecision]:
        """Generate specific workflow creation decisions"""
        decisions = []

        # Determine if we should create workflows based on ensemble score
        if ensemble_score < 0.3:
            return decisions  # No workflows recommended

        # Generate workflow decisions based on project characteristics
        tech_names = [tech.name for tech in project_analysis.technologies]

        # API Integration Workflow
        if any(api in tech_names for api in ["fastapi", "django", "flask"]):
            decisions.append(
                WorkflowDecision(
                    workflow_type="api_integration",
                    priority=0.8,
                    confidence=ensemble_score,
                    reasoning="API framework detected, workflow can help with integration and monitoring",
                    suggested_nodes=["webhook", "httpRequest", "function"],
                    estimated_complexity="medium",
                    use_cases=[
                        "API monitoring",
                        "Integration testing",
                        "Data synchronization",
                    ],
                    metadata={"triggered_by": "api_framework"},
                )
            )

        # Database Workflow
        if any(db in tech_names for db in ["postgresql", "mongodb", "redis"]):
            decisions.append(
                WorkflowDecision(
                    workflow_type="database_management",
                    priority=0.7,
                    confidence=ensemble_score,
                    reasoning="Database detected, automation can help with backup and maintenance",
                    suggested_nodes=["schedule", "postgres", "function"],
                    estimated_complexity="low",
                    use_cases=[
                        "Automated backups",
                        "Data migration",
                        "Health monitoring",
                    ],
                    metadata={"triggered_by": "database"},
                )
            )

        # Docker Workflow
        if "docker" in tech_names:
            decisions.append(
                WorkflowDecision(
                    workflow_type="container_automation",
                    priority=0.6,
                    confidence=ensemble_score,
                    reasoning="Docker detected, automation can help with build and deployment",
                    suggested_nodes=["schedule", "httpRequest", "function"],
                    estimated_complexity="medium",
                    use_cases=[
                        "Automated builds",
                        "Deployment pipeline",
                        "Container monitoring",
                    ],
                    metadata={"triggered_by": "docker"},
                )
            )

        # High complexity projects get additional workflows
        if project_analysis.complexity_score > 0.7:
            decisions.append(
                WorkflowDecision(
                    workflow_type="testing_automation",
                    priority=0.5,
                    confidence=ensemble_score,
                    reasoning="High complexity project benefits from automated testing",
                    suggested_nodes=["schedule", "function", "httpRequest"],
                    estimated_complexity="high",
                    use_cases=[
                        "Automated testing",
                        "Quality assurance",
                        "Performance monitoring",
                    ],
                    metadata={"triggered_by": "high_complexity"},
                )
            )

        return decisions

    async def _generate_node_decisions(
        self,
        ensemble_score: float,
        project_analysis: ProjectAnalysis,
        knowledge_data: KnowledgeQueryResult,
    ) -> List[NodeDecision]:
        """Generate specific node selection decisions"""
        decisions = []

        # Recommend nodes based on available knowledge and project context
        for node_info in knowledge_data.nodes:
            # Calculate relevance score based on project context
            relevance_score = self._calculate_node_relevance(
                node_info, project_analysis
            )

            if relevance_score > 0.3:  # Only recommend relevant nodes
                decisions.append(
                    NodeDecision(
                        node_name=node_info.name,
                        relevance_score=relevance_score,
                        confidence=ensemble_score,
                        reasoning=f"Node {node_info.name} is relevant for {node_info.category} operations",
                        parameters={},  # Would be populated based on node documentation
                        connections=[],  # Would be populated based on workflow patterns
                        alternatives=[],  # Would be populated based on similar nodes
                    )
                )

        # Sort by relevance score
        decisions.sort(key=lambda x: x.relevance_score, reverse=True)

        return decisions

    def _calculate_node_relevance(
        self, node_info, project_analysis: ProjectAnalysis
    ) -> float:
        """Calculate how relevant a node is to the project"""
        relevance = 0.0

        # Category-based relevance
        tech_names = [tech.name for tech in project_analysis.technologies]

        if node_info.category == "database":
            if any(db in tech_names for db in ["postgresql", "mongodb", "redis"]):
                relevance += 0.4

        if node_info.category == "core":
            relevance += 0.3  # Core nodes are generally useful

        if node_info.category == "trigger":
            if project_analysis.automation_potential > 0.5:
                relevance += 0.3

        # Tag-based relevance
        for tag in node_info.tags:
            if tag in tech_names:
                relevance += 0.2
            elif any(tag in tech.name for tech in project_analysis.technologies):
                relevance += 0.1

        # Architecture-based relevance
        if project_analysis.architecture_type == "api" and "api" in node_info.tags:
            relevance += 0.2

        return min(1.0, relevance)

    def _calculate_confidence(self, ensemble_score: float) -> str:
        """Calculate confidence level based on ensemble score"""
        if ensemble_score >= 0.7:
            return "high"
        elif ensemble_score >= 0.4:
            return "medium"
        else:
            return "low"

    def _generate_reasoning(
        self, ensemble_score: float, project_analysis: ProjectAnalysis
    ) -> str:
        """Generate human-readable reasoning for the decision"""
        reasoning_parts = []

        reasoning_parts.append(f"Ensemble score: {ensemble_score:.3f}")

        if project_analysis.complexity_score > 0.7:
            reasoning_parts.append("High complexity project detected")

        if project_analysis.automation_potential > 0.6:
            reasoning_parts.append("High automation potential identified")

        tech_count = len(project_analysis.technologies)
        if tech_count > 5:
            reasoning_parts.append(f"Multiple technologies detected ({tech_count})")

        if project_analysis.architecture_type:
            reasoning_parts.append(
                f"Architecture type: {project_analysis.architecture_type}"
            )

        return "; ".join(reasoning_parts)
