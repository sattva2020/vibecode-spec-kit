"""
n8n API Client for Intelligent n8n Workflow Creation System
"""

import httpx
import logging
from typing import Dict, Any, List, Optional
import asyncio


class N8nClient:
    """Client for interacting with n8n API"""

    def __init__(
        self, base_url: str, username: str, password: str, api_key: Optional[str] = None
    ):
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)
        self.logger = logging.getLogger(__name__)
        self._auth_token = None

    async def initialize(self):
        """Initialize the client and authenticate"""
        if self.api_key:
            self._auth_token = self.api_key
        else:
            await self._authenticate()

    async def _authenticate(self):
        """Authenticate with n8n"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/login",
                json={"email": self.username, "password": self.password},
            )

            if response.status_code == 200:
                data = response.json()
                self._auth_token = data.get("data", {}).get("token")
                self.logger.info("Successfully authenticated with n8n")
            else:
                self.logger.error(f"Authentication failed: {response.status_code}")

        except Exception as e:
            self.logger.error(f"Authentication error: {e}")

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        headers = {"Content-Type": "application/json"}
        if self._auth_token:
            headers["Authorization"] = f"Bearer {self._auth_token}"
        return headers

    async def get_workflows(self) -> List[Dict[str, Any]]:
        """Get all workflows"""
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/workflows", headers=self._get_headers()
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            else:
                self.logger.error(f"Failed to get workflows: {response.status_code}")
                return []

        except Exception as e:
            self.logger.error(f"Error getting workflows: {e}")
            return []

    async def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific workflow"""
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/workflows/{workflow_id}",
                headers=self._get_headers(),
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("data")
            else:
                self.logger.error(
                    f"Failed to get workflow {workflow_id}: {response.status_code}"
                )
                return None

        except Exception as e:
            self.logger.error(f"Error getting workflow {workflow_id}: {e}")
            return None

    async def create_workflow(
        self, workflow_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Create a new workflow"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/workflows",
                headers=self._get_headers(),
                json=workflow_data,
            )

            if response.status_code in [200, 201]:
                data = response.json()
                return data.get("data")
            else:
                self.logger.error(f"Failed to create workflow: {response.status_code}")
                return None

        except Exception as e:
            self.logger.error(f"Error creating workflow: {e}")
            return None

    async def update_workflow(
        self, workflow_id: str, workflow_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update an existing workflow"""
        try:
            response = await self.client.put(
                f"{self.base_url}/api/v1/workflows/{workflow_id}",
                headers=self._get_headers(),
                json=workflow_data,
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("data")
            else:
                self.logger.error(
                    f"Failed to update workflow {workflow_id}: {response.status_code}"
                )
                return None

        except Exception as e:
            self.logger.error(f"Error updating workflow {workflow_id}: {e}")
            return None

    async def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow"""
        try:
            response = await self.client.delete(
                f"{self.base_url}/api/v1/workflows/{workflow_id}",
                headers=self._get_headers(),
            )

            return response.status_code in [200, 204]

        except Exception as e:
            self.logger.error(f"Error deleting workflow {workflow_id}: {e}")
            return False

    async def execute_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Execute a workflow"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/workflows/{workflow_id}/execute",
                headers=self._get_headers(),
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("data")
            else:
                self.logger.error(
                    f"Failed to execute workflow {workflow_id}: {response.status_code}"
                )
                return None

        except Exception as e:
            self.logger.error(f"Error executing workflow {workflow_id}: {e}")
            return None

    async def get_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get execution details"""
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/executions/{execution_id}",
                headers=self._get_headers(),
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("data")
            else:
                self.logger.error(
                    f"Failed to get execution {execution_id}: {response.status_code}"
                )
                return None

        except Exception as e:
            self.logger.error(f"Error getting execution {execution_id}: {e}")
            return None

    async def create_webhook(
        self, workflow_id: str, webhook_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Create a webhook for a workflow"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/workflows/{workflow_id}/webhooks",
                headers=self._get_headers(),
                json=webhook_data,
            )

            if response.status_code in [200, 201]:
                data = response.json()
                return data.get("data")
            else:
                self.logger.error(f"Failed to create webhook: {response.status_code}")
                return None

        except Exception as e:
            self.logger.error(f"Error creating webhook: {e}")
            return None

    async def get_webhooks(self, workflow_id: str) -> List[Dict[str, Any]]:
        """Get webhooks for a workflow"""
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/workflows/{workflow_id}/webhooks",
                headers=self._get_headers(),
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            else:
                self.logger.error(f"Failed to get webhooks: {response.status_code}")
                return []

        except Exception as e:
            self.logger.error(f"Error getting webhooks: {e}")
            return []

    async def create_credential(
        self, credential_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Create a credential"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/credentials",
                headers=self._get_headers(),
                json=credential_data,
            )

            if response.status_code in [200, 201]:
                data = response.json()
                return data.get("data")
            else:
                self.logger.error(
                    f"Failed to create credential: {response.status_code}"
                )
                return None

        except Exception as e:
            self.logger.error(f"Error creating credential: {e}")
            return None

    async def get_credentials(self) -> List[Dict[str, Any]]:
        """Get all credentials"""
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/credentials", headers=self._get_headers()
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            else:
                self.logger.error(f"Failed to get credentials: {response.status_code}")
                return []

        except Exception as e:
            self.logger.error(f"Error getting credentials: {e}")
            return []

    async def delete_credential(self, credential_id: str) -> bool:
        """Delete a credential"""
        try:
            response = await self.client.delete(
                f"{self.base_url}/api/v1/credentials/{credential_id}",
                headers=self._get_headers(),
            )

            return response.status_code in [200, 204]

        except Exception as e:
            self.logger.error(f"Error deleting credential {credential_id}: {e}")
            return False

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
