"""Tests for Sungrow WINET-S config flow."""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.sungrow_winet_s.const import (
    CONF_CONNECTION_MODE,
    CONNECTION_MODE_MODBUS,
    DOMAIN,
)


async def test_user_form_modbus(hass: HomeAssistant, mock_modbus_client: AsyncMock) -> None:
    """Test we can configure via Modbus."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    # Select Modbus connection
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_CONNECTION_MODE: CONNECTION_MODE_MODBUS},
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "modbus"

    # Configure Modbus connection
    with patch(
        "custom_components.sungrow_winet_s.config_flow.SungrowModbusClient",
        return_value=mock_modbus_client,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {"host": "192.168.1.100"},
        )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Sungrow (192.168.1.100)"
    assert result["data"]["host"] == "192.168.1.100"


async def test_connection_error(hass: HomeAssistant) -> None:
    """Test handling of connection errors."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_CONNECTION_MODE: CONNECTION_MODE_MODBUS},
    )

    # Simulate connection failure
    mock_client = AsyncMock()
    mock_client.test_connection = AsyncMock(return_value=False)
    mock_client.disconnect = AsyncMock()

    with patch(
        "custom_components.sungrow_winet_s.config_flow.SungrowModbusClient",
        return_value=mock_client,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {"host": "192.168.1.100"},
        )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"]["base"] == "cannot_connect"
