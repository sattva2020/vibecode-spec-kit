"""
Main API for Intelligent n8n Workflow Creation System
FastAPI application that orchestrates the entire system
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import time

from ..core.config import get_config, setup_directories
from ..core.pipeline_coordinator import PipelineCoordinator, PipelineResult
from ..analyzers.project_analyzer import ProjectAnalyzer
from ..knowledge.lightrag_service import LightRAGService
from ..decision.ensemble_decision_engine import EnsembleDecisionEngine
from ..generator.workflow_generator import WorkflowGenerator


# Request/Response Models
class ProjectAnalysisRequest(BaseModel):
    """Request model for project analysis"""
    project_path: str = Field(..., description="Path to the project directory")
    user_id: Optional[str] = Field(None, description="Optional user identifier")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")


class WorkflowGenerationRequest(BaseModel):
    """Request model for workflow generation"""
    project_path: str = Field(..., description="Path to the project directory")
    user_id: Optional[str] = Field(None, description="Optional user identifier")
    preferences: Optional[Dict[str, Any]] = Field(None, description="User preferences")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")


class WorkflowGenerationResponse(BaseModel):
    """Response model for workflow generation"""
    success: bool
    request_id: str
    workflows: List[Dict[str, Any]]
    confidence: float
    execution_time: float
    message: str


class SystemStatusResponse(BaseModel):
    """Response model for system status"""
    status: str
    components: Dict[str, str]
    statistics: Dict[str, Any]
    uptime: float


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    timestamp: float
    version: str


# Initialize FastAPI app
app = FastAPI(
    title="Intelligent n8n Workflow Creation System",
    description="AI-powered system for automatically creating n8n workflows based on project analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
config = get_config()
pipeline_coordinator = None
system_start_time = time.time()

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.server.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@app.on_event("startup")
async def startup_event():
    """Initialize the system on startup"""
    global pipeline_coordinator
    
    logger.info("Starting Intelligent n8n Workflow Creation System")
    
    try:
        # Setup directories
        setup_directories(config)
        
        # Initialize components
        project_analyzer = ProjectAnalyzer()
        knowledge_service = LightRAGService()
        decision_engine = EnsembleDecisionEngine()
        workflow_generator = WorkflowGenerator()
        
        # Initialize pipeline coordinator
        pipeline_coordinator = PipelineCoordinator()
        
        # Set components in pipeline coordinator
        pipeline_coordinator.set_project_analyzer(project_analyzer)
        pipeline_coordinator.set_knowledge_service(knowledge_service)
        pipeline_coordinator.set_decision_engine(decision_engine)
        pipeline_coordinator.set_workflow_generator(workflow_generator)
        
        # Initialize knowledge service
        await knowledge_service.initialize_knowledge_base()
        
        # Initialize decision engine
        await decision_engine.initialize()
        
        logger.info("System initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize system: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Intelligent n8n Workflow Creation System")
    
    if pipeline_coordinator and pipeline_coordinator.knowledge_service:
        await pipeline_coordinator.knowledge_service.close()


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with basic information"""
    return HealthResponse(
        status="healthy",
        timestamp=time.time(),
        version="1.0.0"
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=time.time(),
        version="1.0.0"
    )


@app.get("/status", response_model=SystemStatusResponse)
async def get_system_status():
    """Get system status and statistics"""
    if not pipeline_coordinator:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    # Check component status
    components = {
        "pipeline_coordinator": "healthy",
        "project_analyzer": "healthy" if pipeline_coordinator.project_analyzer else "not_initialized",
        "knowledge_service": "healthy" if pipeline_coordinator.knowledge_service else "not_initialized",
        "decision_engine": "healthy" if pipeline_coordinator.decision_engine else "not_initialized",
        "workflow_generator": "healthy" if pipeline_coordinator.workflow_generator else "not_initialized"
    }
    
    # Get statistics
    statistics = {
        "uptime": time.time() - system_start_time,
        "active_contexts": len(pipeline_coordinator.active_contexts),
        "pipeline_state": pipeline_coordinator.state.value
    }
    
    # Add generator statistics if available
    if pipeline_coordinator.workflow_generator:
        statistics.update(pipeline_coordinator.workflow_generator.get_generation_stats())
    
    return SystemStatusResponse(
        status="healthy",
        components=components,
        statistics=statistics,
        uptime=time.time() - system_start_time
    )


@app.post("/api/analyze", response_model=Dict[str, Any])
async def analyze_project(request: ProjectAnalysisRequest):
    """Analyze a project and return analysis results"""
    if not pipeline_coordinator or not pipeline_coordinator.project_analyzer:
        raise HTTPException(status_code=503, detail="Project analyzer not available")
    
    try:
        project_path = Path(request.project_path)
        if not project_path.exists():
            raise HTTPException(status_code=400, detail="Project path does not exist")
        
        logger.info(f"Analyzing project: {project_path}")
        
        # Perform project analysis
        analysis = await pipeline_coordinator.project_analyzer.analyze_project(project_path)
        
        # Convert to dict for JSON response
        analysis_dict = {
            "project_path": analysis.project_path,
            "project_name": analysis.project_name,
            "languages": analysis.languages,
            "technologies": [
                {
                    "name": tech.name,
                    "version": tech.version,
                    "type": tech.type,
                    "confidence": tech.confidence,
                    "usage_patterns": tech.usage_patterns
                }
                for tech in analysis.technologies
            ],
            "architecture_type": analysis.architecture_type,
            "complexity_score": analysis.complexity_score,
            "automation_potential": analysis.automation_potential,
            "suggested_workflows": analysis.suggested_workflows,
            "structure_patterns": analysis.structure_patterns,
            "file_count": len(analysis.file_analyses),
            "analysis_timestamp": analysis.analysis_timestamp
        }
        
        return {
            "success": True,
            "analysis": analysis_dict,
            "message": "Project analysis completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Project analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/api/generate", response_model=WorkflowGenerationResponse)
async def generate_workflows(request: WorkflowGenerationRequest, background_tasks: BackgroundTasks):
    """Generate n8n workflows for a project"""
    if not pipeline_coordinator:
        raise HTTPException(status_code=503, detail="Pipeline coordinator not available")
    
    try:
        project_path = Path(request.project_path)
        if not project_path.exists():
            raise HTTPException(status_code=400, detail="Project path does not exist")
        
        request_id = f"req_{int(time.time() * 1000)}"
        
        logger.info(f"Generating workflows for project: {project_path} (request: {request_id})")
        
        # Execute the full pipeline
        result = await pipeline_coordinator.execute_pipeline(
            project_path=project_path,
            request_id=request_id,
            user_id=request.user_id,
            metadata=request.metadata
        )
        
        if result.success:
            # Convert workflows to dict format
            workflows_dict = []
            for workflow in result.workflows:
                if hasattr(workflow, '__dict__'):
                    workflows_dict.append(workflow.__dict__)
                else:
                    workflows_dict.append(workflow)
            
            return WorkflowGenerationResponse(
                success=True,
                request_id=request_id,
                workflows=workflows_dict,
                confidence=result.confidence_score,
                execution_time=result.execution_time,
                message="Workflows generated successfully"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Workflow generation failed: {result.error_message}"
            )
            
    except Exception as e:
        logger.error(f"Workflow generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@app.get("/api/pipeline/status/{request_id}")
async def get_pipeline_status(request_id: str):
    """Get status of a pipeline execution"""
    if not pipeline_coordinator:
        raise HTTPException(status_code=503, detail="Pipeline coordinator not available")
    
    status = pipeline_coordinator.get_pipeline_status(request_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Request not found")
    
    return status


@app.get("/api/workflows")
async def list_workflow_templates():
    """List available workflow templates and patterns"""
    if not pipeline_coordinator or not pipeline_coordinator.workflow_generator:
        raise HTTPException(status_code=503, detail="Workflow generator not available")
    
    generator = pipeline_coordinator.workflow_generator
    
    return {
        "node_templates": list(generator.node_templates.keys()),
        "workflow_patterns": list(generator.workflow_patterns.keys()),
        "generation_stats": generator.get_generation_stats()
    }


@app.post("/api/workflows/validate")
async def validate_workflow(workflow: Dict[str, Any]):
    """Validate a workflow structure"""
    if not pipeline_coordinator or not pipeline_coordinator.workflow_generator:
        raise HTTPException(status_code=503, detail="Workflow generator not available")
    
    try:
        generator = pipeline_coordinator.workflow_generator
        
        # Create a mock GeneratedWorkflow object for validation
        from ..generator.workflow_generator import GeneratedWorkflow, WorkflowStatus
        
        mock_workflow = GeneratedWorkflow(
            id=workflow.get("id", "mock_id"),
            name=workflow.get("name", "Mock Workflow"),
            description=workflow.get("description", ""),
            nodes=workflow.get("nodes", []),
            connections=workflow.get("connections", {}),
            settings=workflow.get("settings", {}),
            metadata=workflow.get("metadata", {}),
            status=WorkflowStatus.COMPLETED,
            confidence=1.0
        )
        
        is_valid, errors = await generator.validate_workflow(mock_workflow)
        
        return {
            "valid": is_valid,
            "errors": errors,
            "message": "Validation completed" if is_valid else "Validation failed"
        }
        
    except Exception as e:
        logger.error(f"Workflow validation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@app.get("/api/knowledge/nodes")
async def get_available_nodes():
    """Get available n8n nodes from knowledge base"""
    if not pipeline_coordinator or not pipeline_coordinator.knowledge_service:
        raise HTTPException(status_code=503, detail="Knowledge service not available")
    
    try:
        # Get mock workflow patterns for now
        patterns = await pipeline_coordinator.knowledge_service.get_workflow_patterns()
        
        return {
            "patterns": [
                {
                    "name": pattern.name,
                    "description": pattern.description,
                    "category": pattern.category,
                    "nodes": pattern.nodes,
                    "use_cases": pattern.use_cases,
                    "complexity": pattern.complexity
                }
                for pattern in patterns
            ],
            "total_count": len(patterns)
        }
        
    except Exception as e:
        logger.error(f"Failed to get available nodes: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get nodes: {str(e)}")


@app.get("/api/knowledge/nodes/{node_name}")
async def get_node_details(node_name: str):
    """Get detailed information about a specific node"""
    if not pipeline_coordinator or not pipeline_coordinator.knowledge_service:
        raise HTTPException(status_code=503, detail="Knowledge service not available")
    
    try:
        node_info = await pipeline_coordinator.knowledge_service.get_node_details(node_name)
        
        if not node_info:
            raise HTTPException(status_code=404, detail="Node not found")
        
        return {
            "name": node_info.name,
            "display_name": node_info.display_name,
            "description": node_info.description,
            "category": node_info.category,
            "version": node_info.version,
            "parameters": node_info.parameters,
            "outputs": node_info.outputs,
            "inputs": node_info.inputs,
            "documentation": node_info.documentation,
            "examples": node_info.examples,
            "tags": node_info.tags,
            "confidence": node_info.confidence
        }
        
    except Exception as e:
        logger.error(f"Failed to get node details: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get node details: {str(e)}")


def main():
    """Main entry point for the application"""
    logger.info("Starting Intelligent n8n Workflow Creation System API")
    
    uvicorn.run(
        "intelligent_n8n_system.src.api.main:app",
        host=config.server.host,
        port=config.server.port,
        reload=config.server.debug,
        log_level=config.server.log_level.lower()
    )


if __name__ == "__main__":
    main()
