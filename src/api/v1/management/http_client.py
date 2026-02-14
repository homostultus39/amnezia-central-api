import uuid
import httpx
from typing import Any

from src.management.logger import configure_logger
from src.management.settings import get_settings
from src.api.v1.management.exceptions.cluster import ClusterAPIException

logger = configure_logger("ClusterAPIClient", "cyan")
settings = get_settings()


class ClusterAPIClient:
    def __init__(self, endpoint: str, api_key: str, timeout: int | None = None):
        self.protocol = "http" if settings.development else "http"
        self.endpoint = f"{self.protocol}://{endpoint.rstrip('/')}"
        self.api_key = api_key
        self.timeout = timeout if timeout is not None else settings.cluster_api_timeout
        self.headers = {"X-API-Key": api_key}

    async def get_server_status(self) -> dict[str, Any]:
        url = f"{self.endpoint}/api/v1/server/status"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                logger.debug(f"Server status retrieved from {self.endpoint}")
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting server status from {self.endpoint}: {e}")
            raise ClusterAPIException(f"Server returned status {e.response.status_code}")
        except httpx.TimeoutException:
            logger.error(f"Timeout getting server status from {self.endpoint}")
            raise ClusterAPIException("Server status request timed out")
        except Exception as e:
            logger.error(f"Error getting server status from {self.endpoint}: {e}")
            raise ClusterAPIException(f"Failed to get server status: {str(e)}")

    async def restart_server(self) -> dict[str, Any]:
        url = f"{self.endpoint}/api/v1/server/restart"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=self.headers)
                response.raise_for_status()
                logger.info(f"Server restart initiated on {self.endpoint}")
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error restarting server on {self.endpoint}: {e}")
            raise ClusterAPIException(f"Server returned status {e.response.status_code}")
        except httpx.TimeoutException:
            logger.error(f"Timeout restarting server on {self.endpoint}")
            raise ClusterAPIException("Server restart request timed out")
        except Exception as e:
            logger.error(f"Error restarting server on {self.endpoint}: {e}")
            raise ClusterAPIException(f"Failed to restart server: {str(e)}")

    async def create_peer(self, app_type: str, protocol: str) -> dict[str, Any]:
        """Create a new peer on cluster. Cluster generates keys, IP, and endpoint."""
        url = f"{self.endpoint}/api/v1/peers/"
        peer_data = {
            "app_type": app_type,
            "protocol": protocol,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=self.headers, json=peer_data)
                response.raise_for_status()
                logger.info(f"Peer created on {self.endpoint}")
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error creating peer on {self.endpoint}: {e}")
            raise ClusterAPIException(f"Server returned status {e.response.status_code}")
        except httpx.TimeoutException:
            logger.error(f"Timeout creating peer on {self.endpoint}")
            raise ClusterAPIException("Create peer request timed out")
        except Exception as e:
            logger.error(f"Error creating peer on {self.endpoint}: {e}")
            raise ClusterAPIException(f"Failed to create peer: {str(e)}")

    async def recreate_peer(self, peer_data: dict[str, Any]) -> dict[str, Any]:
        """Recreate an existing peer on cluster with provided data (for updates)."""
        url = f"{self.endpoint}/api/v1/peers/"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=self.headers, json=peer_data)
                response.raise_for_status()
                logger.info(f"Peer recreated on {self.endpoint}")
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error recreating peer on {self.endpoint}: {e}")
            raise ClusterAPIException(f"Server returned status {e.response.status_code}")
        except httpx.TimeoutException:
            logger.error(f"Timeout recreating peer on {self.endpoint}")
            raise ClusterAPIException("Recreate peer request timed out")
        except Exception as e:
            logger.error(f"Error recreating peer on {self.endpoint}: {e}")
            raise ClusterAPIException(f"Failed to recreate peer: {str(e)}")

    async def delete_peer(self, public_key: str) -> dict[str, Any]:
        url = f"{self.endpoint}/api/v1/peers/"
        payload = {"public_key": public_key}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request("DELETE", url, headers=self.headers, json=payload)
                response.raise_for_status()
                logger.info(f"Peer {public_key} deleted on {self.endpoint}")
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error deleting peer on {self.endpoint}: {e}")
            raise ClusterAPIException(f"Server returned status {e.response.status_code}")
        except httpx.TimeoutException:
            logger.error(f"Timeout deleting peer on {self.endpoint}")
            raise ClusterAPIException("Delete peer request timed out")
        except Exception as e:
            logger.error(f"Error deleting peer on {self.endpoint}: {e}")
            raise ClusterAPIException(f"Failed to delete peer: {str(e)}")

    async def get_peer(self, peer_id: uuid.UUID) -> dict[str, Any]:
        url = f"{self.endpoint}/api/v1/peers/{peer_id}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                logger.debug(f"Peer {peer_id} retrieved from {self.endpoint}")
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting peer from {self.endpoint}: {e}")
            raise ClusterAPIException(f"Server returned status {e.response.status_code}")
        except httpx.TimeoutException:
            logger.error(f"Timeout getting peer from {self.endpoint}")
            raise ClusterAPIException("Get peer request timed out")
        except Exception as e:
            logger.error(f"Error getting peer from {self.endpoint}: {e}")
            raise ClusterAPIException(f"Failed to get peer: {str(e)}")

    async def get_all_peers(self) -> list[dict[str, Any]]:
        url = f"{self.endpoint}/api/v1/peers/"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                logger.debug(f"All peers retrieved from {self.endpoint}")
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting peers from {self.endpoint}: {e}")
            raise ClusterAPIException(f"Server returned status {e.response.status_code}")
        except httpx.TimeoutException:
            logger.error(f"Timeout getting peers from {self.endpoint}")
            raise ClusterAPIException("Get peers request timed out")
        except Exception as e:
            logger.error(f"Error getting peers from {self.endpoint}: {e}")
            raise ClusterAPIException(f"Failed to get peers: {str(e)}")
