"""Cloud API client for Sungrow iSolarCloud."""
import asyncio
import hashlib
import logging
import time
from typing import Any, Optional

import aiohttp
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend

from ..const import (
    CLOUD_API_BASE_URL,
    CLOUD_API_TOKEN_URL,
    CLOUD_API_PLANT_LIST_URL,
    CLOUD_API_DEVICE_LIST_URL,
    CLOUD_API_REALTIME_DATA_URL,
    DEFAULT_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)


class SungrowCloudClient:
    """Client for Sungrow iSolarCloud API.
    
    Uses OAuth 2.0 authentication with RSA signing.
    API documentation: https://developer-api.isolarcloud.com/
    """

    def __init__(
        self,
        username: str,
        password: str,
        api_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize the cloud client.
        
        Args:
            username: iSolarCloud account username/email
            password: iSolarCloud account password
            api_key: API key (optional, for advanced features)
            timeout: Request timeout in seconds
        """
        self.username = username
        self.password = password
        self.api_key = api_key
        self.timeout = timeout
        self.base_url = CLOUD_API_BASE_URL
        self._session: Optional[aiohttp.ClientSession] = None
        self._token: Optional[str] = None
        self._token_expires: float = 0
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

    def _generate_signature(self, params: dict[str, Any]) -> str:
        """Generate request signature for API authentication.
        
        Args:
            params: Request parameters
            
        Returns:
            MD5 signature string
        """
        # Sort parameters and create signature string
        sorted_params = sorted(params.items())
        sig_string = "".join([f"{k}{v}" for k, v in sorted_params if v is not None])
        
        # Add API key if available
        if self.api_key:
            sig_string += self.api_key
            
        # Generate MD5 hash
        return hashlib.md5(sig_string.encode()).hexdigest()

    async def authenticate(self) -> bool:
        """Authenticate with iSolarCloud and get access token.
        
        Returns:
            True if authentication successful
        """
        async with self._lock:
            try:
                # Check if token is still valid
                if self._token and time.time() < self._token_expires:
                    return True

                session = await self._get_session()
                
                # Prepare login request
                params = {
                    "user_account": self.username,
                    "user_password": hashlib.md5(self.password.encode()).hexdigest(),
                    "appkey": self.api_key or "default",
                }
                
                # Add signature
                params["sign"] = self._generate_signature(params)
                
                async with session.post(CLOUD_API_TOKEN_URL, json=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get("result_code") == 1:
                            result_data = data.get("result_data", {})
                            self._token = result_data.get("token")
                            # Token typically valid for 24 hours
                            self._token_expires = time.time() + (23 * 3600)
                            _LOGGER.info("Successfully authenticated with iSolarCloud")
                            return True
                        else:
                            _LOGGER.error("Authentication failed: %s", data.get("result_msg"))
                            return False
                    else:
                        _LOGGER.error("Authentication request failed with status %s", response.status)
                        return False
                        
            except Exception as err:
                _LOGGER.error("Error during authentication: %s", err)
                return False

    async def _make_request(
        self,
        url: str,
        params: dict[str, Any],
    ) -> Optional[dict[str, Any]]:
        """Make authenticated API request.
        
        Args:
            url: API endpoint URL
            params: Request parameters
            
        Returns:
            Response data or None if request failed
        """
        # Ensure we're authenticated
        if not await self.authenticate():
            return None
            
        try:
            session = await self._get_session()
            
            # Add token and signature
            params["token"] = self._token
            params["sign"] = self._generate_signature(params)
            
            async with session.post(url, json=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("result_code") == 1:
                        return data.get("result_data")
                    else:
                        _LOGGER.error("API request failed: %s", data.get("result_msg"))
                        return None
                else:
                    _LOGGER.error("API request failed with status %s", response.status)
                    return None
                    
        except Exception as err:
            _LOGGER.error("Error making API request: %s", err)
            return None

    async def get_plant_list(self) -> Optional[list[dict[str, Any]]]:
        """Get list of power plants/stations.
        
        Returns:
            List of plant dictionaries or None if request failed
        """
        params = {
            "curPage": 1,
            "size": 100,
        }
        
        result = await self._make_request(CLOUD_API_PLANT_LIST_URL, params)
        
        if result:
            return result.get("pageList", [])
        return None

    async def get_device_list(self, plant_id: str) -> Optional[list[dict[str, Any]]]:
        """Get list of devices in a plant.
        
        Args:
            plant_id: Plant/station ID
            
        Returns:
            List of device dictionaries or None if request failed
        """
        params = {
            "ps_id": plant_id,
        }
        
        result = await self._make_request(CLOUD_API_DEVICE_LIST_URL, params)
        
        if result:
            return result.get("list", [])
        return None

    async def get_realtime_data(
        self,
        device_sn: str,
    ) -> Optional[dict[str, Any]]:
        """Get realtime data for a device.
        
        Args:
            device_sn: Device serial number
            
        Returns:
            Device data dictionary or None if request failed
        """
        params = {
            "dev_sn": device_sn,
        }
        
        result = await self._make_request(CLOUD_API_REALTIME_DATA_URL, params)
        
        if result:
            return self._parse_cloud_data(result)
        return None

    def _parse_cloud_data(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        """Parse cloud API data into standardized format.
        
        Args:
            raw_data: Raw API response data
            
        Returns:
            Parsed data dictionary
        """
        parsed = {}
        
        try:
            # Cloud API returns data as key-value pairs
            data_list = raw_data.get("data_list", [])
            
            for item in data_list:
                point_name = item.get("point_name", "")
                value = item.get("data_value")
                
                # Map cloud point names to our sensor keys
                # This mapping may need adjustment based on actual API response
                mapping = {
                    "p13003": "pv_power",
                    "p13022": "battery_soc",
                    "p13020": "battery_power",
                    "p13009": "grid_export_power",
                    "p13007": "load_power",
                    "p5002": "daily_pv_generation",
                    "p13025": "daily_battery_charge",
                    "p13026": "daily_battery_discharge",
                    "p13034": "daily_grid_export",
                    "p13035": "daily_grid_import",
                }
                
                if point_name in mapping and value is not None:
                    parsed[mapping[point_name]] = float(value)
                    
        except Exception as err:
            _LOGGER.error("Error parsing cloud data: %s", err)
            
        return parsed

    async def test_connection(self) -> bool:
        """Test if cloud connection is working.
        
        Returns:
            True if connection test successful
        """
        try:
            return await self.authenticate()
        except Exception as err:
            _LOGGER.error("Cloud connection test failed: %s", err)
            return False

    async def read_all_data(
        self,
        device_sn: str,
    ) -> dict[str, Any]:
        """Read all available data from cloud API.
        
        Args:
            device_sn: Device serial number
            
        Returns:
            Dictionary with sensor keys and values
        """
        data = await self.get_realtime_data(device_sn)
        return data if data else {}
