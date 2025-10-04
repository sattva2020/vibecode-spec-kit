"""
Services module for Memory Bank CLI
"""

from .n8n_workflow_manager import (
    N8nWorkflowManager,
    create_rag_workflows,
    WorkflowType,
    WorkflowTemplate,
)

__all__ = [
    "N8nWorkflowManager",
    "create_rag_workflows",
    "WorkflowType",
    "WorkflowTemplate",
]
