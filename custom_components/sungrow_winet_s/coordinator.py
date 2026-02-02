"""Data update coordinator for Sungrow WINET-S integration."""
from __future__ import annotations

import asyncio
import logging
import time
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import SungrowCloudClient, SungrowHttpClient, SungrowModbusClient
from .const import (
    CONF_ACCESS_KEY,
    CONF_API_KEY,
    CONF_CONNECTION_MODE,
    CONF_DEVICE_SN,
    CONF_MODBUS_PORT,
    CONF_MODBUS_SLAVE_ID,
    CONF_MODBUS_USE_TLS,
    CONF_PLANT_ID,
    CONF_RSA_PRIVATE_KEY,
    CONNECTION_MODE_CLOUD,
    CONNECTION_MODE_HTTP,
    CONNECTION_MODE_MODBUS,
    DEFAULT_MODBUS_PORT,
    DEFAULT_MODBUS_SLAVE_ID,
    DEFAULT_MODBUS_USE_TLS,
    DEFAULT_SCAN_INTERVAL_CLOUD,
    DEFAULT_SCAN_INTERVAL_LOCAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

# Maximum age of cached data before considered stale (in seconds)
MAX_DATA_AGE = 300  # 5 minutes


class SungrowDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for fetching data from Sungrow inverter."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        self._connection_mode = entry.data.get(CONF_CONNECTION_MODE, CONNECTION_MODE_MODBUS)

        # Determine update interval based on connection mode
        if self._connection_mode == CONNECTION_MODE_CLOUD:
            update_interval = DEFAULT_SCAN_INTERVAL_CLOUD
        else:
            update_interval = DEFAULT_SCAN_INTERVAL_LOCAL

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=update_interval,
        )

        # Initialize the appropriate client
        self._client: SungrowModbusClient | SungrowHttpClient | SungrowCloudClient | None = None
        self._init_client()
        
        # Stability improvements
        self._last_valid_data: dict[str, Any] = {}
        self._last_successful_update: float = 0
        self._consecutive_failures = 0
        self._max_consecutive_failures = 10  # More tolerant before reconnect
        self._reconnect_delay = 5.0

    def _init_client(self) -> None:
        """Initialize the API client based on connection mode."""
        config = self.entry.data

        if self._connection_mode == CONNECTION_MODE_MODBUS:
            self._client = SungrowModbusClient(
                host=config[CONF_HOST],
                port=int(config.get(CONF_MODBUS_PORT, DEFAULT_MODBUS_PORT)),
                slave_id=int(config.get(CONF_MODBUS_SLAVE_ID, DEFAULT_MODBUS_SLAVE_ID)),
                use_tls=config.get(CONF_MODBUS_USE_TLS, DEFAULT_MODBUS_USE_TLS),
            )
        elif self._connection_mode == CONNECTION_MODE_HTTP:
            self._client = SungrowHttpClient(
                host=config[CONF_HOST],
                port=int(config.get(CONF_PORT, 80)),
                username=config.get(CONF_USERNAME, "admin"),
                password=config.get(CONF_PASSWORD, "pw8888"),
            )
        elif self._connection_mode == CONNECTION_MODE_CLOUD:
            self._client = SungrowCloudClient(
                api_key=config[CONF_API_KEY],
                access_key=config[CONF_ACCESS_KEY],
                rsa_private_key=config[CONF_RSA_PRIVATE_KEY],
                plant_id=config.get(CONF_PLANT_ID),
                device_sn=config.get(CONF_DEVICE_SN),
            )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the inverter."""
        if not self._client:
            raise UpdateFailed("No client configured")

        try:
            data = await self._client.read_all_data()

            # Consider partial data as success - don't fail if we got some data
            if data:
                # We got data - this is a success even if some values are missing
                self._consecutive_failures = 0
                self._last_successful_update = time.time()
                
                # Merge with cached data to fill in any missing values
                data = self._merge_with_cached_data(data)
                
                # Update cache with new valid data
                self._update_cache(data)

                # Add metadata
                data["_connection_mode"] = self._connection_mode
                data["_last_update"] = dt_util.utcnow().isoformat()

                return data
            
            # No data at all - this is a problem
            self._consecutive_failures += 1
            _LOGGER.debug(
                "No data received (attempt %d/%d)",
                self._consecutive_failures,
                self._max_consecutive_failures,
            )
            
            # Return cached data if available and not too old
            if self._last_valid_data and (time.time() - self._last_successful_update) < MAX_DATA_AGE:
                _LOGGER.debug("Using cached data from last successful update")
                cached = self._merge_with_cached_data({})
                cached["_connection_mode"] = self._connection_mode
                cached["_last_update"] = dt_util.utcnow().isoformat()
                cached["_using_cached"] = True
                return cached
            
            # Try to reconnect if too many failures
            if self._consecutive_failures >= self._max_consecutive_failures:
                _LOGGER.warning("Too many consecutive failures, attempting reconnect")
                await self._reconnect()
                
            raise UpdateFailed("No data received from inverter")

        except UpdateFailed:
            raise
        except Exception as err:
            self._consecutive_failures += 1
            _LOGGER.debug(
                "Error fetching data (attempt %d/%d): %s",
                self._consecutive_failures,
                self._max_consecutive_failures,
                err,
            )
            
            # Return cached data if available - don't raise error if we have cache
            if self._last_valid_data and (time.time() - self._last_successful_update) < MAX_DATA_AGE:
                _LOGGER.debug("Returning cached data due to error")
                cached = self._merge_with_cached_data({})
                cached["_connection_mode"] = self._connection_mode
                cached["_last_update"] = dt_util.utcnow().isoformat()
                cached["_using_cached"] = True
                return cached
            
            # Try to reconnect if too many failures
            if self._consecutive_failures >= self._max_consecutive_failures:
                await self._reconnect()
                
            raise UpdateFailed(f"Error communicating with inverter: {err}") from err

    def _merge_with_cached_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Merge new data with cached data, filling in missing values."""
        if not self._last_valid_data:
            return data
        
        merged = dict(self._last_valid_data)
        merged.update(data)
        return merged

    def _update_cache(self, data: dict[str, Any]) -> None:
        """Update the cache with new valid data."""
        for key, value in data.items():
            if key.startswith("_"):
                continue  # Skip metadata
            if value is not None:
                self._last_valid_data[key] = value

    async def _reconnect(self) -> None:
        """Attempt to reconnect to the inverter."""
        _LOGGER.info("Attempting to reconnect to inverter...")
        try:
            if self._client:
                await self._client.disconnect()
            
            await asyncio.sleep(self._reconnect_delay)
            
            if self._client:
                connected = await self._client.connect()
                if connected:
                    _LOGGER.info("Successfully reconnected to inverter")
                    self._consecutive_failures = 0
                else:
                    _LOGGER.warning("Reconnection attempt failed")
        except Exception as err:
            _LOGGER.error("Error during reconnection: %s", err)

    async def async_shutdown(self) -> None:
        """Shutdown the coordinator and close connections."""
        if self._client:
            await self._client.disconnect()

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        serial = self.data.get("serial_number") if self.data else None
        device_type = self.data.get("device_type_code") if self.data else None
        
        arm_version = self.data.get("arm_software_version") if self.data else None
        
        return {
            "identifiers": {(DOMAIN, serial or self.entry.entry_id)},
            "name": f"Sungrow Inverter ({serial or self.entry.data.get(CONF_HOST, 'Cloud')})",
            "manufacturer": "Sungrow",
            "model": f"Device Type {device_type}" if device_type else "WINET-S",
            "serial_number": serial,
            "sw_version": arm_version,
        }
