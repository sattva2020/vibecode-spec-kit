"""
Supabase Client for Intelligent n8n Workflow Creation System
"""

import httpx
import logging
from typing import Dict, Any, List, Optional
import asyncio


class SupabaseClient:
    """Client for interacting with Supabase"""

    def __init__(self, url: str, anon_key: str, service_key: Optional[str] = None):
        self.url = url.rstrip("/")
        self.anon_key = anon_key
        self.service_key = service_key
        self.client = httpx.AsyncClient(timeout=30.0)
        self.logger = logging.getLogger(__name__)

    def _get_headers(self, use_service_key: bool = False) -> Dict[str, str]:
        """Get headers for API requests"""
        headers = {
            "Content-Type": "application/json",
            "apikey": self.service_key if use_service_key else self.anon_key,
        }

        if use_service_key:
            headers["Authorization"] = f"Bearer {self.service_key}"
        else:
            headers["Authorization"] = f"Bearer {self.anon_key}"

        return headers

    async def query_table(
        self,
        table_name: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Query a table"""
        try:
            url = f"{self.url}/rest/v1/{table_name}"

            params = {}
            if filters:
                for key, value in filters.items():
                    params[key] = value

            if limit:
                params["limit"] = limit

            response = await self.client.get(
                url, headers=self._get_headers(), params=params
            )

            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(
                    f"Failed to query table {table_name}: {response.status_code}"
                )
                return []

        except Exception as e:
            self.logger.error(f"Error querying table {table_name}: {e}")
            return []

    async def insert_record(
        self, table_name: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Insert a record into a table"""
        try:
            url = f"{self.url}/rest/v1/{table_name}"

            response = await self.client.post(
                url, headers=self._get_headers(), json=data
            )

            if response.status_code in [200, 201]:
                return response.json()
            else:
                self.logger.error(
                    f"Failed to insert into table {table_name}: {response.status_code}"
                )
                return None

        except Exception as e:
            self.logger.error(f"Error inserting into table {table_name}: {e}")
            return None

    async def update_record(
        self, table_name: str, record_id: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update a record in a table"""
        try:
            url = f"{self.url}/rest/v1/{table_name}"

            response = await self.client.patch(
                url,
                headers=self._get_headers(),
                json=data,
                params={"id": f"eq.{record_id}"},
            )

            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(
                    f"Failed to update record {record_id} in table {table_name}: {response.status_code}"
                )
                return None

        except Exception as e:
            self.logger.error(
                f"Error updating record {record_id} in table {table_name}: {e}"
            )
            return None

    async def delete_record(self, table_name: str, record_id: str) -> bool:
        """Delete a record from a table"""
        try:
            url = f"{self.url}/rest/v1/{table_name}"

            response = await self.client.delete(
                url, headers=self._get_headers(), params={"id": f"eq.{record_id}"}
            )

            return response.status_code in [200, 204]

        except Exception as e:
            self.logger.error(
                f"Error deleting record {record_id} from table {table_name}: {e}"
            )
            return False

    async def execute_function(
        self, function_name: str, parameters: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Execute a Supabase function"""
        try:
            url = f"{self.url}/rest/v1/rpc/{function_name}"

            response = await self.client.post(
                url, headers=self._get_headers(), json=parameters or {}
            )

            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(
                    f"Failed to execute function {function_name}: {response.status_code}"
                )
                return None

        except Exception as e:
            self.logger.error(f"Error executing function {function_name}: {e}")
            return None

    async def get_health(self) -> bool:
        """Check Supabase health"""
        try:
            response = await self.client.get(f"{self.url}/health", timeout=5.0)
            return response.status_code == 200
        except Exception:
            return False

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
