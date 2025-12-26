"""Data update coordinator for Sungrow WINET-S integration."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import SungrowCloudClient, SungrowHttpClient, SungrowModbusClient
from .const import (
    CONF_ACCESS_KEY,
    CONF_API_KEY,
    CONF_CONNECTION_MODE,
    CONF_DEVICE_SN,
    CONF_MODBUS_PORT,
    CONF_MODBUS_SLAVE_ID,
    CONF_PLANT_ID,
    CONF_RSA_PRIVATE_KEY,
    CONNECTION_MODE_CLOUD,
    CONNECTION_MODE_HTTP,
    CONNECTION_MODE_MODBUS,
    DEFAULT_MODBUS_PORT,
    DEFAULT_MODBUS_SLAVE_ID,
    DEFAULT_SCAN_INTERVAL_CLOUD,
    DEFAULT_SCAN_INTERVAL_LOCAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


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

    def _init_client(self) -> None:
        """Initialize the API client based on connection mode."""
        config = self.entry.data

        if self._connection_mode == CONNECTION_MODE_MODBUS:
            self._client = SungrowModbusClient(
                host=config[CONF_HOST],
                port=config.get(CONF_MODBUS_PORT, DEFAULT_MODBUS_PORT),
                slave_id=config.get(CONF_MODBUS_SLAVE_ID, DEFAULT_MODBUS_SLAVE_ID),
            )
        elif self._connection_mode == CONNECTION_MODE_HTTP:
            self._client = SungrowHttpClient(
                host=config[CONF_HOST],
                port=config.get(CONF_PORT, 80),
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

            if not data:
                raise UpdateFailed("No data received from inverter")

            # Add metadata
            data["_connection_mode"] = self._connection_mode
            data["_last_update"] = self.hass.util.dt.utcnow().isoformat()

            return data

        except Exception as err:
            _LOGGER.error("Error fetching data: %s", err)
            raise UpdateFailed(f"Error communicating with inverter: {err}") from err

    async def async_shutdown(self) -> None:
        """Shutdown the coordinator and close connections."""
        if self._client:
            await self._client.disconnect()

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self.entry.entry_id)},
            "name": f"Sungrow Inverter ({self.entry.data.get(CONF_HOST, 'Cloud')})",
            "manufacturer": "Sungrow",
            "model": self.data.get("device_model", "WINET-S"),
            "sw_version": self.data.get("firmware") if self.data else None,
        }
