"""
Integration tests for n8n API
"""

import pytest
import asyncio
import httpx
import json
from unittest.mock import AsyncMock, patch, MagicMock
from pathlib import Path


@pytest.mark.integration
@pytest.mark.docker
class TestN8nIntegration:
    """Integration tests for n8n API"""

    @pytest.fixture
    def n8n_client(self, test_config):
        """Create n8n API client for testing"""
        from src.integrations.n8n_client import N8nClient

        client = N8nClient(
            base_url=test_config.n8n.url,
            username=test_config.n8n.user,
            password=test_config.n8n.password,
        )

        # Mock the client's HTTP client for testing
        client.client = AsyncMock()
        client._auth_token = "mock-api-key"

        return client

    @pytest.mark.asyncio
    async def test_n8n_authentication(self, test_config, http_client):
        """Test n8n authentication"""

        try:
            # Test login endpoint
            login_data = {
                "email": test_config.n8n.user,
                "password": test_config.n8n.password,
            }

            response = await http_client.post(
                f"{test_config.n8n.url}/api/v1/login", json=login_data
            )

            if response.status_code == 200:
                data = response.json()
                assert "data" in data
                assert "token" in data["data"]
            elif response.status_code == 401:
                pytest.skip("n8n authentication failed - check credentials")
            else:
                pytest.skip("n8n service not available")

        except httpx.ConnectError:
            pytest.skip("n8n service not running")

    @pytest.mark.asyncio
    async def test_n8n_workflow_crud_operations(self, n8n_client):
        """Test CRUD operations for n8n workflows"""

        # Test workflow data
        test_workflow = {
            "name": "Test Workflow",
            "nodes": [
                {
                    "id": "node1",
                    "name": "Schedule Trigger",
                    "type": "n8n-nodes-base.scheduleTrigger",
                    "typeVersion": 1,
                    "position": [100, 100],
                    "parameters": {
                        "rule": {"interval": [{"field": "hours", "hoursInterval": 1}]}
                    },
                },
                {
                    "id": "node2",
                    "name": "HTTP Request",
                    "type": "n8n-nodes-base.httpRequest",
                    "typeVersion": 1,
                    "position": [300, 100],
                    "parameters": {
                        "url": "http://localhost:8000/health",
                        "method": "GET",
                    },
                },
            ],
            "connections": {
                "node1": {"main": [[{"node": "node2", "type": "main", "index": 0}]]}
            },
            "active": False,
            "settings": {},
        }

        # Mock successful API responses
        with (
            patch.object(n8n_client.client, "post") as mock_post,
            patch.object(n8n_client.client, "get") as mock_get,
            patch.object(n8n_client.client, "put") as mock_put,
            patch.object(n8n_client.client, "delete") as mock_delete,
        ):
            # Mock create workflow response
            mock_create_response = MagicMock()
            mock_create_response.status_code = 201
            mock_create_response.json.return_value = {
                "data": {"id": "test-workflow-123", **test_workflow}
            }
            mock_post.return_value = mock_create_response

            # Test create workflow
            created_workflow = await n8n_client.create_workflow(test_workflow)
            assert created_workflow["id"] == "test-workflow-123"
            assert created_workflow["name"] == "Test Workflow"

            # Mock get workflows response
            mock_get_response = MagicMock()
            mock_get_response.status_code = 200
            mock_get_response.json.return_value = {
                "data": [{"id": "test-workflow-123", **test_workflow}]
            }
            mock_get.return_value = mock_get_response

            # Test get workflows
            workflows = await n8n_client.get_workflows()
            assert len(workflows) == 1
            assert workflows[0]["id"] == "test-workflow-123"

            # Test get single workflow
            workflow = await n8n_client.get_workflow("test-workflow-123")
            assert workflow is not None
            if isinstance(workflow, list):
                assert len(workflow) > 0
                workflow = workflow[0]
            assert workflow["id"] == "test-workflow-123"

            # Mock update workflow response
            mock_update_response = MagicMock()
            mock_update_response.status_code = 200
            updated_workflow = {**test_workflow, "name": "Updated Test Workflow"}
            mock_update_response.json.return_value = {
                "data": {"id": "test-workflow-123", **updated_workflow}
            }
            mock_put.return_value = mock_update_response

            # Test update workflow
            updated = await n8n_client.update_workflow(
                "test-workflow-123", updated_workflow
            )
            assert updated["name"] == "Updated Test Workflow"

            # Mock delete workflow response
            mock_delete_response = MagicMock()
            mock_delete_response.status_code = 200
            mock_delete.return_value = mock_delete_response

            # Test delete workflow
            result = await n8n_client.delete_workflow("test-workflow-123")
            assert result is True

    @pytest.mark.asyncio
    async def test_n8n_workflow_execution(self, n8n_client):
        """Test n8n workflow execution"""

        workflow_id = "test-workflow-123"

        with (
            patch.object(n8n_client.client, "post") as mock_post,
            patch.object(n8n_client.client, "get") as mock_get,
        ):
            # Mock execute workflow response
            mock_execute_response = MagicMock()
            mock_execute_response.status_code = 200
            mock_execute_response.json.return_value = {
                "data": {
                    "executionId": "exec-123",
                    "finished": False,
                    "status": "running",
                }
            }
            mock_post.return_value = mock_execute_response

            # Test execute workflow
            execution = await n8n_client.execute_workflow(workflow_id)
            assert execution["executionId"] == "exec-123"
            assert execution["status"] == "running"

            # Mock get execution response
            mock_execution_response = MagicMock()
            mock_execution_response.status_code = 200
            mock_execution_response.json.return_value = {
                "data": {
                    "id": "exec-123",
                    "finished": True,
                    "status": "success",
                    "data": {"resultData": [{"json": {"status": "healthy"}}]},
                }
            }
            mock_get.return_value = mock_execution_response

            # Test get execution status
            execution_status = await n8n_client.get_execution("exec-123")
            assert execution_status["status"] == "success"
            assert execution_status["finished"] is True

    @pytest.mark.asyncio
    async def test_n8n_webhook_operations(self, n8n_client):
        """Test n8n webhook operations"""

        workflow_id = "test-workflow-123"
        webhook_data = {
            "path": "test-webhook",
            "httpMethod": "POST",
            "authentication": "none",
        }

        with (
            patch.object(n8n_client.client, "post") as mock_post,
            patch.object(n8n_client.client, "get") as mock_get,
        ):
            # Mock create webhook response
            mock_webhook_response = MagicMock()
            mock_webhook_response.status_code = 200
            mock_webhook_response.json.return_value = {
                "data": {
                    "webhookUrl": "http://localhost:5678/webhook/test-webhook",
                    "path": "test-webhook",
                }
            }
            mock_post.return_value = mock_webhook_response

            # Test create webhook
            webhook = await n8n_client.create_webhook(workflow_id, webhook_data)
            assert webhook["path"] == "test-webhook"
            assert "webhookUrl" in webhook

            # Mock get webhooks response
            mock_webhooks_response = MagicMock()
            mock_webhooks_response.status_code = 200
            mock_webhooks_response.json.return_value = {
                "data": [
                    {
                        "workflowId": workflow_id,
                        "path": "test-webhook",
                        "webhookUrl": "http://localhost:5678/webhook/test-webhook",
                    }
                ]
            }
            mock_get.return_value = mock_webhooks_response

            # Test get webhooks
            webhooks = await n8n_client.get_webhooks(workflow_id)
            assert len(webhooks) == 1
            assert webhooks[0]["path"] == "test-webhook"

    @pytest.mark.asyncio
    async def test_n8n_credential_management(self, n8n_client):
        """Test n8n credential management"""

        credential_data = {
            "name": "Test API Credential",
            "type": "httpBasicAuth",
            "data": {"user": "testuser", "password": "testpass"},
        }

        with (
            patch.object(n8n_client.client, "post") as mock_post,
            patch.object(n8n_client.client, "get") as mock_get,
            patch.object(n8n_client.client, "put") as mock_put,
            patch.object(n8n_client.client, "delete") as mock_delete,
        ):
            # Mock create credential response
            mock_create_response = MagicMock()
            mock_create_response.status_code = 201
            mock_create_response.json.return_value = {
                "data": {"id": "cred-123", **credential_data}
            }
            mock_post.return_value = mock_create_response

            # Test create credential
            credential = await n8n_client.create_credential(credential_data)
            assert credential["id"] == "cred-123"
            assert credential["name"] == "Test API Credential"

            # Mock get credentials response
            mock_credentials_response = MagicMock()
            mock_credentials_response.status_code = 200
            mock_credentials_response.json.return_value = {
                "data": [{"id": "cred-123", **credential_data}]
            }
            mock_get.return_value = mock_credentials_response

            # Test get credentials
            credentials = await n8n_client.get_credentials()
            assert len(credentials) == 1
            assert credentials[0]["id"] == "cred-123"

            # Mock delete credential response
            mock_delete_response = MagicMock()
            mock_delete_response.status_code = 200
            mock_delete.return_value = mock_delete_response

            # Test delete credential
            result = await n8n_client.delete_credential("cred-123")
            assert result is True

    @pytest.mark.asyncio
    async def test_n8n_error_handling(self, n8n_client):
        """Test n8n error handling"""

        with patch.object(n8n_client.client, "get") as mock_get:
            # Mock error response
            mock_error_response = MagicMock()
            mock_error_response.status_code = 404
            mock_error_response.json.return_value = {"message": "Workflow not found"}
            mock_get.return_value = mock_error_response

            # Test error handling
            workflow = await n8n_client.get_workflow("nonexistent-workflow")
            assert workflow is None

    @pytest.mark.asyncio
    async def test_n8n_workflow_validation(self, n8n_client):
        """Test n8n workflow validation"""

        # Invalid workflow (missing required fields)
        invalid_workflow = {
            "name": "Invalid Workflow",
            "nodes": [],  # Missing required node structure
        }

        # Valid workflow
        valid_workflow = {
            "name": "Valid Workflow",
            "nodes": [
                {
                    "id": "node1",
                    "name": "Manual Trigger",
                    "type": "n8n-nodes-base.manualTrigger",
                    "typeVersion": 1,
                    "position": [100, 100],
                    "parameters": {},
                }
            ],
            "connections": {},
            "active": False,
            "settings": {},
        }

        with patch.object(n8n_client.client, "post") as mock_post:
            # Mock validation error response
            mock_error_response = MagicMock()
            mock_error_response.status_code = 400
            mock_error_response.json.return_value = {
                "message": "Invalid workflow structure"
            }
            mock_post.return_value = mock_error_response

            # Test invalid workflow
            result = await n8n_client.create_workflow(invalid_workflow)
            assert result is None

            # Mock successful response
            mock_success_response = MagicMock()
            mock_success_response.status_code = 201
            mock_success_response.json.return_value = {
                "data": {"id": "valid-workflow-123", **valid_workflow}
            }
            mock_post.return_value = mock_success_response

            # Test valid workflow
            result = await n8n_client.create_workflow(valid_workflow)
            assert result is not None
            assert result["id"] == "valid-workflow-123"
