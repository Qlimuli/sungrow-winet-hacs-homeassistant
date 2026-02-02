"""HTTP API client for Sungrow WINET-S local access."""
from __future__ import annotations

import asyncio
import hashlib
import logging
import time
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)


class SungrowHttpClient:
    """Client for communicating with Sungrow inverter via HTTP API."""

    def __init__(
        self,
        host: str,
        port: int = 80,
        username: str = "admin",
        password: str = "pw8888",
    ) -> None:
        """Initialize the HTTP client."""
        self._host = host
        self._port = int(port)  # Ensure port is integer to avoid URLs like "http://host:80.0/..."
        self._username = username
        self._password = password
        self._base_url = f"http://{host}:{self._port}"
        self._session: aiohttp.ClientSession | None = None
        self._token: str | None = None
        
        # Stability improvements
        self._retry_count = 3
        self._retry_delay = 1.0
        self._last_valid_data: dict[str, Any] = {}
        self._last_successful_read: float = 0

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def connect(self) -> bool:
        """Authenticate and get session token."""
        try:
            session = await self._get_session()

            # Hash password
            password_hash = hashlib.md5(self._password.encode()).hexdigest()

            auth_payload = {
                "lang": "en_us",
                "service": "login",
                "username": self._username,
                "passwd": password_hash,
            }

            async with session.post(
                f"{self._base_url}/inverter/web",
                json=auth_payload,
            ) as response:
                if response.status != 200:
                    _LOGGER.error("HTTP auth failed with status %s", response.status)
                    return False

                data = await response.json()
                if data.get("result_code") == 1:
                    self._token = data.get("result_data", {}).get("token")
                    _LOGGER.info("Successfully authenticated with WINET-S HTTP API")
                    return True
                else:
                    _LOGGER.error("HTTP auth failed: %s", data.get("result_msg"))
                    return False

        except aiohttp.ClientError as err:
            _LOGGER.error("HTTP connection error: %s", err)
            return False
        except Exception as err:
            _LOGGER.error("HTTP auth error: %s", err)
            return False

    async def disconnect(self) -> None:
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
        self._session = None
        self._token = None

    async def _request(self, service: str, params: dict | None = None) -> dict[str, Any] | None:
        """Make authenticated API request."""
        if not self._token:
            if not await self.connect():
                return None

        try:
            session = await self._get_session()

            payload = {
                "lang": "en_us",
                "token": self._token,
                "service": service,
            }
            if params:
                payload.update(params)

            async with session.post(
                f"{self._base_url}/inverter/web",
                json=payload,
            ) as response:
                if response.status != 200:
                    return None

                data = await response.json()
                if data.get("result_code") == 1:
                    return data.get("result_data", {})
                elif data.get("result_code") == -1:
                    # Token expired, re-authenticate
                    self._token = None
                    return await self._request(service, params)
                else:
                    _LOGGER.warning("API request failed: %s", data.get("result_msg"))
                    return None

        except Exception as err:
            _LOGGER.error("HTTP request error: %s", err)
            return None

    async def _request_with_retry(self, service: str, params: dict | None = None) -> dict[str, Any] | None:
        """Make API request with retry logic."""
        for attempt in range(self._retry_count):
            try:
                result = await self._request(service, params)
                if result is not None:
                    return result
                    
                if attempt < self._retry_count - 1:
                    await asyncio.sleep(self._retry_delay * (attempt + 1))
                    
            except Exception as err:
                _LOGGER.debug(
                    "HTTP request attempt %d failed for %s: %s",
                    attempt + 1,
                    service,
                    err,
                )
                if attempt < self._retry_count - 1:
                    await asyncio.sleep(self._retry_delay * (attempt + 1))
        
        return None

    async def read_all_data(self) -> dict[str, Any]:
        """Read all available data from HTTP API."""
        data: dict[str, Any] = {}
        errors = 0

        # Get real-time data
        realtime = await self._request_with_retry("real_time_data")
        if realtime:
            parsed = self._parse_realtime_data(realtime)
            data.update(parsed)
            # Cache valid data
            for key, value in parsed.items():
                if value is not None:
                    self._last_valid_data[key] = value
        else:
            errors += 1
            # Use cached data if available
            for key in ["pv_power", "daily_pv_energy", "total_pv_energy", "grid_power", 
                       "load_power", "battery_soc", "battery_power", "inverter_temp", "running_state"]:
                if key in self._last_valid_data:
                    data[key] = self._last_valid_data[key]

        # Get device info
        device_info = await self._request_with_retry("device_info")
        if device_info:
            data["device_model"] = device_info.get("dev_model", "Unknown")
            data["device_sn"] = device_info.get("dev_sn", "Unknown")
            data["firmware"] = device_info.get("sw_ver", "Unknown")
            # Cache device info
            self._last_valid_data["device_model"] = data["device_model"]
            self._last_valid_data["device_sn"] = data["device_sn"]
            self._last_valid_data["firmware"] = data["firmware"]
        else:
            errors += 1
            # Use cached device info
            for key in ["device_model", "device_sn", "firmware"]:
                if key in self._last_valid_data:
                    data[key] = self._last_valid_data[key]

        # Get statistics
        statistics = await self._request_with_retry("statistics")
        if statistics:
            parsed = self._parse_statistics(statistics)
            data.update(parsed)
            # Cache valid data
            for key, value in parsed.items():
                if value is not None:
                    self._last_valid_data[key] = value
        else:
            errors += 1
            # Use cached statistics
            for key in ["daily_import_energy", "daily_export_energy", "daily_battery_charge",
                       "daily_battery_discharge", "daily_load_energy"]:
                if key in self._last_valid_data:
                    data[key] = self._last_valid_data[key]

        if errors == 0:
            self._last_successful_read = time.time()
        elif errors > 0:
            _LOGGER.warning("HTTP read completed with %d errors", errors)

        return data

    def _parse_realtime_data(self, raw: dict) -> dict[str, Any]:
        """Parse real-time data response."""
        parsed = {}

        # Map HTTP API fields to our standard keys
        field_mapping = {
            "p_pv": "pv_power",
            "e_today": "daily_pv_energy",
            "e_total": "total_pv_energy",
            "p_grid": "grid_power",
            "p_load": "load_power",
            "soc": "battery_soc",
            "p_bat": "battery_power",
            "temp_inv": "inverter_temp",
            "status": "running_state",
        }

        for api_key, our_key in field_mapping.items():
            if api_key in raw:
                value = raw[api_key]
                if isinstance(value, (int, float)):
                    parsed[our_key] = round(float(value), 2)
                else:
                    parsed[our_key] = value

        return parsed

    def _parse_statistics(self, raw: dict) -> dict[str, Any]:
        """Parse statistics response."""
        parsed = {}

        stat_mapping = {
            "e_import_today": "daily_import_energy",
            "e_export_today": "daily_export_energy",
            "e_bat_charge_today": "daily_battery_charge",
            "e_bat_discharge_today": "daily_battery_discharge",
            "e_load_today": "daily_load_energy",
        }

        for api_key, our_key in stat_mapping.items():
            if api_key in raw:
                parsed[our_key] = round(float(raw[api_key]), 2)

        return parsed

    async def test_connection(self) -> bool:
        """Test connection to HTTP API."""
        try:
            return await self.connect()
        except Exception:
            return False
