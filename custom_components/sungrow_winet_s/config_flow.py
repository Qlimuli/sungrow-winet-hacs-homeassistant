"""Config flow for Sungrow WINET-S Inverter integration."""
import logging
from typing import Any, Optional

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_USERNAME, CONF_PASSWORD
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .api import SungrowModbusClient, SungrowHTTPClient, SungrowCloudClient
from .const import (
    DOMAIN,
    DEFAULT_NAME,
    DEFAULT_PORT_MODBUS,
    DEFAULT_PORT_HTTP,
    DEFAULT_MODBUS_SLAVE_ID,
    DEFAULT_SCAN_INTERVAL,
    CONF_CONNECTION_TYPE,
    CONF_MODBUS_SLAVE_ID,
    CONF_API_KEY,
    CONF_DEVICE_SN,
    CONF_SCAN_INTERVAL,
    CONNECTION_TYPE_MODBUS,
    CONNECTION_TYPE_HTTP,
    CONNECTION_TYPE_CLOUD,
)

_LOGGER = logging.getLogger(__name__)


async def validate_modbus_connection(
    hass: HomeAssistant, host: str, port: int, slave_id: int
) -> dict[str, Any]:
    """Validate Modbus TCP connection to inverter.
    
    Args:
        hass: Home Assistant instance
        host: Inverter/WINET-S IP address
        port: Modbus port
        slave_id: Modbus slave ID
        
    Returns:
        Dict with device info
        
    Raises:
        Exception: If connection fails
    """
    client = SungrowModbusClient(host, port, slave_id)
    
    if not await client.test_connection():
        raise Exception("Cannot connect to inverter via Modbus TCP")
    
    await client.disconnect()
    
    return {"title": f"{DEFAULT_NAME} ({host})"}


async def validate_http_connection(
    hass: HomeAssistant, host: str, port: int
) -> dict[str, Any]:
    """Validate HTTP connection to WINET-S.
    
    Args:
        hass: Home Assistant instance
        host: WINET-S IP address
        port: HTTP port
        
    Returns:
        Dict with device info
        
    Raises:
        Exception: If connection fails
    """
    client = SungrowHTTPClient(host, port)
    
    if not await client.test_connection():
        raise Exception("Cannot connect to WINET-S via HTTP")
    
    await client.close()
    
    return {"title": f"{DEFAULT_NAME} ({host})"}


async def validate_cloud_connection(
    hass: HomeAssistant, username: str, password: str, api_key: Optional[str]
) -> dict[str, Any]:
    """Validate cloud API connection.
    
    Args:
        hass: Home Assistant instance
        username: iSolarCloud username
        password: iSolarCloud password
        api_key: API key (optional)
        
    Returns:
        Dict with device info
        
    Raises:
        Exception: If connection fails
    """
    client = SungrowCloudClient(username, password, api_key)
    
    if not await client.test_connection():
        raise Exception("Cannot authenticate with iSolarCloud")
    
    await client.close()
    
    return {"title": f"{DEFAULT_NAME} (Cloud)"}


class SungrowConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Sungrow WINET-S Inverter."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self.connection_type: Optional[str] = None
        self.data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: Optional[dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step - choose connection type."""
        if user_input is not None:
            self.connection_type = user_input[CONF_CONNECTION_TYPE]
            
            if self.connection_type == CONNECTION_TYPE_MODBUS:
                return await self.async_step_modbus()
            elif self.connection_type == CONNECTION_TYPE_HTTP:
                return await self.async_step_http()
            elif self.connection_type == CONNECTION_TYPE_CLOUD:
                return await self.async_step_cloud()

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_CONNECTION_TYPE,
                    default=CONNECTION_TYPE_MODBUS,
                ): vol.In(
                    {
                        CONNECTION_TYPE_MODBUS: "Modbus TCP (Local)",
                        CONNECTION_TYPE_HTTP: "HTTP API (Local)",
                        CONNECTION_TYPE_CLOUD: "iSolarCloud (Internet)",
                    }
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            description_placeholders={
                "name": DEFAULT_NAME,
            },
        )

    async def async_step_modbus(
        self, user_input: Optional[dict[str, Any]] = None
    ) -> FlowResult:
        """Handle Modbus TCP configuration."""
        errors = {}

        if user_input is not None:
            try:
                info = await validate_modbus_connection(
                    self.hass,
                    user_input[CONF_HOST],
                    user_input[CONF_PORT],
                    user_input[CONF_MODBUS_SLAVE_ID],
                )
                
                # Store configuration
                self.data = {
                    CONF_CONNECTION_TYPE: CONNECTION_TYPE_MODBUS,
                    CONF_HOST: user_input[CONF_HOST],
                    CONF_PORT: user_input[CONF_PORT],
                    CONF_MODBUS_SLAVE_ID: user_input[CONF_MODBUS_SLAVE_ID],
                }
                
                # Create entry
                return self.async_create_entry(title=info["title"], data=self.data)
                
            except Exception as err:
                _LOGGER.error("Error connecting via Modbus: %s", err)
                errors["base"] = "cannot_connect"

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST): cv.string,
                vol.Required(CONF_PORT, default=DEFAULT_PORT_MODBUS): cv.port,
                vol.Required(
                    CONF_MODBUS_SLAVE_ID, default=DEFAULT_MODBUS_SLAVE_ID
                ): cv.positive_int,
            }
        )

        return self.async_show_form(
            step_id="modbus",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "name": DEFAULT_NAME,
            },
        )

    async def async_step_http(
        self, user_input: Optional[dict[str, Any]] = None
    ) -> FlowResult:
        """Handle HTTP API configuration."""
        errors = {}

        if user_input is not None:
            try:
                info = await validate_http_connection(
                    self.hass,
                    user_input[CONF_HOST],
                    user_input[CONF_PORT],
                )
                
                # Store configuration
                self.data = {
                    CONF_CONNECTION_TYPE: CONNECTION_TYPE_HTTP,
                    CONF_HOST: user_input[CONF_HOST],
                    CONF_PORT: user_input[CONF_PORT],
                }
                
                # Create entry
                return self.async_create_entry(title=info["title"], data=self.data)
                
            except Exception as err:
                _LOGGER.error("Error connecting via HTTP: %s", err)
                errors["base"] = "cannot_connect"

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST): cv.string,
                vol.Required(CONF_PORT, default=DEFAULT_PORT_HTTP): cv.port,
            }
        )

        return self.async_show_form(
            step_id="http",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "name": DEFAULT_NAME,
            },
        )

    async def async_step_cloud(
        self, user_input: Optional[dict[str, Any]] = None
    ) -> FlowResult:
        """Handle cloud API configuration."""
        errors = {}

        if user_input is not None:
            try:
                info = await validate_cloud_connection(
                    self.hass,
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                    user_input.get(CONF_API_KEY),
                )
                
                # Store configuration
                self.data = {
                    CONF_CONNECTION_TYPE: CONNECTION_TYPE_CLOUD,
                    CONF_USERNAME: user_input[CONF_USERNAME],
                    CONF_PASSWORD: user_input[CONF_PASSWORD],
                    CONF_API_KEY: user_input.get(CONF_API_KEY),
                    CONF_DEVICE_SN: user_input[CONF_DEVICE_SN],
                }
                
                # Create entry
                return self.async_create_entry(title=info["title"], data=self.data)
                
            except Exception as err:
                _LOGGER.error("Error connecting to cloud: %s", err)
                errors["base"] = "cannot_connect"

        data_schema = vol.Schema(
            {
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
                vol.Optional(CONF_API_KEY): cv.string,
                vol.Required(CONF_DEVICE_SN): cv.string,
            }
        )

        return self.async_show_form(
            step_id="cloud",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "name": DEFAULT_NAME,
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> "SungrowOptionsFlow":
        """Get the options flow for this handler."""
        return SungrowOptionsFlow(config_entry)


class SungrowOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Sungrow integration."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: Optional[dict[str, Any]] = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=self.config_entry.options.get(
                        CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                    ),
                ): cv.positive_int,
            }
        )

        return self.async_show_form(step_id="init", data_schema=data_schema)
