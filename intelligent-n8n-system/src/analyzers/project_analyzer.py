"""
Project Context Analyzer for Intelligent n8n Workflow Creation System
Analyzes project structure, technologies, and patterns to understand context
"""

import os
import ast
import json
import yaml
import logging
from typing import Dict, Any, List, Optional, Set, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import asyncio
import aiofiles

from ..core.config import get_config


@dataclass
class FileAnalysis:
    """Analysis result for a single file"""

    path: str
    language: str
    size: int
    complexity: float
    functions: List[str]
    classes: List[str]
    imports: List[str]
    patterns: List[str]
    metadata: Dict[str, Any]


@dataclass
class TechnologyInfo:
    """Information about detected technology"""

    name: str
    version: Optional[str]
    type: str  # framework, library, tool, language
    confidence: float
    usage_patterns: List[str]
    metadata: Dict[str, Any]


@dataclass
class ProjectAnalysis:
    """Complete project analysis result"""

    project_path: str
    project_name: str
    languages: Dict[str, int]
    technologies: List[TechnologyInfo]
    file_analyses: List[FileAnalysis]
    structure_patterns: List[str]
    architecture_type: Optional[str]
    complexity_score: float
    automation_potential: float
    suggested_workflows: List[str]
    metadata: Dict[str, Any]
    analysis_timestamp: float


class ProjectAnalyzer:
    """
    Analyzes project structure and context to understand:
    - Technologies and frameworks used
    - Code patterns and architecture
    - Automation opportunities
    - Integration points
    """

    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)

        # Supported file patterns
        self.language_patterns = {
            "python": [".py"],
            "javascript": [".js", ".mjs"],
            "typescript": [".ts", ".tsx"],
            "json": [".json"],
            "yaml": [".yaml", ".yml"],
            "markdown": [".md"],
            "shell": [".sh", ".bash"],
            "powershell": [".ps1"],
            "docker": ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"],
            "git": [".gitignore", ".gitattributes"],
        }

        # Technology detection patterns
        self.technology_patterns = {
            "fastapi": {
                "patterns": ["fastapi", "FastAPI", "from fastapi import"],
                "files": ["requirements.txt", "pyproject.toml"],
                "type": "framework",
            },
            "django": {
                "patterns": ["django", "Django", "from django import"],
                "files": ["manage.py", "requirements.txt"],
                "type": "framework",
            },
            "flask": {
                "patterns": ["flask", "Flask", "from flask import"],
                "files": ["requirements.txt", "pyproject.toml"],
                "type": "framework",
            },
            "react": {
                "patterns": ["react", "React", "from react import"],
                "files": ["package.json"],
                "type": "framework",
            },
            "vue": {
                "patterns": ["vue", "Vue", "from vue import"],
                "files": ["package.json", "vue.config.js"],
                "type": "framework",
            },
            "nodejs": {
                "patterns": ["node", "npm", "yarn"],
                "files": ["package.json", "package-lock.json"],
                "type": "runtime",
            },
            "docker": {
                "patterns": ["docker", "FROM", "RUN", "COPY"],
                "files": ["Dockerfile", "docker-compose.yml"],
                "type": "tool",
            },
            "postgresql": {
                "patterns": ["postgresql", "postgres", "psycopg2", "asyncpg"],
                "files": ["requirements.txt", "package.json"],
                "type": "database",
            },
            "redis": {
                "patterns": ["redis", "Redis"],
                "files": ["requirements.txt", "package.json"],
                "type": "database",
            },
            "mongodb": {
                "patterns": ["mongodb", "mongo", "pymongo", "mongoose"],
                "files": ["requirements.txt", "package.json"],
                "type": "database",
            },
            "supabase": {
                "patterns": ["supabase", "Supabase", "@supabase"],
                "files": ["package.json", "requirements.txt"],
                "type": "platform",
            },
            "n8n": {
                "patterns": ["n8n", "n8n.io"],
                "files": ["package.json", "docker-compose.yml"],
                "type": "tool",
            },
        }

        # Architecture patterns
        self.architecture_patterns = {
            "microservices": ["docker-compose", "kubernetes", "service", "api"],
            "monolith": ["single", "main.py", "app.py", "index.js"],
            "serverless": ["lambda", "vercel", "netlify", "functions"],
            "spa": ["public", "src", "components", "pages"],
            "api": ["api", "endpoints", "routes", "controllers"],
        }

    async def analyze_project(self, project_path: Path) -> ProjectAnalysis:
        """
        Perform comprehensive project analysis

        Args:
            project_path: Path to the project directory

        Returns:
            ProjectAnalysis with detailed project information
        """
        self.logger.info(f"Starting project analysis for {project_path}")

        # Get all files in the project
        files = await self._get_project_files(project_path)

        # Analyze individual files
        file_analyses = await self._analyze_files(files)

        # Detect technologies
        technologies = await self._detect_technologies(files)

        # Analyze project structure
        structure_patterns = self._analyze_structure(project_path, files)

        # Determine architecture type
        architecture_type = self._detect_architecture_type(
            technologies, structure_patterns
        )

        # Calculate complexity score
        complexity_score = self._calculate_complexity_score(file_analyses, technologies)

        # Assess automation potential
        automation_potential = self._assess_automation_potential(
            technologies, structure_patterns
        )

        # Suggest potential workflows
        suggested_workflows = self._suggest_workflows(
            technologies, architecture_type, automation_potential
        )

        # Count languages
        languages = Counter([analysis.language for analysis in file_analyses])

        analysis = ProjectAnalysis(
            project_path=str(project_path),
            project_name=project_path.name,
            languages=dict(languages),
            technologies=technologies,
            file_analyses=file_analyses,
            structure_patterns=structure_patterns,
            architecture_type=architecture_type,
            complexity_score=complexity_score,
            automation_potential=automation_potential,
            suggested_workflows=suggested_workflows,
            metadata={
                "total_files": len(files),
                "total_size": sum(analysis.size for analysis in file_analyses),
                "config": self.config.model_dump()
                if hasattr(self.config, "model_dump")
                else str(self.config),
            },
            analysis_timestamp=float(os.path.getctime(project_path)),
        )

        self.logger.info(
            f"Project analysis completed: {len(technologies)} technologies, "
            f"{len(file_analyses)} files, complexity: {complexity_score:.2f}"
        )

        return analysis

    async def _get_project_files(self, project_path: Path) -> List[Path]:
        """Get all relevant files in the project"""
        files = []
        supported_extensions = self.config.file_processing.supported_extensions_list

        for root, dirs, filenames in os.walk(project_path):
            # Skip hidden directories and common build/cache directories
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".")
                and d
                not in [
                    "node_modules",
                    "__pycache__",
                    "venv",
                    "env",
                    "build",
                    "dist",
                    "target",
                ]
            ]

            for filename in filenames:
                if filename.startswith("."):
                    continue

                file_path = Path(root) / filename

                # Check if file extension is supported or if it's a special file
                if (
                    file_path.suffix.lower() in supported_extensions
                    or filename in self.language_patterns.get("docker", [])
                    or filename in self.language_patterns.get("git", [])
                ):
                    # Check file size limit
                    try:
                        if (
                            file_path.stat().st_size
                            <= self.config.file_processing.max_file_size
                        ):
                            files.append(file_path)
                    except (OSError, PermissionError):
                        continue

        return files

    async def _analyze_files(self, files: List[Path]) -> List[FileAnalysis]:
        """Analyze individual files"""
        analyses = []

        # Process files concurrently (with limit)
        semaphore = asyncio.Semaphore(self.config.performance.max_concurrent_analyses)

        async def analyze_single_file(file_path: Path) -> Optional[FileAnalysis]:
            async with semaphore:
                try:
                    return await self._analyze_single_file(file_path)
                except Exception as e:
                    self.logger.warning(f"Failed to analyze file {file_path}: {e}")
                    return None

        tasks = [analyze_single_file(file_path) for file_path in files]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out None results and exceptions
        for result in results:
            if isinstance(result, FileAnalysis):
                analyses.append(result)

        return analyses

    async def _analyze_single_file(self, file_path: Path) -> FileAnalysis:
        """Analyze a single file"""
        language = self._detect_language(file_path)
        size = file_path.stat().st_size

        functions = []
        classes = []
        imports = []
        patterns = []
        complexity = 0.0

        try:
            content = await self._read_file_content(file_path)

            if language == "python":
                functions, classes, imports, complexity = self._analyze_python_file(
                    content
                )
            elif language in ["javascript", "typescript"]:
                functions, classes, imports, complexity = self._analyze_js_file(content)
            elif language == "json":
                patterns = self._analyze_json_file(content)
            elif language == "yaml":
                patterns = self._analyze_yaml_file(content)

            # Detect general patterns
            patterns.extend(self._detect_general_patterns(content))

        except Exception as e:
            self.logger.warning(f"Error analyzing file {file_path}: {e}")

        return FileAnalysis(
            path=str(file_path),
            language=language,
            size=size,
            complexity=complexity,
            functions=functions,
            classes=classes,
            imports=imports,
            patterns=patterns,
            metadata={
                "readable": True,
                "lines": len(content.split("\n")) if "content" in locals() else 0,
            },
        )

    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file path"""
        suffix = file_path.suffix.lower()
        filename = file_path.name.lower()

        for language, patterns in self.language_patterns.items():
            if suffix in patterns or filename in patterns:
                return language

        return "unknown"

    async def _read_file_content(self, file_path: Path) -> str:
        """Read file content with encoding detection"""
        try:
            async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                return await f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            async with aiofiles.open(file_path, "r", encoding="latin-1") as f:
                return await f.read()

    def _analyze_python_file(
        self, content: str
    ) -> Tuple[List[str], List[str], List[str], float]:
        """Analyze Python file content"""
        try:
            tree = ast.parse(content)

            functions = []
            classes = []
            imports = []
            complexity = 0

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                    complexity += self._calculate_function_complexity(node)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                    complexity += len(node.body) * 2  # Class complexity
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        imports.extend([alias.name for alias in node.names])
                    else:
                        imports.append(node.module or "")

            return functions, classes, imports, complexity

        except SyntaxError:
            return [], [], [], 0.0

    def _analyze_js_file(
        self, content: str
    ) -> Tuple[List[str], List[str], List[str], float]:
        """Analyze JavaScript/TypeScript file content"""
        functions = []
        classes = []
        imports = []
        complexity = 0

        lines = content.split("\n")

        for line in lines:
            line = line.strip()

            # Function detection
            if "function " in line or "=>" in line:
                if "function" in line:
                    func_name = line.split("function")[1].split("(")[0].strip()
                    if func_name:
                        functions.append(func_name)
                complexity += 1

            # Class detection
            elif "class " in line:
                class_name = line.split("class")[1].split(" ")[0].strip()
                if class_name:
                    classes.append(class_name)
                complexity += 2

            # Import detection
            elif line.startswith("import ") or line.startswith("require("):
                imports.append(line)

        return functions, classes, imports, complexity

    def _analyze_json_file(self, content: str) -> List[str]:
        """Analyze JSON file content"""
        patterns = []
        try:
            data = json.loads(content)

            # Common JSON patterns
            if isinstance(data, dict):
                if "scripts" in data:
                    patterns.append("package_scripts")
                if "dependencies" in data:
                    patterns.append("dependencies")
                if "devDependencies" in data:
                    patterns.append("dev_dependencies")
                if "name" in data:
                    patterns.append("package_manifest")

        except json.JSONDecodeError:
            pass

        return patterns

    def _analyze_yaml_file(self, content: str) -> List[str]:
        """Analyze YAML file content"""
        patterns = []
        try:
            data = yaml.safe_load(content)

            if isinstance(data, dict):
                if "services" in data:
                    patterns.append("docker_compose")
                if "version" in data and "services" in data:
                    patterns.append("container_orchestration")
                if "name" in data and "tasks" in data:
                    patterns.append("workflow_definition")

        except yaml.YAMLError:
            pass

        return patterns

    def _detect_general_patterns(self, content: str) -> List[str]:
        """Detect general patterns in file content"""
        patterns = []
        content_lower = content.lower()

        # API patterns
        if any(
            keyword in content_lower
            for keyword in ["api", "endpoint", "route", "controller"]
        ):
            patterns.append("api_related")

        # Database patterns
        if any(
            keyword in content_lower
            for keyword in ["database", "db", "sql", "query", "model"]
        ):
            patterns.append("database_related")

        # Authentication patterns
        if any(
            keyword in content_lower
            for keyword in ["auth", "login", "token", "jwt", "oauth"]
        ):
            patterns.append("authentication")

        # Testing patterns
        if any(
            keyword in content_lower for keyword in ["test", "spec", "mock", "assert"]
        ):
            patterns.append("testing")

        # CI/CD patterns
        if any(
            keyword in content_lower
            for keyword in ["ci", "cd", "pipeline", "deploy", "build"]
        ):
            patterns.append("cicd")

        return patterns

    def _calculate_function_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity for a function"""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(
                child, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.ExceptHandler)
            ):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity

    async def _detect_technologies(self, files: List[Path]) -> List[TechnologyInfo]:
        """Detect technologies used in the project"""
        technologies = []

        for file_path in files:
            try:
                content = await self._read_file_content(file_path)
                file_name = file_path.name.lower()

                for tech_name, tech_info in self.technology_patterns.items():
                    confidence = 0.0
                    usage_patterns = []

                    # Check file patterns
                    if file_name in tech_info["files"]:
                        confidence += 0.5
                        usage_patterns.append(f"config_file:{file_name}")

                    # Check content patterns
                    for pattern in tech_info["patterns"]:
                        if pattern.lower() in content.lower():
                            confidence += 0.3
                            usage_patterns.append(f"content_pattern:{pattern}")

                    # If confidence is high enough, add technology
                    if confidence >= 0.3:
                        # Check if technology already exists
                        existing_tech = next(
                            (t for t in technologies if t.name == tech_name), None
                        )

                        if existing_tech:
                            existing_tech.confidence = max(
                                existing_tech.confidence, confidence
                            )
                            existing_tech.usage_patterns.extend(usage_patterns)
                        else:
                            technologies.append(
                                TechnologyInfo(
                                    name=tech_name,
                                    version=None,  # TODO: Extract version from content
                                    type=tech_info["type"],
                                    confidence=confidence,
                                    usage_patterns=usage_patterns,
                                    metadata={"detected_in": str(file_path)},
                                )
                            )

            except Exception as e:
                self.logger.warning(f"Error detecting technologies in {file_path}: {e}")
                continue

        # Remove duplicates and sort by confidence
        unique_technologies = {}
        for tech in technologies:
            if (
                tech.name not in unique_technologies
                or tech.confidence > unique_technologies[tech.name].confidence
            ):
                unique_technologies[tech.name] = tech

        return sorted(
            unique_technologies.values(), key=lambda x: x.confidence, reverse=True
        )

    def _analyze_structure(self, project_path: Path, files: List[Path]) -> List[str]:
        """Analyze project structure patterns"""
        patterns = []

        # Common directory patterns
        dirs = set()
        for file_path in files:
            if file_path.parent != project_path:
                dirs.add(file_path.parent)

        dir_names = [d.name.lower() for d in dirs]

        # Structure patterns
        if "src" in dir_names or "source" in dir_names:
            patterns.append("src_based_structure")

        if "tests" in dir_names or "test" in dir_names:
            patterns.append("separate_test_directory")

        if "docs" in dir_names or "documentation" in dir_names:
            patterns.append("documentation_present")

        if "config" in dir_names or "configuration" in dir_names:
            patterns.append("config_management")

        if "scripts" in dir_names:
            patterns.append("automation_scripts")

        # File count patterns
        if len(files) > 100:
            patterns.append("large_project")
        elif len(files) < 10:
            patterns.append("small_project")

        return patterns

    def _detect_architecture_type(
        self, technologies: List[TechnologyInfo], structure_patterns: List[str]
    ) -> Optional[str]:
        """Detect the architecture type of the project"""
        tech_names = [tech.name for tech in technologies]

        # Check for microservices indicators
        if (
            any(pattern in tech_names for pattern in ["docker", "kubernetes"])
            or "docker_compose" in structure_patterns
        ):
            return "microservices"

        # Check for serverless indicators
        if any(pattern in tech_names for pattern in ["lambda", "vercel", "netlify"]):
            return "serverless"

        # Check for SPA indicators
        if any(pattern in tech_names for pattern in ["react", "vue", "angular"]):
            return "spa"

        # Check for API indicators
        if (
            any(pattern in tech_names for pattern in ["fastapi", "django", "flask"])
            or "api_related" in structure_patterns
        ):
            return "api"

        # Check for monolith indicators
        if "src_based_structure" in structure_patterns and len(tech_names) > 3:
            return "monolith"

        return None

    def _calculate_complexity_score(
        self, file_analyses: List[FileAnalysis], technologies: List[TechnologyInfo]
    ) -> float:
        """Calculate overall project complexity score (0.0 - 1.0)"""
        if not file_analyses:
            return 0.0

        # File complexity component
        total_complexity = sum(analysis.complexity for analysis in file_analyses)
        max_file_complexity = max(analysis.complexity for analysis in file_analyses)
        file_complexity_score = min(1.0, (total_complexity / len(file_analyses)) / 10.0)

        # Technology complexity component
        tech_complexity_score = min(1.0, len(technologies) / 10.0)

        # Size complexity component
        total_size = sum(analysis.size for analysis in file_analyses)
        size_complexity_score = min(1.0, total_size / (1024 * 1024))  # MB

        # Weighted average
        complexity = (
            file_complexity_score * 0.4
            + tech_complexity_score * 0.3
            + size_complexity_score * 0.3
        )

        return round(complexity, 2)

    def _assess_automation_potential(
        self, technologies: List[TechnologyInfo], structure_patterns: List[str]
    ) -> float:
        """Assess automation potential (0.0 - 1.0)"""
        potential = 0.0

        # Technology-based potential
        automation_techs = ["docker", "n8n", "github", "gitlab", "jenkins", "ci"]
        tech_names = [tech.name for tech in technologies]

        for tech in automation_techs:
            if tech in tech_names:
                potential += 0.2

        # Structure-based potential
        if "automation_scripts" in structure_patterns:
            potential += 0.2

        if "config_management" in structure_patterns:
            potential += 0.1

        if "cicd" in structure_patterns:
            potential += 0.2

        # API-based potential
        if any(pattern in tech_names for pattern in ["fastapi", "django", "flask"]):
            potential += 0.2

        # Database integration potential
        if any(pattern in tech_names for pattern in ["postgresql", "mongodb", "redis"]):
            potential += 0.1

        return round(min(1.0, potential), 2)

    def _suggest_workflows(
        self,
        technologies: List[TechnologyInfo],
        architecture_type: Optional[str],
        automation_potential: float,
    ) -> List[str]:
        """Suggest potential n8n workflows based on analysis"""
        suggestions = []
        tech_names = [tech.name for tech in technologies]

        # CI/CD workflows
        if automation_potential > 0.5:
            suggestions.append("automated_testing_pipeline")
            suggestions.append("deployment_automation")

        # Database workflows
        if any(db in tech_names for db in ["postgresql", "mongodb", "redis"]):
            suggestions.append("database_backup_automation")
            suggestions.append("data_migration_workflow")

        # API workflows
        if any(api in tech_names for api in ["fastapi", "django", "flask"]):
            suggestions.append("api_monitoring_workflow")
            suggestions.append("api_testing_automation")

        # Docker workflows
        if "docker" in tech_names:
            suggestions.append("container_build_pipeline")
            suggestions.append("container_deployment")

        # n8n integration workflows
        if "n8n" in tech_names:
            suggestions.append("workflow_management")
            suggestions.append("n8n_backup_workflow")

        # Documentation workflows
        if "docs" in [tech.name for tech in technologies]:
            suggestions.append("documentation_generation")
            suggestions.append("changelog_automation")

        # Monitoring workflows
        if architecture_type in ["microservices", "api"]:
            suggestions.append("health_check_automation")
            suggestions.append("performance_monitoring")

        return suggestions
