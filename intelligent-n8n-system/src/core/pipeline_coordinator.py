"""
Pipeline Coordinator for Intelligent n8n Workflow Creation System
Central orchestrator that manages the AI pipeline workflow
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass
from pathlib import Path
import time

from .config import get_config


class PipelineState(Enum):
    """Pipeline execution states"""

    IDLE = "idle"
    ANALYZING_PROJECT = "analyzing_project"
    QUERYING_KNOWLEDGE = "querying_knowledge"
    MAKING_DECISIONS = "making_decisions"
    GENERATING_WORKFLOWS = "generating_workflows"
    VALIDATING_OUTPUT = "validating_output"
    COMPLETED = "completed"
    ERROR = "error"


class PipelineStage(Enum):
    """Pipeline stages"""

    PROJECT_ANALYSIS = "project_analysis"
    KNOWLEDGE_QUERY = "knowledge_query"
    DECISION_MAKING = "decision_making"
    WORKFLOW_GENERATION = "workflow_generation"
    VALIDATION = "validation"


@dataclass
class PipelineContext:
    """Context for pipeline execution"""

    project_path: Path
    request_id: str
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    start_time: float = None
    current_stage: PipelineStage = None
    stage_results: Dict[PipelineStage, Any] = None
    errors: List[str] = None

    def __post_init__(self):
        if self.start_time is None:
            self.start_time = time.time()
        if self.stage_results is None:
            self.stage_results = {}
        if self.errors is None:
            self.errors = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class PipelineResult:
    """Result of pipeline execution"""

    success: bool
    workflows: List[Dict[str, Any]]
    context: PipelineContext
    execution_time: float
    error_message: Optional[str] = None
    confidence_score: float = 0.0


class PipelineCoordinator:
    """
    Central coordinator for the AI pipeline workflow
    Manages state, error handling, and stage orchestration
    """

    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        self.state = PipelineState.IDLE
        self.active_contexts: Dict[str, PipelineContext] = {}

        # Stage processors (will be injected)
        self.project_analyzer = None
        self.knowledge_service = None
        self.decision_engine = None
        self.workflow_generator = None
        self.validator = None

        # Error handling
        self.max_retries = 3
        self.retry_delay = 1.0

    async def execute_pipeline(
        self,
        project_path: Path,
        request_id: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> PipelineResult:
        """
        Execute the complete AI pipeline for workflow generation

        Args:
            project_path: Path to the project to analyze
            request_id: Unique request identifier
            user_id: Optional user identifier
            metadata: Optional metadata for the request

        Returns:
            PipelineResult with generated workflows or error information
        """
        context = PipelineContext(
            project_path=project_path,
            request_id=request_id,
            user_id=user_id,
            metadata=metadata or {},
        )

        self.active_contexts[request_id] = context
        self.state = PipelineState.ANALYZING_PROJECT

        try:
            self.logger.info(f"Starting pipeline execution for request {request_id}")

            # Stage 1: Project Analysis
            await self._execute_stage(
                context, PipelineStage.PROJECT_ANALYSIS, self._analyze_project
            )

            # Stage 2: Knowledge Query
            await self._execute_stage(
                context, PipelineStage.KNOWLEDGE_QUERY, self._query_knowledge
            )

            # Stage 3: Decision Making
            await self._execute_stage(
                context, PipelineStage.DECISION_MAKING, self._make_decisions
            )

            # Stage 4: Workflow Generation
            await self._execute_stage(
                context, PipelineStage.WORKFLOW_GENERATION, self._generate_workflows
            )

            # Stage 5: Validation
            await self._execute_stage(
                context, PipelineStage.VALIDATION, self._validate_output
            )

            self.state = PipelineState.COMPLETED
            execution_time = time.time() - context.start_time

            result = PipelineResult(
                success=True,
                workflows=context.stage_results.get(
                    PipelineStage.WORKFLOW_GENERATION, []
                ),
                context=context,
                execution_time=execution_time,
                confidence_score=self._calculate_confidence_score(context),
            )

            self.logger.info(
                f"Pipeline completed successfully for request {request_id} in {execution_time:.2f}s"
            )
            return result

        except Exception as e:
            self.state = PipelineState.ERROR
            execution_time = time.time() - context.start_time

            self.logger.error(f"Pipeline failed for request {request_id}: {str(e)}")
            context.errors.append(str(e))

            return PipelineResult(
                success=False,
                workflows=[],
                context=context,
                execution_time=execution_time,
                error_message=str(e),
            )

        finally:
            # Cleanup
            if request_id in self.active_contexts:
                del self.active_contexts[request_id]

    async def _execute_stage(
        self, context: PipelineContext, stage: PipelineStage, stage_function
    ) -> Any:
        """Execute a pipeline stage with error handling and retries"""
        context.current_stage = stage

        for attempt in range(self.max_retries):
            try:
                self.logger.info(
                    f"Executing stage {stage.value} (attempt {attempt + 1})"
                )

                # Update pipeline state based on stage
                if stage == PipelineStage.PROJECT_ANALYSIS:
                    self.state = PipelineState.ANALYZING_PROJECT
                elif stage == PipelineStage.KNOWLEDGE_QUERY:
                    self.state = PipelineState.QUERYING_KNOWLEDGE
                elif stage == PipelineStage.DECISION_MAKING:
                    self.state = PipelineState.MAKING_DECISIONS
                elif stage == PipelineStage.WORKFLOW_GENERATION:
                    self.state = PipelineState.GENERATING_WORKFLOWS
                elif stage == PipelineStage.VALIDATION:
                    self.state = PipelineState.VALIDATING_OUTPUT

                result = await stage_function(context)
                context.stage_results[stage] = result

                self.logger.info(f"Stage {stage.value} completed successfully")
                return result

            except Exception as e:
                self.logger.warning(
                    f"Stage {stage.value} failed (attempt {attempt + 1}): {str(e)}"
                )

                if attempt == self.max_retries - 1:
                    raise e

                await asyncio.sleep(self.retry_delay * (attempt + 1))

    async def _analyze_project(self, context: PipelineContext) -> Dict[str, Any]:
        """Stage 1: Analyze project structure and context"""
        if not self.project_analyzer:
            raise RuntimeError("Project analyzer not initialized")

        return await self.project_analyzer.analyze_project(context.project_path)

    async def _query_knowledge(self, context: PipelineContext):
        """Stage 2: Query knowledge base for relevant n8n information"""
        if not self.knowledge_service:
            raise RuntimeError("Knowledge service not initialized")

        project_analysis = context.stage_results[PipelineStage.PROJECT_ANALYSIS]
        return await self.knowledge_service.query_relevant_knowledge(project_analysis)

    async def _make_decisions(self, context: PipelineContext) -> Dict[str, Any]:
        """Stage 3: Make decisions about which workflows to create"""
        if not self.decision_engine:
            raise RuntimeError("Decision engine not initialized")

        project_analysis = context.stage_results[PipelineStage.PROJECT_ANALYSIS]
        knowledge_data = context.stage_results[PipelineStage.KNOWLEDGE_QUERY]

        return await self.decision_engine.make_decisions(
            project_analysis, knowledge_data
        )

    async def _generate_workflows(
        self, context: PipelineContext
    ) -> List[Dict[str, Any]]:
        """Stage 4: Generate n8n workflows based on decisions"""
        if not self.workflow_generator:
            raise RuntimeError("Workflow generator not initialized")

        decisions = context.stage_results[PipelineStage.DECISION_MAKING]
        project_analysis = context.stage_results[PipelineStage.PROJECT_ANALYSIS]

        return await self.workflow_generator.generate_workflows(
            decisions, project_analysis
        )

    async def _validate_output(self, context: PipelineContext) -> Dict[str, Any]:
        """Stage 5: Validate generated workflows"""
        if not self.validator:
            raise RuntimeError("Validator not initialized")

        workflows = context.stage_results[PipelineStage.WORKFLOW_GENERATION]

        return await self.validator.validate_workflows(workflows)

    def _calculate_confidence_score(self, context: PipelineContext) -> float:
        """Calculate overall confidence score for the pipeline result"""
        # Simple confidence calculation based on stage success and data quality
        base_score = 1.0

        # Reduce score for errors
        error_penalty = len(context.errors) * 0.1

        # Check stage results quality
        stage_penalty = 0.0
        for stage, result in context.stage_results.items():
            if not result:
                stage_penalty += 0.2
            elif isinstance(result, dict) and result.get("confidence", 1.0) < 0.8:
                stage_penalty += 0.1

        confidence = max(0.0, base_score - error_penalty - stage_penalty)
        return round(confidence, 2)

    def get_pipeline_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a pipeline execution"""
        if request_id not in self.active_contexts:
            return None

        context = self.active_contexts[request_id]
        elapsed_time = time.time() - context.start_time

        return {
            "request_id": request_id,
            "state": self.state.value,
            "current_stage": context.current_stage.value
            if context.current_stage
            else None,
            "elapsed_time": elapsed_time,
            "errors": context.errors,
            "completed_stages": list(context.stage_results.keys()),
            "progress": len(context.stage_results) / len(PipelineStage) * 100,
        }

    def set_project_analyzer(self, analyzer):
        """Set the project analyzer instance"""
        self.project_analyzer = analyzer

    def set_knowledge_service(self, service):
        """Set the knowledge service instance"""
        self.knowledge_service = service

    def set_decision_engine(self, engine):
        """Set the decision engine instance"""
        self.decision_engine = engine

    def set_workflow_generator(self, generator):
        """Set the workflow generator instance"""
        self.workflow_generator = generator

    def set_validator(self, validator):
        """Set the validator instance"""
        self.validator = validator
