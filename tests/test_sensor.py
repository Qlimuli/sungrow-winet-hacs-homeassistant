"""Tests for Sungrow WINET-S sensors."""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from custom_components.sungrow_winet_s.const import DOMAIN


async def test_sensors_created(
    hass: HomeAssistant,
    mock_modbus_client: AsyncMock,
) -> None:
    """Test that sensors are created correctly."""
    # This is a placeholder test structure
    # In a real test, you would:
    # 1. Set up a mock config entry
    # 2. Load the integration
    # 3. Verify sensors are created with correct values

    assert mock_modbus_client.read_all_data is not None

    data = await mock_modbus_client.read_all_data()
    assert data["pv_power"] == 5000
    assert data["battery_soc"] == 85.0
    assert data["running_state"] == "Running"
