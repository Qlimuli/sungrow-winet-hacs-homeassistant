"""Data coordinator for Sungrow WINET-S integration."""
import asyncio
import logging
from datetime import timedelta
from typing import Any, Optional

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import SungrowModbusClient, SungrowHTTPClient, SungrowCloudClient
from .const import (
    DOMAIN,
    CONNECTION_TYPE_MODBUS,
    CONNECTION_TYPE_HTTP,
    CONNECTION_TYPE_CLOUD,
    UPDATE_INTERVAL_LOCAL,
    UPDATE_INTERVAL_CLOUD,
)

_LOGGER = logging.getLogger(__name__)


class SungrowDataCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Sungrow inverter data with intelligent fallback."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry_data: dict[str, Any],
    ) -> None:
        """Initialize the coordinator.
        
        Args:
            hass: Home Assistant instance
            config_entry_data: Configuration data from config entry
        """
        self.config_data = config_entry_data
        self.connection_type = config_entry_data.get("connection_type", CONNECTION_TYPE_MODBUS)
        
        # Initialize clients based on connection type
        self.modbus_client: Optional[SungrowModbusClient] = None
        self.http_client: Optional[SungrowHTTPClient] = None
        self.cloud_client: Optional[SungrowCloudClient] = None
        
        # Set up primary client
        if self.connection_type == CONNECTION_TYPE_MODBUS:
            self.modbus_client = SungrowModbusClient(
                host=config_entry_data["host"],
                port=config_entry_data.get("port", 502),
                slave_id=config_entry_data.get("modbus_slave_id", 1),
            )
            update_interval = UPDATE_INTERVAL_LOCAL
            
        elif self.connection_type == CONNECTION_TYPE_HTTP:
            self.http_client = SungrowHTTPClient(
                host=config_entry_data["host"],
                port=config_entry_data.get("port", 8082),
            )
            update_interval = UPDATE_INTERVAL_LOCAL
            
        elif self.connection_type == CONNECTION_TYPE_CLOUD:
            self.cloud_client = SungrowCloudClient(
                username=config_entry_data["username"],
                password=config_entry_data["password"],
                api_key=config_entry_data.get("api_key"),
            )
            update_interval = UPDATE_INTERVAL_CLOUD
        else:
            update_interval = UPDATE_INTERVAL_LOCAL
            
        # Track connection failures for intelligent fallback
        self.consecutive_failures = 0
        self.max_failures_before_fallback = 3
        self.fallback_attempted = False
        
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_coordinator",
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from inverter with intelligent fallback.
        
        Returns:
            Dictionary containing sensor data
            
        Raises:
            UpdateFailed: If all data sources fail
        """
        # Try primary connection method
        try:
            data = await self._fetch_from_primary_source()
            
            if data:
                # Reset failure counter on success
                self.consecutive_failures = 0
                self.fallback_attempted = False
                return data
            else:
                self.consecutive_failures += 1
                
        except Exception as err:
            self.consecutive_failures += 1
            _LOGGER.error("Error fetching from primary source: %s", err)
        
        # Attempt fallback if primary fails repeatedly
        if self.consecutive_failures >= self.max_failures_before_fallback:
            if not self.fallback_attempted:
                _LOGGER.warning(
                    "Primary connection failed %d times, attempting fallback",
                    self.consecutive_failures
                )
                self.fallback_attempted = True
                
            try:
                data = await self._fetch_from_fallback_source()
                if data:
                    return data
            except Exception as err:
                _LOGGER.error("Fallback source also failed: %s", err)
        
        raise UpdateFailed("Failed to fetch data from all available sources")

    async def _fetch_from_primary_source(self) -> Optional[dict[str, Any]]:
        """Fetch data from primary configured source.
        
        Returns:
            Data dictionary or None if fetch failed
        """
        if self.connection_type == CONNECTION_TYPE_MODBUS and self.modbus_client:
            _LOGGER.debug("Fetching data via Modbus TCP")
            return await self.modbus_client.read_all_data()
            
        elif self.connection_type == CONNECTION_TYPE_HTTP and self.http_client:
            _LOGGER.debug("Fetching data via HTTP API")
            return await self.http_client.read_all_data()
            
        elif self.connection_type == CONNECTION_TYPE_CLOUD and self.cloud_client:
            _LOGGER.debug("Fetching data via Cloud API")
            device_sn = self.config_data.get("device_sn")
            if device_sn:
                return await self.cloud_client.read_all_data(device_sn)
            else:
                _LOGGER.error("No device serial number configured for cloud access")
                return None
                
        return None

    async def _fetch_from_fallback_source(self) -> Optional[dict[str, Any]]:
        """Attempt to fetch data from fallback sources.
        
        Fallback priority:
        1. Modbus -> HTTP -> Cloud
        2. HTTP -> Modbus -> Cloud
        3. Cloud -> (no fallback, already most resilient)
        
        Returns:
            Data dictionary or None if all fallbacks failed
        """
        # If primary was local (Modbus or HTTP), try the other local method first
        if self.connection_type == CONNECTION_TYPE_MODBUS:
            # Try HTTP fallback
            if "host" in self.config_data:
                _LOGGER.info("Attempting HTTP fallback")
                if not self.http_client:
                    self.http_client = SungrowHTTPClient(
                        host=self.config_data["host"],
                        port=8082,
                    )
                data = await self.http_client.read_all_data()
                if data:
                    return data
                    
        elif self.connection_type == CONNECTION_TYPE_HTTP:
            # Try Modbus fallback
            if "host" in self.config_data:
                _LOGGER.info("Attempting Modbus fallback")
                if not self.modbus_client:
                    self.modbus_client = SungrowModbusClient(
                        host=self.config_data["host"],
                        port=502,
                        slave_id=1,
                    )
                data = await self.modbus_client.read_all_data()
                if data:
                    return data
        
        # If local methods failed and cloud credentials are available, try cloud
        if self.connection_type != CONNECTION_TYPE_CLOUD:
            if "username" in self.config_data and "password" in self.config_data:
                _LOGGER.info("Attempting cloud API fallback")
                if not self.cloud_client:
                    self.cloud_client = SungrowCloudClient(
                        username=self.config_data["username"],
                        password=self.config_data["password"],
                        api_key=self.config_data.get("api_key"),
                    )
                device_sn = self.config_data.get("device_sn")
                if device_sn:
                    data = await self.cloud_client.read_all_data(device_sn)
                    if data:
                        return data
        
        return None

    async def async_shutdown(self) -> None:
        """Shutdown coordinator and close connections."""
        if self.modbus_client:
            await self.modbus_client.disconnect()
        if self.http_client:
            await self.http_client.close()
        if self.cloud_client:
            await self.cloud_client.close()
