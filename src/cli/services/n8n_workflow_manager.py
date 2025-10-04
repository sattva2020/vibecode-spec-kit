"""
n8n Workflow Manager - автоматическое создание workflow'ов через API
"""

import asyncio
import json
import httpx
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from ..utils.output import OutputFormatter


class WorkflowType(Enum):
    """Типы workflow'ов для RAG системы"""

    CODE_INDEXING = "code_indexing"
    CODE_ANALYSIS = "code_analysis"
    SPEC_KIT_VALIDATION = "spec_kit_validation"
    AUTOMATED_TESTING = "automated_testing"
    DEPLOYMENT = "deployment"
    DOCUMENTATION = "documentation"


@dataclass
class WorkflowTemplate:
    """Шаблон для создания workflow'а"""

    name: str
    description: str
    workflow_type: WorkflowType
    nodes: List[Dict[str, Any]]
    connections: List[Dict[str, Any]]
    settings: Optional[Dict[str, Any]] = None


class N8nWorkflowManager:
    """Менеджер для создания и управления n8n workflow'ами через API"""

    def __init__(
        self,
        n8n_url: str = "http://localhost:5678",
        username: str = "admin",
        password: str = "admin123",
    ):
        self.n8n_url = n8n_url.rstrip("/")
        self.username = username
        self.password = password
        self.auth_token: Optional[str] = None
        self.output = OutputFormatter()
        self.client = httpx.AsyncClient(timeout=30.0)

    async def authenticate(self) -> bool:
        """Аутентификация в n8n"""
        try:
            auth_url = f"{self.n8n_url}/rest/login"
            auth_data = {"email": self.username, "password": self.password}

            response = await self.client.post(auth_url, json=auth_data)

            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("token")
                self.output.print_success("✅ Успешная аутентификация в n8n")
                return True
            else:
                self.output.print_error(
                    f"❌ Ошибка аутентификации: {response.status_code}"
                )
                return False

        except Exception as e:
            self.output.print_error(f"❌ Ошибка подключения к n8n: {e}")
            return False

    async def create_workflow(self, template: WorkflowTemplate) -> Optional[str]:
        """Создание workflow'а из шаблона"""
        if not self.auth_token:
            if not await self.authenticate():
                return None

        try:
            workflow_data = {
                "name": template.name,
                "nodes": template.nodes,
                "connections": template.connections,
                "settings": template.settings or {},
                "active": False,  # Создаем неактивным для безопасности
                "versionId": 1,
            }

            create_url = f"{self.n8n_url}/rest/workflows"
            headers = {"Authorization": f"Bearer {self.auth_token}"}

            response = await self.client.post(
                create_url, json=workflow_data, headers=headers
            )

            if response.status_code in [200, 201]:
                workflow_id = response.json().get("id")
                self.output.print_success(
                    f"✅ Workflow '{template.name}' создан (ID: {workflow_id})"
                )
                return workflow_id
            else:
                self.output.print_error(
                    f"❌ Ошибка создания workflow: {response.status_code}"
                )
                return None

        except Exception as e:
            self.output.print_error(f"❌ Ошибка создания workflow: {e}")
            return None

    async def list_workflows(self) -> List[Dict[str, Any]]:
        """Получение списка workflow'ов"""
        if not self.auth_token:
            if not await self.authenticate():
                return []

        try:
            list_url = f"{self.n8n_url}/rest/workflows"
            headers = {"Authorization": f"Bearer {self.auth_token}"}

            response = await self.client.get(list_url, headers=headers)

            if response.status_code == 200:
                workflows = response.json().get("data", [])
                self.output.print_success(f"✅ Найдено {len(workflows)} workflow'ов")
                return workflows
            else:
                self.output.print_error(
                    f"❌ Ошибка получения workflow'ов: {response.status_code}"
                )
                return []

        except Exception as e:
            self.output.print_error(f"❌ Ошибка получения workflow'ов: {e}")
            return []

    async def execute_workflow(
        self, workflow_id: str, input_data: Dict[str, Any] = None
    ) -> bool:
        """Запуск workflow'а"""
        if not self.auth_token:
            if not await self.authenticate():
                return False

        try:
            execute_url = f"{self.n8n_url}/rest/workflows/{workflow_id}/execute"
            headers = {"Authorization": f"Bearer {self.auth_token}"}

            payload = {"data": input_data or {}}

            response = await self.client.post(
                execute_url, json=payload, headers=headers
            )

            if response.status_code == 200:
                self.output.print_success(f"✅ Workflow {workflow_id} запущен успешно")
                return True
            else:
                self.output.print_error(
                    f"❌ Ошибка запуска workflow: {response.status_code}"
                )
                return False

        except Exception as e:
            self.output.print_error(f"❌ Ошибка запуска workflow: {e}")
            return False

    def get_code_indexing_template(self, project_path: str) -> WorkflowTemplate:
        """Шаблон для автоматической индексации кода"""
        return WorkflowTemplate(
            name="RAG Code Indexing",
            description="Автоматическая индексация кода в RAG систему",
            workflow_type=WorkflowType.CODE_INDEXING,
            nodes=[
                {
                    "id": "webhook-trigger",
                    "name": "File Changed",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 1,
                    "position": [240, 300],
                    "parameters": {"path": "code-changed", "httpMethod": "POST"},
                },
                {
                    "id": "file-processor",
                    "name": "Process File",
                    "type": "n8n-nodes-base.function",
                    "typeVersion": 1,
                    "position": [460, 300],
                    "parameters": {
                        "functionCode": f"""
// Обработка измененного файла для RAG индексации
const fileData = $input.first().json;
const filePath = fileData.file_path;
const content = fileData.content;
const language = fileData.language || 'unknown';

// Определяем тип файла и создаем метаданные
const metadata = {{
    file_path: filePath,
    language: language,
    project_path: "{project_path}",
    indexed_at: new Date().toISOString(),
    file_size: content.length
}};

// Подготавливаем данные для RAG Proxy
const ragData = {{
    file_path: filePath,
    code: content,
    language: language,
    context: {{
        project_type: "vibecode_spec_kit",
        methodology: "spec_driven_development"
    }},
    metadata: metadata
}};

return {{
    json: ragData,
    binary: {{}}
}};
                        """
                    },
                },
                {
                    "id": "rag-proxy-call",
                    "name": "Index in RAG",
                    "type": "n8n-nodes-base.httpRequest",
                    "typeVersion": 4.1,
                    "position": [680, 300],
                    "parameters": {
                        "url": "http://rag-proxy:8000/api/learn",
                        "method": "POST",
                        "sendHeaders": True,
                        "headerParameters": {
                            "parameters": [
                                {"name": "Content-Type", "value": "application/json"}
                            ]
                        },
                        "sendBody": True,
                        "bodyParameters": {
                            "parameters": [
                                {
                                    "name": "file_path",
                                    "value": "={{ $json.file_path }}",
                                },
                                {"name": "code", "value": "={{ $json.code }}"},
                                {"name": "language", "value": "={{ $json.language }}"},
                                {"name": "context", "value": "={{ $json.context }}"},
                            ]
                        },
                    },
                },
                {
                    "id": "memory-bank-update",
                    "name": "Update Memory Bank",
                    "type": "n8n-nodes-base.httpRequest",
                    "typeVersion": 4.1,
                    "position": [900, 300],
                    "parameters": {
                        "url": "http://rag-proxy:8000/api/integrate",
                        "method": "POST",
                        "sendHeaders": True,
                        "headerParameters": {
                            "parameters": [
                                {"name": "Content-Type", "value": "application/json"}
                            ]
                        },
                        "sendBody": True,
                        "bodyParameters": {
                            "parameters": [
                                {"name": "spec_type", "value": "auto_detect"},
                                {"name": "code", "value": "={{ $json.code }}"},
                                {
                                    "name": "file_path",
                                    "value": "={{ $json.file_path }}",
                                },
                            ]
                        },
                    },
                },
            ],
            connections={
                "webhook-trigger": {
                    "main": [[{"node": "file-processor", "type": "main", "index": 0}]]
                },
                "file-processor": {
                    "main": [[{"node": "rag-proxy-call", "type": "main", "index": 0}]]
                },
                "rag-proxy-call": {
                    "main": [
                        [{"node": "memory-bank-update", "type": "main", "index": 0}]
                    ]
                },
            },
        )

    def get_spec_kit_validation_template(self) -> WorkflowTemplate:
        """Шаблон для валидации Spec Kit методологий"""
        return WorkflowTemplate(
            name="Spec Kit Validation",
            description="Валидация кода по методологиям Spec Kit",
            workflow_type=WorkflowType.SPEC_KIT_VALIDATION,
            nodes=[
                {
                    "id": "manual-trigger",
                    "name": "Manual Trigger",
                    "type": "n8n-nodes-base.manualTrigger",
                    "typeVersion": 1,
                    "position": [240, 300],
                    "parameters": {},
                },
                {
                    "id": "code-analyzer",
                    "name": "Analyze Code",
                    "type": "n8n-nodes-base.function",
                    "typeVersion": 1,
                    "position": [460, 300],
                    "parameters": {
                        "functionCode": """
// Анализ кода на соответствие Spec Kit методологиям
const inputData = $input.first().json;

// Проверяем различные аспекты Spec Kit
const checks = {
    modularity: checkModularity(inputData.code),
    testability: checkTestability(inputData.code),
    documentation: checkDocumentation(inputData.code),
    error_handling: checkErrorHandling(inputData.code)
};

function checkModularity(code) {
    // Проверка модульности кода
    const hasClasses = /class\\s+\\w+/.test(code);
    const hasFunctions = /function\\s+\\w+|const\\s+\\w+\\s*=.*=>/.test(code);
    return { score: hasClasses && hasFunctions ? 1.0 : 0.5, details: "Modular structure detected" };
}

function checkTestability(code) {
    // Проверка тестируемости
    const hasTests = /test|spec|describe|it\\(/.test(code);
    return { score: hasTests ? 1.0 : 0.3, details: hasTests ? "Tests present" : "No tests found" };
}

function checkDocumentation(code) {
    // Проверка документации
    const hasComments = /\\/\\/|\\/\\*/.test(code);
    return { score: hasComments ? 0.8 : 0.2, details: hasComments ? "Comments present" : "Limited documentation" };
}

function checkErrorHandling(code) {
    // Проверка обработки ошибок
    const hasTryCatch = /try\\s*\\{|catch\\s*\\(/.test(code);
    const hasErrorHandling = /throw|error|exception/i.test(code);
    return { score: hasTryCatch || hasErrorHandling ? 0.9 : 0.4, details: "Error handling present" };
}

const overallScore = Object.values(checks).reduce((sum, check) => sum + check.score, 0) / Object.keys(checks).length;

return {
    json: {
        code: inputData.code,
        checks: checks,
        overall_score: overallScore,
        spec_kit_compliance: overallScore > 0.7 ? "HIGH" : overallScore > 0.4 ? "MEDIUM" : "LOW",
        recommendations: generateRecommendations(checks)
    }
};

function generateRecommendations(checks) {
    const recommendations = [];
    
    if (checks.modularity.score < 0.7) {
        recommendations.push("Consider breaking code into smaller, focused modules");
    }
    if (checks.testability.score < 0.7) {
        recommendations.push("Add unit tests following Test-First Implementation");
    }
    if (checks.documentation.score < 0.7) {
        recommendations.push("Add comprehensive documentation and comments");
    }
    if (checks.error_handling.score < 0.7) {
        recommendations.push("Implement proper error handling mechanisms");
    }
    
    return recommendations;
}
                        """
                    },
                },
                {
                    "id": "validation-report",
                    "name": "Generate Report",
                    "type": "n8n-nodes-base.httpRequest",
                    "typeVersion": 4.1,
                    "position": [680, 300],
                    "parameters": {
                        "url": "http://rag-proxy:8000/api/explain",
                        "method": "POST",
                        "sendHeaders": True,
                        "headerParameters": {
                            "parameters": [
                                {"name": "Content-Type", "value": "application/json"}
                            ]
                        },
                        "sendBody": True,
                        "bodyParameters": {
                            "parameters": [
                                {"name": "code", "value": "={{ $json.code }}"},
                                {"name": "language", "value": "typescript"},
                                {
                                    "name": "spec_kit_context",
                                    "value": "={{ JSON.stringify($json.checks) }}",
                                },
                            ]
                        },
                    },
                },
            ],
            connections={
                "manual-trigger": {
                    "main": [[{"node": "code-analyzer", "type": "main", "index": 0}]]
                },
                "code-analyzer": {
                    "main": [
                        [{"node": "validation-report", "type": "main", "index": 0}]
                    ]
                },
            },
        )

    async def setup_default_workflows(self, project_path: str) -> List[str]:
        """Создание стандартных workflow'ов для RAG системы"""
        created_workflows = []

        # Создаем workflow для индексации кода
        code_indexing_template = self.get_code_indexing_template(project_path)
        workflow_id = await self.create_workflow(code_indexing_template)
        if workflow_id:
            created_workflows.append(workflow_id)

        # Создаем workflow для валидации Spec Kit
        validation_template = self.get_spec_kit_validation_template()
        workflow_id = await self.create_workflow(validation_template)
        if workflow_id:
            created_workflows.append(workflow_id)

        return created_workflows

    async def close(self):
        """Закрытие HTTP клиента"""
        await self.client.aclose()


# Утилитарные функции для работы с workflow'ами
async def create_rag_workflows(project_path: str, n8n_config: Dict[str, str]) -> bool:
    """Создание всех необходимых RAG workflow'ов"""
    manager = N8nWorkflowManager(
        n8n_url=n8n_config.get("url", "http://localhost:5678"),
        username=n8n_config.get("username", "admin"),
        password=n8n_config.get("password", "admin123"),
    )

    try:
        self.output.print_header("🚀 Создание RAG Workflow'ов в n8n")

        # Аутентификация
        if not await manager.authenticate():
            return False

        # Создание workflow'ов
        created_workflows = await manager.setup_default_workflows(project_path)

        if created_workflows:
            self.output.print_success(
                f"✅ Создано {len(created_workflows)} workflow'ов"
            )
            for i, workflow_id in enumerate(created_workflows, 1):
                self.output.print_info(f"   {i}. Workflow ID: {workflow_id}")
            return True
        else:
            self.output.print_error("❌ Не удалось создать workflow'ы")
            return False

    except Exception as e:
        self.output.print_error(f"❌ Ошибка создания workflow'ов: {e}")
        return False
    finally:
        await manager.close()


if __name__ == "__main__":
    # Тестирование менеджера workflow'ов
    async def test_workflow_manager():
        manager = N8nWorkflowManager()

        if await manager.authenticate():
            workflows = await manager.list_workflows()
            print(f"Найдено {len(workflows)} workflow'ов")

        await manager.close()

    asyncio.run(test_workflow_manager())
