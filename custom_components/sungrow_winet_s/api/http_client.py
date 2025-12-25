"""HTTP API client for Sungrow WINET-S local access."""
import asyncio
import logging
from typing import Any, Optional

import aiohttp

from ..const import DEFAULT_TIMEOUT

_LOGGER = logging.getLogger(__name__)


class SungrowHTTPClient:
    """Client for HTTP API communication with Sungrow WINET-S device.
    
    This client accesses the local HTTP API exposed by the WINET-S dongle.
    Note: This API is limited compared to Modbus and may not expose all data.
    """

    def __init__(
        self,
        host: str,
        port: int = 8082,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize the HTTP client.
        
        Args:
            host: IP address or hostname of the WINET-S device
            port: HTTP port (default: 8082)
            timeout: Request timeout in seconds
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.base_url = f"http://{host}:{port}"
        self._session: Optional[aiohttp.ClientSession] = None
        self._lock = asyncio.Lock()

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        return self._session

    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def get_device_info(self) -> Optional[dict[str, Any]]:
        """Get device information from WINET-S.
        
        Returns:
            Device info dictionary or None if request failed
        """
        try:
            session = await self._get_session()
            async with session.get(f"{self.base_url}/device/getParam") as response:
                if response.status == 200:
                    data = await response.json()
                    _LOGGER.debug("Device info: %s", data)
                    return data
                _LOGGER.error("HTTP request failed with status %s", response.status)
                return None
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout getting device info")
            return None
        except Exception as err:
            _LOGGER.error("Error getting device info: %s", err)
            return None

    async def get_runtime_data(self) -> Optional[dict[str, Any]]:
        """Get runtime data from WINET-S.
        
        Returns:
            Runtime data dictionary or None if request failed
        """
        try:
            session = await self._get_session()
            async with session.get(f"{self.base_url}/runtime/get") as response:
                if response.status == 200:
                    data = await response.json()
                    _LOGGER.debug("Runtime data: %s", data)
                    return self._parse_runtime_data(data)
                _LOGGER.error("HTTP request failed with status %s", response.status)
                return None
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout getting runtime data")
            return None
        except Exception as err:
            _LOGGER.error("Error getting runtime data: %s", err)
            return None

    def _parse_runtime_data(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        """Parse raw runtime data into standardized format.
        
        Note: The exact structure depends on WINET-S firmware version.
        This is a best-effort mapping.
        """
        parsed = {}
        
        try:
            # Map common fields (structure may vary by firmware)
            result_data = raw_data.get("result_data", {})
            
            # PV data
            if "p13003" in result_data:  # Total DC power
                parsed["pv_power"] = float(result_data["p13003"])
            
            # Battery data
            if "p13022" in result_data:  # Battery SOC
                parsed["battery_soc"] = float(result_data["p13022"]) * 0.1
            if "p13020" in result_data:  # Battery power
                parsed["battery_power"] = float(result_data["p13020"])
                
            # Grid data
            if "p13009" in result_data:  # Export power
                parsed["grid_export_power"] = float(result_data["p13009"])
                
            # Load data
            if "p13007" in result_data:  # Load power
                parsed["load_power"] = float(result_data["p13007"])
                
            _LOGGER.debug("Parsed data: %s", parsed)
            
        except Exception as err:
            _LOGGER.error("Error parsing runtime data: %s", err)
            
        return parsed

    async def get_export_limit(self) -> Optional[float]:
        """Get current export limit setting.
        
        Returns:
            Export limit in watts or None if request failed
        """
        try:
            session = await self._get_session()
            async with session.get(f"{self.base_url}/config/export_limit") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("export_limit")
                return None
        except Exception as err:
            _LOGGER.error("Error getting export limit: %s", err)
            return None

    async def test_connection(self) -> bool:
        """Test if HTTP connection to WINET-S is working.
        
        Returns:
            True if connection test successful
        """
        try:
            device_info = await self.get_device_info()
            return device_info is not None
        except Exception as err:
            _LOGGER.error("HTTP connection test failed: %s", err)
            return False

    async def read_all_data(self) -> dict[str, Any]:
        """Read all available data via HTTP API.
        
        Returns:
            Dictionary with sensor keys and values
        """
        runtime_data = await self.get_runtime_data()
        return runtime_data if runtime_data else {}
