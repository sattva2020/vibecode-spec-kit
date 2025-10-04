"""
Workflow Generator for Intelligent n8n Workflow Creation System
"""

import logging
from typing import Dict, Any, List
from dataclasses import dataclass
import asyncio


@dataclass
class WorkflowNode:
    """Represents a workflow node"""

    id: str
    name: str
    type: str
    parameters: Dict[str, Any]
    position: List[int]


@dataclass
class Workflow:
    """Represents a complete workflow"""

    name: str
    nodes: List[WorkflowNode]
    connections: Dict[str, Any]
    metadata: Dict[str, Any]


class WorkflowGenerator:
    """Generates n8n workflows based on decisions"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def generate_workflows(
        self, decisions: Dict[str, Any], project_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate workflows based on decisions and project analysis

        Args:
            decisions: Decision results from decision engine
            project_analysis: Project analysis results

        Returns:
            List of generated workflows
        """
        self.logger.info("Generating workflows based on decisions")

        workflows = []

        # Extract workflow decisions
        workflow_decisions = decisions.get("workflow_decisions", [])

        for decision in workflow_decisions:
            # Handle both dict and WorkflowDecision object formats
            if hasattr(decision, 'workflow_type'):
                # WorkflowDecision object
                workflow = await self._generate_single_workflow(
                    decision, project_analysis
                )
                if workflow:
                    workflows.append(workflow)
            elif decision.get("decision") == "create":
                # Dict format
                workflow = await self._generate_single_workflow(
                    decision, project_analysis
                )
                if workflow:
                    workflows.append(workflow)

        self.logger.info(f"Generated {len(workflows)} workflows")
        return workflows

    async def _generate_single_workflow(
        self, decision: Any, project_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a single workflow"""

        # Handle both dict and WorkflowDecision object formats
        if hasattr(decision, 'workflow_type'):
            workflow_type = decision.workflow_type
            suggested_nodes = decision.suggested_nodes
            suggested_connections = []  # WorkflowDecision doesn't have connections
            confidence = decision.confidence
            reasoning = decision.reasoning
        else:
            workflow_type = decision.get("workflow_type", "unknown")
            suggested_nodes = decision.get("suggested_nodes", [])
            suggested_connections = decision.get("suggested_connections", [])
            confidence = decision.get("confidence", 0.5)
            reasoning = decision.get("reason", "")

        # Create workflow structure
        workflow = {
            "name": f"{workflow_type.title()} Workflow",
            "nodes": [],
            "connections": {},
            "metadata": {
                "type": workflow_type,
                "confidence": confidence,
                "reason": reasoning,
                "generated_at": "2024-01-01T00:00:00Z",
            },
        }

        # Generate nodes
        node_id_counter = 1
        for node_type in suggested_nodes:
            node = self._create_node(node_type, node_id_counter)
            workflow["nodes"].append(node)
            node_id_counter += 1

        # Generate connections
        for connection in suggested_connections:
            from_node = connection.get("from")
            to_node = connection.get("to")

            if from_node and to_node:
                if from_node not in workflow["connections"]:
                    workflow["connections"][from_node] = {"main": []}

                workflow["connections"][from_node]["main"].append(
                    [{"node": to_node, "type": "main", "index": 0}]
                )

        return workflow

    def _create_node(self, node_type: str, node_id: int) -> Dict[str, Any]:
        """Create a workflow node"""

        # Node type mappings
        node_configs = {
            "scheduleTrigger": {
                "name": "Schedule Trigger",
                "parameters": {"rule": {"interval": [{"field": "hours"}]}},
            },
            "httpRequest": {
                "name": "HTTP Request",
                "parameters": {"url": "http://localhost:8000/health", "method": "GET"},
            },
            "webhook": {
                "name": "Webhook",
                "parameters": {"path": "test-webhook", "httpMethod": "POST"},
            },
            "function": {
                "name": "Function",
                "parameters": {"functionCode": "return items;"},
            },
        }

        config = node_configs.get(
            node_type, {"name": f"{node_type.title()} Node", "parameters": {}}
        )

        return {
            "id": f"node{node_id}",
            "name": config["name"],
            "type": f"n8n-nodes-base.{node_type}",
            "typeVersion": 1,
            "position": [100 + (node_id - 1) * 200, 100],
            "parameters": config["parameters"],
        }
