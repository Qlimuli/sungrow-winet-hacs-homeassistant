"""iSolarCloud API client for Sungrow inverters."""
from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import logging
import time
import uuid
from typing import Any

import aiohttp
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from ..const import ISOLARCLOUD_API_ENDPOINTS, ISOLARCLOUD_BASE_URL

_LOGGER = logging.getLogger(__name__)


class SungrowCloudClient:
    """Client for communicating with Sungrow iSolarCloud API."""

    def __init__(
        self,
        api_key: str,
        access_key: str,
        rsa_private_key: str,
        plant_id: str | None = None,
        device_sn: str | None = None,
    ) -> None:
        """Initialize the cloud client."""
        self._api_key = api_key
        self._access_key = access_key
        self._rsa_private_key = rsa_private_key
        self._plant_id = plant_id
        self._device_sn = device_sn
        self._session: aiohttp.ClientSession | None = None
        self._token: str | None = None
        self._token_expiry: float = 0

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=60)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    def _sign_request(self, params: dict) -> str:
        """Sign request parameters using RSA private key."""
        try:
            # Sort parameters and create signing string
            sorted_params = sorted(params.items())
            sign_string = "&".join(f"{k}={v}" for k, v in sorted_params)

            # Load RSA private key
            private_key = serialization.load_pem_private_key(
                self._rsa_private_key.encode(),
                password=None,
                backend=default_backend(),
            )

            # Sign with SHA256
            signature = private_key.sign(
                sign_string.encode(),
                padding.PKCS1v15(),
                hashes.SHA256(),
            )

            return base64.b64encode(signature).decode()

        except Exception as err:
            _LOGGER.error("Failed to sign request: %s", err)
            raise

    async def _request(
        self,
        endpoint: str,
        params: dict | None = None,
    ) -> dict[str, Any] | None:
        """Make authenticated API request."""
        try:
            session = await self._get_session()

            # Build request parameters
            timestamp = str(int(time.time() * 1000))
            nonce = str(uuid.uuid4())

            request_params = {
                "api_key": self._api_key,
                "timestamp": timestamp,
                "nonce": nonce,
                **(params or {}),
            }

            # Sign the request
            signature = self._sign_request(request_params)

            headers = {
                "Content-Type": "application/json",
                "x-access-key": self._access_key,
                "x-signature": signature,
            }

            url = f"{ISOLARCLOUD_BASE_URL}{endpoint}"

            async with session.post(
                url,
                json=request_params,
                headers=headers,
            ) as response:
                if response.status != 200:
                    _LOGGER.error("Cloud API request failed: HTTP %s", response.status)
                    return None

                data = await response.json()

                if data.get("result_code") == "1" or data.get("success"):
                    return data.get("result_data") or data.get("data", {})
                else:
                    _LOGGER.warning(
                        "Cloud API error: %s",
                        data.get("result_msg") or data.get("message"),
                    )
                    return None

        except aiohttp.ClientError as err:
            _LOGGER.error("Cloud API connection error: %s", err)
            return None
        except Exception as err:
            _LOGGER.error("Cloud API request error: %s", err)
            return None

    async def connect(self) -> bool:
        """Test connection and fetch plant/device info if needed."""
        try:
            # Get plant list if not configured
            if not self._plant_id:
                plants = await self.get_plant_list()
                if plants and len(plants) > 0:
                    self._plant_id = plants[0].get("ps_id")
                    _LOGGER.info("Auto-detected plant ID: %s", self._plant_id)

            # Get device list if not configured
            if self._plant_id and not self._device_sn:
                devices = await self.get_device_list()
                if devices and len(devices) > 0:
                    # Find first inverter device
                    for device in devices:
                        if device.get("dev_type") in [1, 2, 3]:  # Inverter types
                            self._device_sn = device.get("dev_sn")
                            _LOGGER.info("Auto-detected device SN: %s", self._device_sn)
                            break

            return bool(self._plant_id and self._device_sn)

        except Exception as err:
            _LOGGER.error("Cloud connection failed: %s", err)
            return False

    async def disconnect(self) -> None:
        """Close the session."""
        if self._session and not self._session.closed:
            await self._session.close()
        self._session = None

    async def get_plant_list(self) -> list[dict] | None:
        """Get list of power plants/stations."""
        result = await self._request(
            ISOLARCLOUD_API_ENDPOINTS["plant_list"],
            {"curPage": 1, "size": 100},
        )
        if result:
            return result.get("pageList", [])
        return None

    async def get_device_list(self) -> list[dict] | None:
        """Get list of devices for the plant."""
        if not self._plant_id:
            return None

        result = await self._request(
            ISOLARCLOUD_API_ENDPOINTS["device_list"],
            {"ps_id": self._plant_id},
        )
        if result:
            return result.get("pageList", result.get("list", []))
        return None

    async def read_all_data(self) -> dict[str, Any]:
        """Read all available data from cloud API."""
        if not self._device_sn:
            if not await self.connect():
                return {}

        data: dict[str, Any] = {}

        # Get real-time device data
        realtime = await self._request(
            ISOLARCLOUD_API_ENDPOINTS["realtime_data"],
            {
                "ps_id": self._plant_id,
                "dev_sn": self._device_sn,
                "points": "p1,p2,p3,p4,p5,p6,p7,p8,p9,p10",  # Common point IDs
            },
        )

        if realtime:
            data.update(self._parse_cloud_data(realtime))

        # Get minute-level data for more details
        minute_data = await self._request(
            ISOLARCLOUD_API_ENDPOINTS["device_points"],
            {
                "ps_id": self._plant_id,
                "dev_sn": self._device_sn,
            },
        )

        if minute_data:
            data.update(self._parse_minute_data(minute_data))

        return data

    def _parse_cloud_data(self, raw: dict | list) -> dict[str, Any]:
        """Parse cloud API response data."""
        parsed = {}

        # Handle different response formats
        points = raw if isinstance(raw, list) else raw.get("points", [])

        # iSolarCloud point ID mapping (varies by model)
        point_mapping = {
            "p1": "pv_power",
            "p2": "daily_pv_energy",
            "p3": "total_pv_energy",
            "p4": "grid_power",
            "p5": "battery_soc",
            "p6": "battery_power",
            "p7": "load_power",
            "p8": "inverter_temp",
            "p9": "daily_import_energy",
            "p10": "daily_export_energy",
        }

        for point in points:
            point_id = point.get("point_id") or point.get("id")
            value = point.get("value")

            if point_id in point_mapping and value is not None:
                try:
                    parsed[point_mapping[point_id]] = round(float(value), 2)
                except (ValueError, TypeError):
                    parsed[point_mapping[point_id]] = value

        return parsed

    def _parse_minute_data(self, raw: dict) -> dict[str, Any]:
        """Parse minute-level data response."""
        parsed = {}

        # Extract latest values from time series
        data_list = raw.get("dataList", [])
        if data_list:
            latest = data_list[-1] if data_list else {}
            field_mapping = {
                "pv_power": "pv_power",
                "battery_soc": "battery_soc",
                "grid_active_power": "grid_power",
                "load_total_active_power": "load_power",
            }

            for api_key, our_key in field_mapping.items():
                if api_key in latest:
                    try:
                        parsed[our_key] = round(float(latest[api_key]), 2)
                    except (ValueError, TypeError):
                        pass

        return parsed

    async def test_connection(self) -> bool:
        """Test connection to cloud API."""
        try:
            plants = await self.get_plant_list()
            return plants is not None and len(plants) > 0
        except Exception:
            return False

    @property
    def plant_id(self) -> str | None:
        """Return detected plant ID."""
        return self._plant_id

    @property
    def device_sn(self) -> str | None:
        """Return detected device serial number."""
        return self._device_sn
