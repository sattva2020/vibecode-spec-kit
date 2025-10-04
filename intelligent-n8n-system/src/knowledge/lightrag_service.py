"""
LightRAG Knowledge Service for Intelligent n8n Workflow Creation System
Integrates with LightRAG to provide n8n knowledge and semantic search
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import httpx
import json
from pathlib import Path

from ..core.config import get_config
from .documentation_loader import N8nDocumentationLoader
from ..analyzers.project_analyzer import ProjectAnalysis


@dataclass
class N8nNodeInfo:
    """Information about an n8n node"""

    name: str
    display_name: str
    description: str
    category: str
    version: str
    parameters: List[Dict[str, Any]]
    outputs: List[str]
    inputs: List[str]
    documentation: str
    examples: List[Dict[str, Any]]
    tags: List[str]
    confidence: float


@dataclass
class WorkflowPattern:
    """Information about a workflow pattern"""

    name: str
    description: str
    category: str
    nodes: List[str]
    connections: List[Dict[str, Any]]
    use_cases: List[str]
    complexity: str
    confidence: float


@dataclass
class KnowledgeQueryResult:
    """Result of a knowledge query"""

    nodes: List[N8nNodeInfo]
    patterns: List[WorkflowPattern]
    related_concepts: List[str]
    confidence: float
    query_time: float


class LightRAGService:
    """
    Service for interacting with LightRAG knowledge base
    Provides semantic search and knowledge retrieval for n8n
    """

    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        self.client = httpx.AsyncClient(timeout=30.0)
        self.base_url = self.config.lightrag.url

        # Knowledge base status
        self.knowledge_base_initialized = False
        self.n8n_docs_indexed = False

        # Cache for frequently accessed data
        self.node_cache = {}
        self.pattern_cache = {}

    async def initialize_knowledge_base(self) -> bool:
        """
        Initialize the LightRAG knowledge base with n8n documentation

        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            self.logger.info("Initializing LightRAG knowledge base for n8n")

            # Check if LightRAG is available
            if not await self._check_lightrag_health():
                self.logger.error("LightRAG service is not available")
                return False

            # Initialize n8n knowledge base if not already done
            if not self.n8n_docs_indexed:
                success = await self._index_n8n_documentation_with_loader()
                if not success:
                    self.logger.error("Failed to index n8n documentation")
                    return False

            self.knowledge_base_initialized = True
            self.logger.info("LightRAG knowledge base initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize knowledge base: {e}")
            return False

    async def _check_lightrag_health(self) -> bool:
        """Check if LightRAG service is healthy"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception:
            return False

    async def _index_n8n_documentation(self) -> bool:
        """
        Index n8n documentation in LightRAG
        This would typically involve:
        1. Fetching n8n documentation from various sources
        2. Processing and chunking the documentation
        3. Generating embeddings
        4. Storing in LightRAG knowledge base
        """
        try:
            # For now, we'll create a mock indexing process
            # In a real implementation, this would:
            # 1. Fetch n8n docs from GitHub, official docs, etc.
            # 2. Process node documentation
            # 3. Extract workflow examples
            # 4. Generate embeddings and store in LightRAG

            self.logger.info("Indexing n8n documentation...")

            # Mock indexing process
            n8n_docs = await self._fetch_n8n_documentation()

            for doc in n8n_docs:
                await self._add_document_to_lightrag(doc)

            self.n8n_docs_indexed = True
            self.logger.info(f"Successfully indexed {len(n8n_docs)} n8n documents")
            return True

        except Exception as e:
            self.logger.error(f"Failed to index n8n documentation: {e}")
            return False

    async def _index_n8n_documentation_with_loader(self) -> bool:
        """
        Index n8n documentation into LightRAG using DocumentationLoader
        
        Returns:
            bool: True if indexing successful, False otherwise
        """
        try:
            self.logger.info("Loading and indexing n8n documentation into LightRAG")
            
            # Use DocumentationLoader to load documentation
            async with N8nDocumentationLoader() as loader:
                # Load all documentation
                load_results = await loader.load_all_documentation()
                self.logger.info(f"Loaded {load_results['total_documents']} documents from {len(load_results['sources'])} sources")
                
                # Get documents ready for ingestion
                documents = await loader.get_documentation_for_ingestion()
                
                # Index each document into LightRAG
                indexed_count = 0
                for doc in documents:
                    try:
                        success = await self._add_document_to_lightrag(doc)
                        if success:
                            indexed_count += 1
                    except Exception as e:
                        self.logger.warning(f"Failed to index document '{doc.get('title', 'Unknown')}': {e}")
                
                self.n8n_docs_indexed = True
                self.logger.info(f"Successfully indexed {indexed_count}/{len(documents)} n8n documents")
                return indexed_count > 0
            
        except Exception as e:
            self.logger.error(f"Failed to index n8n documentation with loader: {e}")
            # Fallback to existing method
            return await self._index_n8n_documentation()

    async def _fetch_n8n_documentation(self) -> List[Dict[str, Any]]:
        """Fetch n8n documentation from various sources"""
        # This is a mock implementation
        # In reality, you would fetch from:
        # - n8n official documentation
        # - GitHub repositories
        # - Community examples
        # - API specifications

        return [
            {
                "title": "HTTP Request Node",
                "content": "The HTTP Request node allows you to make HTTP requests to external APIs...",
                "type": "node_documentation",
                "category": "core",
                "tags": ["http", "api", "request", "external"],
            },
            {
                "title": "Webhook Trigger",
                "content": "Webhook triggers allow n8n to receive data from external services...",
                "type": "node_documentation",
                "category": "trigger",
                "tags": ["webhook", "trigger", "incoming"],
            },
            {
                "title": "Data Processing Workflow",
                "content": "A common pattern for processing incoming data with validation and transformation...",
                "type": "workflow_pattern",
                "category": "data_processing",
                "tags": ["data", "processing", "validation", "transformation"],
            },
        ]

    async def _add_document_to_lightrag(self, doc: Dict[str, Any]) -> bool:
        """Add a document to LightRAG knowledge base"""
        try:
            # This would be the actual LightRAG API call
            # For now, we'll mock it

            payload = {
                "content": doc["content"],
                "title": doc["title"],
                "metadata": {
                    "type": doc["type"],
                    "category": doc.get("category", ""),
                    "tags": doc.get("tags", []),
                },
            }

            # Mock API call
            # response = await self.client.post(f"{self.base_url}/api/documents", json=payload)
            # return response.status_code in [200, 201]

            return True  # Mock success

        except Exception as e:
            self.logger.error(f"Failed to add document to LightRAG: {e}")
            return False

    async def query_relevant_knowledge(
        self, project_analysis: ProjectAnalysis
    ) -> Dict[str, Any]:
        """
        Query LightRAG for knowledge relevant to the project

        Args:
            project_analysis: Analysis of the project to find relevant knowledge for

        Returns:
            Dict containing relevant nodes, patterns, and concepts
        """
        try:
            self.logger.info("Querying relevant n8n knowledge for project")

            # Generate search queries based on project analysis
            queries = self._generate_search_queries(project_analysis)

            # Execute queries
            results = []
            for query in queries:
                result = await self._execute_semantic_query(query)
                if result:
                    results.append(result)

            # Combine and rank results
            combined_result = self._combine_query_results(results)

            self.logger.info(
                f"Found {len(combined_result.get('nodes', []))} relevant nodes, "
                f"{len(combined_result.get('patterns', []))} relevant patterns"
            )

            # Convert to KnowledgeQueryResult object
            return KnowledgeQueryResult(
                nodes=combined_result.get("nodes", []),
                patterns=combined_result.get("patterns", []),
                related_concepts=combined_result.get("related_concepts", []),
                confidence=combined_result.get("confidence", 0.0),
                query_time=time.time() - start_time,
            )

        except Exception as e:
            self.logger.error(f"Failed to query relevant knowledge: {e}")
            return KnowledgeQueryResult(
                nodes=[],
                patterns=[],
                related_concepts=[],
                confidence=0.0,
                query_time=0.0,
            )

    def _generate_search_queries(self, project_analysis: ProjectAnalysis) -> List[str]:
        """Generate search queries based on project analysis"""
        queries = []

        # Technology-based queries
        for tech in project_analysis.technologies:
            if tech.type == "database":
                queries.append(f"database integration {tech.name}")
            elif tech.type == "framework":
                queries.append(f"{tech.name} API integration")
            elif tech.type == "tool":
                queries.append(f"{tech.name} automation workflow")

        # Architecture-based queries
        if project_analysis.architecture_type:
            queries.append(
                f"{project_analysis.architecture_type} architecture workflow"
            )

        # Pattern-based queries
        for pattern in project_analysis.suggested_workflows:
            queries.append(f"{pattern} n8n workflow")

        # General queries based on project characteristics
        if project_analysis.complexity_score > 0.7:
            queries.append("complex project automation")

        if project_analysis.automation_potential > 0.5:
            queries.append("high automation potential workflow")

        return queries

    async def _execute_semantic_query(
        self, query: str
    ) -> Optional[KnowledgeQueryResult]:
        """Execute a semantic search query against LightRAG"""
        try:
            # This would be the actual LightRAG semantic search
            # For now, we'll mock the results

            payload = {"query": query, "limit": 10, "threshold": 0.7}

            # Mock API call
            # response = await self.client.post(f"{self.base_url}/api/search", json=payload)
            # if response.status_code != 200:
            #     return None

            # Mock response data
            mock_results = self._generate_mock_search_results(query)

            return KnowledgeQueryResult(
                nodes=mock_results["nodes"],
                patterns=mock_results["patterns"],
                related_concepts=mock_results["concepts"],
                confidence=mock_results["confidence"],
                query_time=0.1,  # Mock query time
            )

        except Exception as e:
            self.logger.error(f"Failed to execute semantic query '{query}': {e}")
            return None

    def _generate_mock_search_results(self, query: str) -> Dict[str, Any]:
        """Generate mock search results for testing"""
        query_lower = query.lower()

        nodes = []
        patterns = []
        concepts = []
        confidence = 0.8

        # Database-related queries
        if "database" in query_lower:
            nodes.append(
                N8nNodeInfo(
                    name="postgres",
                    display_name="PostgreSQL",
                    description="Execute queries on a PostgreSQL database",
                    category="database",
                    version="1.0.0",
                    parameters=[],
                    outputs=["items"],
                    inputs=["items"],
                    documentation="Connect to PostgreSQL databases",
                    examples=[],
                    tags=["database", "postgresql", "sql"],
                    confidence=0.9,
                )
            )
            concepts.extend(["database", "sql", "postgresql"])

        # API-related queries
        if "api" in query_lower:
            nodes.append(
                N8nNodeInfo(
                    name="httpRequest",
                    display_name="HTTP Request",
                    description="Make HTTP requests to external APIs",
                    category="core",
                    version="1.0.0",
                    parameters=[],
                    outputs=["items"],
                    inputs=["items"],
                    documentation="Make HTTP requests to external services",
                    examples=[],
                    tags=["http", "api", "request"],
                    confidence=0.95,
                )
            )
            concepts.extend(["api", "http", "request"])

        # Automation queries
        if "automation" in query_lower or "workflow" in query_lower:
            patterns.append(
                WorkflowPattern(
                    name="Data Processing Pipeline",
                    description="Process incoming data with validation and transformation",
                    category="data_processing",
                    nodes=["webhook", "function", "httpRequest"],
                    connections=[],
                    use_cases=[
                        "API data processing",
                        "Data validation",
                        "Data transformation",
                    ],
                    complexity="medium",
                    confidence=0.85,
                )
            )
            concepts.extend(["automation", "pipeline", "processing"])

        return {
            "nodes": nodes,
            "patterns": patterns,
            "concepts": concepts,
            "confidence": confidence,
        }

    def _combine_query_results(
        self, results: List[KnowledgeQueryResult]
    ) -> Dict[str, Any]:
        """Combine multiple query results and remove duplicates"""
        all_nodes = {}
        all_patterns = {}
        all_concepts = set()
        total_confidence = 0.0

        for result in results:
            # Combine nodes (deduplicate by name)
            for node in result.nodes:
                if (
                    node.name not in all_nodes
                    or node.confidence > all_nodes[node.name].confidence
                ):
                    all_nodes[node.name] = node

            # Combine patterns (deduplicate by name)
            for pattern in result.patterns:
                if (
                    pattern.name not in all_patterns
                    or pattern.confidence > all_patterns[pattern.name].confidence
                ):
                    all_patterns[pattern.name] = pattern

            # Combine concepts
            all_concepts.update(result.related_concepts)

            # Average confidence
            total_confidence += result.confidence

        avg_confidence = total_confidence / len(results) if results else 0.0

        return {
            "nodes": list(all_nodes.values()),
            "patterns": list(all_patterns.values()),
            "related_concepts": list(all_concepts),
            "confidence": avg_confidence,
        }

    async def get_node_details(self, node_name: str) -> Optional[N8nNodeInfo]:
        """Get detailed information about a specific n8n node"""
        try:
            # Check cache first
            if node_name in self.node_cache:
                return self.node_cache[node_name]

            # Query LightRAG for node details
            # This would be the actual API call
            # For now, we'll return mock data

            mock_node = self._get_mock_node_details(node_name)

            if mock_node:
                self.node_cache[node_name] = mock_node

            return mock_node

        except Exception as e:
            self.logger.error(f"Failed to get node details for {node_name}: {e}")
            return None

    def _get_mock_node_details(self, node_name: str) -> Optional[N8nNodeInfo]:
        """Get mock node details for testing"""
        mock_nodes = {
            "httpRequest": N8nNodeInfo(
                name="httpRequest",
                display_name="HTTP Request",
                description="Make HTTP requests to external APIs and services",
                category="core",
                version="1.0.0",
                parameters=[
                    {"name": "url", "type": "string", "required": True},
                    {"name": "method", "type": "string", "default": "GET"},
                    {"name": "headers", "type": "object", "required": False},
                ],
                outputs=["items"],
                inputs=["items"],
                documentation="The HTTP Request node allows you to make HTTP requests...",
                examples=[
                    {"title": "GET Request", "description": "Make a simple GET request"}
                ],
                tags=["http", "api", "request", "external"],
                confidence=1.0,
            ),
            "webhook": N8nNodeInfo(
                name="webhook",
                display_name="Webhook",
                description="Receive data from external services via webhook",
                category="trigger",
                version="1.0.0",
                parameters=[
                    {"name": "path", "type": "string", "required": True},
                    {"name": "httpMethod", "type": "string", "default": "POST"},
                ],
                outputs=["items"],
                inputs=[],
                documentation="Webhook nodes allow n8n to receive data from external services...",
                examples=[
                    {
                        "title": "Basic Webhook",
                        "description": "Set up a basic webhook endpoint",
                    }
                ],
                tags=["webhook", "trigger", "incoming", "api"],
                confidence=1.0,
            ),
        }

        return mock_nodes.get(node_name)

    async def get_workflow_patterns(
        self, category: Optional[str] = None
    ) -> List[WorkflowPattern]:
        """Get workflow patterns, optionally filtered by category"""
        try:
            # Check cache first
            cache_key = f"patterns_{category or 'all'}"
            if cache_key in self.pattern_cache:
                return self.pattern_cache[cache_key]

            # Query LightRAG for patterns
            # This would be the actual API call
            # For now, we'll return mock data

            mock_patterns = self._get_mock_workflow_patterns(category)

            # Cache the results
            self.pattern_cache[cache_key] = mock_patterns

            return mock_patterns

        except Exception as e:
            self.logger.error(f"Failed to get workflow patterns: {e}")
            return []

    def _get_mock_workflow_patterns(
        self, category: Optional[str] = None
    ) -> List[WorkflowPattern]:
        """Get mock workflow patterns for testing"""
        all_patterns = [
            WorkflowPattern(
                name="Data Processing Pipeline",
                description="Process incoming data with validation and transformation",
                category="data_processing",
                nodes=["webhook", "function", "httpRequest"],
                connections=[
                    {"from": "webhook", "to": "function"},
                    {"from": "function", "to": "httpRequest"},
                ],
                use_cases=[
                    "API data processing",
                    "Data validation",
                    "Data transformation",
                ],
                complexity="medium",
                confidence=0.9,
            ),
            WorkflowPattern(
                name="API Integration Workflow",
                description="Integrate with external APIs for data exchange",
                category="api_integration",
                nodes=["schedule", "httpRequest", "function"],
                connections=[
                    {"from": "schedule", "to": "httpRequest"},
                    {"from": "httpRequest", "to": "function"},
                ],
                use_cases=[
                    "Scheduled API calls",
                    "Data synchronization",
                    "External service integration",
                ],
                complexity="low",
                confidence=0.85,
            ),
            WorkflowPattern(
                name="Notification System",
                description="Send notifications based on triggers",
                category="notifications",
                nodes=["webhook", "function", "email", "slack"],
                connections=[
                    {"from": "webhook", "to": "function"},
                    {"from": "function", "to": "email"},
                    {"from": "function", "to": "slack"},
                ],
                use_cases=[
                    "Alert systems",
                    "Status notifications",
                    "Event-driven messaging",
                ],
                complexity="medium",
                confidence=0.8,
            ),
        ]

        if category:
            return [pattern for pattern in all_patterns if pattern.category == category]

        return all_patterns

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
