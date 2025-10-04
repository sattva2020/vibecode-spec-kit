"""
Workflow Generator for Intelligent n8n Workflow Creation System
Generates actual n8n workflows based on decisions from the ensemble engine
"""

import asyncio
import logging
import json
import uuid
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import time

from ..core.config import get_config
from ..decision.ensemble_decision_engine import WorkflowDecision, NodeDecision, EnsembleDecision
from ..knowledge.lightrag_service import N8nNodeInfo, WorkflowPattern


class WorkflowStatus(Enum):
    """Status of workflow generation"""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class GeneratedWorkflow:
    """Generated n8n workflow"""
    id: str
    name: str
    description: str
    nodes: List[Dict[str, Any]]
    connections: List[Dict[str, Any]]
    settings: Dict[str, Any]
    metadata: Dict[str, Any]
    status: WorkflowStatus
    confidence: float
    estimated_runtime: Optional[int] = None


@dataclass
class NodeTemplate:
    """Template for generating n8n nodes"""
    name: str
    display_name: str
    type: str
    category: str
    default_parameters: Dict[str, Any]
    required_parameters: List[str]
    optional_parameters: List[str]
    outputs: List[str]
    inputs: List[str]


class WorkflowGenerator:
    """
    Generates actual n8n workflows based on decisions from the ensemble engine
    """
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        
        # Node templates for common n8n nodes
        self.node_templates = self._initialize_node_templates()
        
        # Workflow patterns
        self.workflow_patterns = {}
        
        # Generation statistics
        self.generation_stats = {
            "total_generated": 0,
            "successful": 0,
            "failed": 0,
            "average_confidence": 0.0
        }
    
    def _initialize_node_templates(self) -> Dict[str, NodeTemplate]:
        """Initialize templates for common n8n nodes"""
        return {
            "webhook": NodeTemplate(
                name="webhook",
                display_name="Webhook",
                type="n8n-nodes-base.webhook",
                category="trigger",
                default_parameters={
                    "path": "webhook",
                    "httpMethod": "POST",
                    "responseMode": "responseNode",
                    "options": {}
                },
                required_parameters=["path"],
                optional_parameters=["httpMethod", "responseMode", "options"],
                outputs=["items"],
                inputs=[]
            ),
            "httpRequest": NodeTemplate(
                name="httpRequest",
                display_name="HTTP Request",
                type="n8n-nodes-base.httpRequest",
                category="core",
                default_parameters={
                    "url": "",
                    "method": "GET",
                    "sendHeaders": True,
                    "headerParameters": {},
                    "sendBody": False,
                    "options": {}
                },
                required_parameters=["url"],
                optional_parameters=["method", "sendHeaders", "headerParameters", "sendBody", "options"],
                outputs=["items"],
                inputs=["items"]
            ),
            "function": NodeTemplate(
                name="function",
                display_name="Function",
                type="n8n-nodes-base.function",
                category="core",
                default_parameters={
                    "functionCode": "// Add your code here\nreturn items;"
                },
                required_parameters=["functionCode"],
                optional_parameters=[],
                outputs=["items"],
                inputs=["items"]
            ),
            "schedule": NodeTemplate(
                name="schedule",
                display_name="Schedule Trigger",
                type="n8n-nodes-base.scheduleTrigger",
                category="trigger",
                default_parameters={
                    "rule": {
                        "interval": [
                            {
                                "field": "minutes",
                                "minutesInterval": 5
                            }
                        ]
                    }
                },
                required_parameters=["rule"],
                optional_parameters=[],
                outputs=["items"],
                inputs=[]
            ),
            "postgres": NodeTemplate(
                name="postgres",
                display_name="PostgreSQL",
                type="n8n-nodes-base.postgres",
                category="database",
                default_parameters={
                    "operation": "executeQuery",
                    "query": "SELECT * FROM table_name LIMIT 10;"
                },
                required_parameters=["operation", "query"],
                optional_parameters=["options"],
                outputs=["items"],
                inputs=["items"]
            ),
            "email": NodeTemplate(
                name="email",
                display_name="Email",
                type="n8n-nodes-base.emailSend",
                category="communication",
                default_parameters={
                    "fromEmail": "",
                    "toEmail": "",
                    "subject": "",
                    "message": ""
                },
                required_parameters=["fromEmail", "toEmail", "subject", "message"],
                optional_parameters=["options"],
                outputs=["items"],
                inputs=["items"]
            ),
            "slack": NodeTemplate(
                name="slack",
                display_name="Slack",
                type="n8n-nodes-base.slack",
                category="communication",
                default_parameters={
                    "resource": "message",
                    "operation": "post",
                    "channel": "",
                    "text": ""
                },
                required_parameters=["resource", "operation", "channel", "text"],
                optional_parameters=["options"],
                outputs=["items"],
                inputs=["items"]
            )
        }
    
    async def generate_workflows(
        self,
        decisions: Dict[str, Any],
        project_analysis: Any
    ) -> List[GeneratedWorkflow]:
        """
        Generate n8n workflows based on ensemble decisions
        
        Args:
            decisions: Decisions from the ensemble engine
            project_analysis: Project analysis data
            
        Returns:
            List of generated workflows
        """
        try:
            self.logger.info("Starting workflow generation")
            
            workflow_decisions = decisions.get("workflow_decisions", [])
            node_decisions = decisions.get("node_decisions", [])
            
            if not workflow_decisions:
                self.logger.info("No workflow decisions to generate")
                return []
            
            generated_workflows = []
            
            for workflow_decision in workflow_decisions:
                try:
                    workflow = await self._generate_single_workflow(
                        workflow_decision, node_decisions, project_analysis
                    )
                    if workflow:
                        generated_workflows.append(workflow)
                        self.generation_stats["successful"] += 1
                except Exception as e:
                    self.logger.error(f"Failed to generate workflow {workflow_decision.workflow_type}: {e}")
                    self.generation_stats["failed"] += 1
            
            self.generation_stats["total_generated"] += len(generated_workflows)
            self._update_average_confidence(generated_workflows)
            
            self.logger.info(f"Generated {len(generated_workflows)} workflows successfully")
            return generated_workflows
            
        except Exception as e:
            self.logger.error(f"Failed to generate workflows: {e}")
            return []
    
    async def _generate_single_workflow(
        self,
        workflow_decision: WorkflowDecision,
        node_decisions: List[NodeDecision],
        project_analysis: Any
    ) -> Optional[GeneratedWorkflow]:
        """Generate a single workflow based on a decision"""
        try:
            workflow_id = str(uuid.uuid4())
            workflow_name = self._generate_workflow_name(workflow_decision, project_analysis)
            
            # Generate nodes for the workflow
            nodes = await self._generate_workflow_nodes(
                workflow_decision, node_decisions, project_analysis
            )
            
            # Generate connections between nodes
            connections = await self._generate_workflow_connections(nodes)
            
            # Generate workflow settings
            settings = self._generate_workflow_settings(workflow_decision)
            
            # Create workflow metadata
            metadata = {
                "generated_at": time.time(),
                "project_path": project_analysis.project_path,
                "workflow_type": workflow_decision.workflow_type,
                "decision_confidence": workflow_decision.confidence,
                "suggested_nodes": workflow_decision.suggested_nodes,
                "use_cases": workflow_decision.use_cases
            }
            
            workflow = GeneratedWorkflow(
                id=workflow_id,
                name=workflow_name,
                description=workflow_decision.reasoning,
                nodes=nodes,
                connections=connections,
                settings=settings,
                metadata=metadata,
                status=WorkflowStatus.COMPLETED,
                confidence=workflow_decision.confidence,
                estimated_runtime=self._estimate_runtime(nodes)
            )
            
            return workflow
            
        except Exception as e:
            self.logger.error(f"Failed to generate single workflow: {e}")
            return None
    
    def _generate_workflow_name(self, workflow_decision: WorkflowDecision, project_analysis: Any) -> str:
        """Generate a descriptive name for the workflow"""
        project_name = project_analysis.project_name
        workflow_type = workflow_decision.workflow_type
        
        # Convert workflow type to readable format
        readable_type = workflow_type.replace("_", " ").title()
        
        return f"{project_name} - {readable_type}"
    
    async def _generate_workflow_nodes(
        self,
        workflow_decision: WorkflowDecision,
        node_decisions: List[NodeDecision],
        project_analysis: Any
    ) -> List[Dict[str, Any]]:
        """Generate nodes for the workflow"""
        nodes = []
        position_x = 240
        position_y = 300
        
        # Determine workflow pattern based on type
        pattern = self._get_workflow_pattern(workflow_decision.workflow_type)
        
        for i, node_name in enumerate(pattern.get("nodes", [])):
            if node_name in self.node_templates:
                node_template = self.node_templates[node_name]
                node = await self._create_node_from_template(
                    node_template, position_x, position_y, workflow_decision, project_analysis
                )
                nodes.append(node)
                
                # Update position for next node
                position_x += 220
        
        return nodes
    
    def _get_workflow_pattern(self, workflow_type: str) -> Dict[str, Any]:
        """Get workflow pattern for a specific type"""
        patterns = {
            "api_integration": {
                "nodes": ["webhook", "function", "httpRequest"],
                "description": "API integration workflow with data processing"
            },
            "database_management": {
                "nodes": ["schedule", "postgres", "function"],
                "description": "Database management with scheduled operations"
            },
            "container_automation": {
                "nodes": ["schedule", "httpRequest", "function"],
                "description": "Container automation with HTTP requests"
            },
            "testing_automation": {
                "nodes": ["schedule", "function", "httpRequest", "email"],
                "description": "Automated testing with notifications"
            },
            "monitoring_workflow": {
                "nodes": ["schedule", "httpRequest", "function", "slack"],
                "description": "Monitoring workflow with alerts"
            },
            "data_processing": {
                "nodes": ["webhook", "function", "postgres"],
                "description": "Data processing pipeline"
            }
        }
        
        return patterns.get(workflow_type, {
            "nodes": ["webhook", "function"],
            "description": "Generic workflow"
        })
    
    async def _create_node_from_template(
        self,
        template: NodeTemplate,
        x: int,
        y: int,
        workflow_decision: WorkflowDecision,
        project_analysis: Any
    ) -> Dict[str, Any]:
        """Create a node from template with customized parameters"""
        node_id = str(uuid.uuid4())
        
        # Start with default parameters
        parameters = template.default_parameters.copy()
        
        # Customize parameters based on workflow decision and project analysis
        parameters = self._customize_node_parameters(
            template, parameters, workflow_decision, project_analysis
        )
        
        node = {
            "id": node_id,
            "name": template.display_name,
            "type": template.type,
            "typeVersion": 1,
            "position": [x, y],
            "parameters": parameters
        }
        
        return node
    
    def _customize_node_parameters(
        self,
        template: NodeTemplate,
        parameters: Dict[str, Any],
        workflow_decision: WorkflowDecision,
        project_analysis: Any
    ) -> Dict[str, Any]:
        """Customize node parameters based on context"""
        
        if template.name == "webhook":
            # Customize webhook path based on workflow type
            parameters["path"] = f"{workflow_decision.workflow_type}-webhook"
        
        elif template.name == "httpRequest":
            # Set default URL based on project context
            if project_analysis.architecture_type == "api":
                parameters["url"] = "http://localhost:8000/api"
            else:
                parameters["url"] = "https://api.example.com"
        
        elif template.name == "function":
            # Generate function code based on workflow type
            parameters["functionCode"] = self._generate_function_code(
                workflow_decision.workflow_type, project_analysis
            )
        
        elif template.name == "schedule":
            # Set schedule based on workflow type
            if workflow_decision.workflow_type == "database_management":
                # Run database tasks less frequently
                parameters["rule"]["interval"][0]["minutesInterval"] = 60
            else:
                # Default to 5 minutes
                parameters["rule"]["interval"][0]["minutesInterval"] = 5
        
        elif template.name == "postgres":
            # Set database query based on project context
            if "postgresql" in [tech.name for tech in project_analysis.technologies]:
                parameters["query"] = "SELECT COUNT(*) FROM users;"
            else:
                parameters["query"] = "SELECT version();"
        
        elif template.name == "email":
            # Set email parameters
            parameters["subject"] = f"Workflow Alert: {workflow_decision.workflow_type}"
            parameters["message"] = f"Workflow {workflow_decision.workflow_type} has been executed."
        
        elif template.name == "slack":
            # Set Slack parameters
            parameters["channel"] = "#alerts"
            parameters["text"] = f"Workflow {workflow_decision.workflow_type} completed"
        
        return parameters
    
    def _generate_function_code(self, workflow_type: str, project_analysis: Any) -> str:
        """Generate function code based on workflow type"""
        
        if workflow_type == "api_integration":
            return '''
// API Integration Function
const items = $input.all();

// Process incoming data
const processedItems = items.map(item => {
    const data = item.json;
    
    // Add timestamp
    data.processed_at = new Date().toISOString();
    
    // Validate required fields
    if (!data.id) {
        data.error = "Missing required field: id";
    }
    
    return {
        json: data,
        binary: {}
    };
});

return processedItems;
'''
        
        elif workflow_type == "database_management":
            return '''
// Database Management Function
const items = $input.all();

// Process database results
const processedItems = items.map(item => {
    const data = item.json;
    
    // Add processing timestamp
    data.processed_at = new Date().toISOString();
    
    // Check if query was successful
    if (data.error) {
        data.status = "error";
    } else {
        data.status = "success";
        data.record_count = Array.isArray(data.result) ? data.result.length : 1;
    }
    
    return {
        json: data,
        binary: {}
    };
});

return processedItems;
'''
        
        elif workflow_type == "monitoring_workflow":
            return '''
// Monitoring Function
const items = $input.all();

const results = items.map(item => {
    const data = item.json;
    
    // Check response status
    const isHealthy = data.status === 200 || data.status === "ok";
    
    return {
        json: {
            timestamp: new Date().toISOString(),
            service: data.url || "unknown",
            status: isHealthy ? "healthy" : "unhealthy",
            response_time: data.response_time || 0,
            details: data
        },
        binary: {}
    };
});

return results;
'''
        
        else:
            return '''
// Generic Processing Function
const items = $input.all();

const processedItems = items.map(item => {
    const data = item.json;
    
    // Add processing metadata
    data.processed_at = new Date().toISOString();
    data.workflow_type = "generic";
    
    return {
        json: data,
        binary: {}
    };
});

return processedItems;
'''
    
    async def _generate_workflow_connections(self, nodes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate connections between workflow nodes"""
        connections = {}
        
        # Connect nodes sequentially
        for i in range(len(nodes) - 1):
            current_node_id = nodes[i]["id"]
            next_node_id = nodes[i + 1]["id"]
            
            if current_node_id not in connections:
                connections[current_node_id] = {"main": []}
            
            connections[current_node_id]["main"].append([
                {
                    "node": next_node_id,
                    "type": "main",
                    "index": 0
                }
            ])
        
        return connections
    
    def _generate_workflow_settings(self, workflow_decision: WorkflowDecision) -> Dict[str, Any]:
        """Generate workflow settings"""
        return {
            "executionOrder": "v1",
            "saveManualExecutions": True,
            "callerPolicy": "workflowsFromSameOwner",
            "errorWorkflow": "",
            "timezone": "UTC"
        }
    
    def _estimate_runtime(self, nodes: List[Dict[str, Any]]) -> int:
        """Estimate workflow runtime in seconds"""
        # Base runtime for each node type
        node_runtimes = {
            "webhook": 0,  # Trigger nodes have no runtime
            "schedule": 0,  # Trigger nodes have no runtime
            "function": 2,  # Function execution
            "httpRequest": 5,  # HTTP request
            "postgres": 3,  # Database query
            "email": 2,  # Email sending
            "slack": 2  # Slack message
        }
        
        total_runtime = 0
        for node in nodes:
            node_type = node["type"].split(".")[-1]  # Extract node type
            runtime = node_runtimes.get(node_type, 1)  # Default 1 second
            total_runtime += runtime
        
        return total_runtime
    
    def _update_average_confidence(self, workflows: List[GeneratedWorkflow]):
        """Update average confidence statistics"""
        if workflows:
            total_confidence = sum(w.confidence for w in workflows)
            self.generation_stats["average_confidence"] = total_confidence / len(workflows)
    
    async def validate_workflow(self, workflow: GeneratedWorkflow) -> Tuple[bool, List[str]]:
        """Validate a generated workflow"""
        errors = []
        
        # Check if workflow has nodes
        if not workflow.nodes:
            errors.append("Workflow has no nodes")
        
        # Check if workflow has connections (except for single-node workflows)
        if len(workflow.nodes) > 1 and not workflow.connections:
            errors.append("Multi-node workflow has no connections")
        
        # Validate each node
        for node in workflow.nodes:
            node_errors = self._validate_node(node)
            errors.extend(node_errors)
        
        # Check for required trigger nodes
        has_trigger = any(
            node["type"].endswith(".webhook") or 
            node["type"].endswith(".scheduleTrigger") or
            node["type"].endswith(".manualTrigger")
            for node in workflow.nodes
        )
        
        if not has_trigger:
            errors.append("Workflow has no trigger node")
        
        return len(errors) == 0, errors
    
    def _validate_node(self, node: Dict[str, Any]) -> List[str]:
        """Validate a single node"""
        errors = []
        
        # Check required fields
        required_fields = ["id", "name", "type", "position", "parameters"]
        for field in required_fields:
            if field not in node:
                errors.append(f"Node missing required field: {field}")
        
        # Validate node type
        if "type" not in node or not node["type"]:
            errors.append("Node has invalid type")
        
        # Validate position
        if "position" in node:
            position = node["position"]
            if not isinstance(position, list) or len(position) != 2:
                errors.append("Node has invalid position")
        
        return errors
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get workflow generation statistics"""
        return self.generation_stats.copy()
    
    async def export_workflow(self, workflow: GeneratedWorkflow, format: str = "json") -> str:
        """Export workflow in specified format"""
        if format == "json":
            return json.dumps(asdict(workflow), indent=2)
        elif format == "n8n":
            # Export in n8n format
            n8n_workflow = {
                "name": workflow.name,
                "nodes": workflow.nodes,
                "connections": workflow.connections,
                "settings": workflow.settings,
                "active": False,
                "versionId": 1
            }
            return json.dumps(n8n_workflow, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")
