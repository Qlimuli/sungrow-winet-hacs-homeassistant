"""Config flow for Sungrow WINET-S integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

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
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class SungrowConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Sungrow WINET-S."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._data: dict[str, Any] = {}
        self._connection_mode: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - choose connection mode."""
        errors = {}

        if user_input is not None:
            self._connection_mode = user_input[CONF_CONNECTION_MODE]
            self._data[CONF_CONNECTION_MODE] = self._connection_mode

            if self._connection_mode == CONNECTION_MODE_MODBUS:
                return await self.async_step_modbus()
            elif self._connection_mode == CONNECTION_MODE_HTTP:
                return await self.async_step_http()
            elif self._connection_mode == CONNECTION_MODE_CLOUD:
                return await self.async_step_cloud()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_CONNECTION_MODE, default=CONNECTION_MODE_MODBUS): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[
                                selector.SelectOptionDict(
                                    value=CONNECTION_MODE_MODBUS,
                                    label="Local (Modbus TCP) - Recommended",
                                ),
                                selector.SelectOptionDict(
                                    value=CONNECTION_MODE_HTTP,
                                    label="Local (HTTP API)",
                                ),
                                selector.SelectOptionDict(
                                    value=CONNECTION_MODE_CLOUD,
                                    label="Cloud (iSolarCloud)",
                                ),
                            ],
                            mode=selector.SelectSelectorMode.LIST,
                        )
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_modbus(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle Modbus TCP configuration."""
        errors = {}

        if user_input is not None:
            self._data.update(user_input)

            # Test the connection
            client = SungrowModbusClient(
                host=user_input[CONF_HOST],
                port=user_input.get(CONF_MODBUS_PORT, DEFAULT_MODBUS_PORT),
                slave_id=user_input.get(CONF_MODBUS_SLAVE_ID, DEFAULT_MODBUS_SLAVE_ID),
            )

            try:
                if await client.test_connection():
                    await self.async_set_unique_id(f"sungrow_modbus_{user_input[CONF_HOST]}")
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title=f"Sungrow ({user_input[CONF_HOST]})",
                        data=self._data,
                    )
                else:
                    errors["base"] = "cannot_connect"
            except Exception as err:
                _LOGGER.error("Connection test failed: %s", err)
                errors["base"] = "cannot_connect"
            finally:
                await client.disconnect()

        return self.async_show_form(
            step_id="modbus",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): selector.TextSelector(
                        selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
                    ),
                    vol.Optional(CONF_MODBUS_PORT, default=DEFAULT_MODBUS_PORT): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1, max=65535, mode=selector.NumberSelectorMode.BOX
                        )
                    ),
                    vol.Optional(CONF_MODBUS_SLAVE_ID, default=DEFAULT_MODBUS_SLAVE_ID): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1, max=247, mode=selector.NumberSelectorMode.BOX
                        )
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_http(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle HTTP API configuration."""
        errors = {}

        if user_input is not None:
            self._data.update(user_input)

            # Test the connection
            client = SungrowHttpClient(
                host=user_input[CONF_HOST],
                port=user_input.get(CONF_PORT, 80),
                username=user_input.get(CONF_USERNAME, "admin"),
                password=user_input.get(CONF_PASSWORD, "pw8888"),
            )

            try:
                if await client.test_connection():
                    await self.async_set_unique_id(f"sungrow_http_{user_input[CONF_HOST]}")
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title=f"Sungrow HTTP ({user_input[CONF_HOST]})",
                        data=self._data,
                    )
                else:
                    errors["base"] = "cannot_connect"
            except Exception as err:
                _LOGGER.error("HTTP connection test failed: %s", err)
                errors["base"] = "cannot_connect"
            finally:
                await client.disconnect()

        return self.async_show_form(
            step_id="http",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): selector.TextSelector(
                        selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
                    ),
                    vol.Optional(CONF_PORT, default=80): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1, max=65535, mode=selector.NumberSelectorMode.BOX
                        )
                    ),
                    vol.Optional(CONF_USERNAME, default="admin"): selector.TextSelector(
                        selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
                    ),
                    vol.Optional(CONF_PASSWORD, default="pw8888"): selector.TextSelector(
                        selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_cloud(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle iSolarCloud API configuration."""
        errors = {}

        if user_input is not None:
            self._data.update(user_input)

            # Test the connection
            client = SungrowCloudClient(
                api_key=user_input[CONF_API_KEY],
                access_key=user_input[CONF_ACCESS_KEY],
                rsa_private_key=user_input[CONF_RSA_PRIVATE_KEY],
                plant_id=user_input.get(CONF_PLANT_ID),
                device_sn=user_input.get(CONF_DEVICE_SN),
            )

            try:
                if await client.test_connection():
                    # Store auto-detected plant/device IDs
                    self._data[CONF_PLANT_ID] = client.plant_id
                    self._data[CONF_DEVICE_SN] = client.device_sn

                    await self.async_set_unique_id(f"sungrow_cloud_{client.device_sn or user_input[CONF_API_KEY][:8]}")
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title=f"Sungrow Cloud ({client.device_sn or 'iSolarCloud'})",
                        data=self._data,
                    )
                else:
                    errors["base"] = "invalid_auth"
            except Exception as err:
                _LOGGER.error("Cloud connection test failed: %s", err)
                errors["base"] = "invalid_auth"
            finally:
                await client.disconnect()

        return self.async_show_form(
            step_id="cloud",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): selector.TextSelector(
                        selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
                    ),
                    vol.Required(CONF_ACCESS_KEY): selector.TextSelector(
                        selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
                    ),
                    vol.Required(CONF_RSA_PRIVATE_KEY): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                            multiline=True,
                        )
                    ),
                    vol.Optional(CONF_PLANT_ID): selector.TextSelector(
                        selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
                    ),
                    vol.Optional(CONF_DEVICE_SN): selector.TextSelector(
                        selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
                    ),
                }
            ),
            errors=errors,
            description_placeholders={
                "api_portal": "https://developer-api.isolarcloud.com/"
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return SungrowOptionsFlow(config_entry)


class SungrowOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Sungrow integration."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_mode = self._config_entry.data.get(CONF_CONNECTION_MODE, CONNECTION_MODE_MODBUS)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        "scan_interval",
                        default=30 if current_mode != CONNECTION_MODE_CLOUD else 300,
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=10,
                            max=3600,
                            unit_of_measurement="seconds",
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    ),
                }
            ),
        )
