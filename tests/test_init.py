"""Tests for Sungrow WINET-S integration."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from custom_components.sungrow_winet_s import async_setup_entry, async_unload_entry
from custom_components.sungrow_winet_s.const import DOMAIN


@pytest.fixture
def mock_config_entry():
    """Mock a config entry."""
    return MagicMock(spec=ConfigEntry, entry_id="test_entry_id", data={
        "connection_type": "modbus",
        "host": "192.168.1.100",
        "port": 502,
        "modbus_slave_id": 1,
    })


@pytest.fixture
def mock_coordinator():
    """Mock the coordinator."""
    coordinator = MagicMock()
    coordinator.async_config_entry_first_refresh = AsyncMock()
    coordinator.last_update_success = True
    coordinator.data = {"pv_power": 1000.0}
    return coordinator


@pytest.mark.asyncio
async def test_setup_entry(hass: HomeAssistant, mock_config_entry, mock_coordinator):
    """Test setting up the integration."""
    with patch(
        "custom_components.sungrow_winet_s.SungrowDataCoordinator",
        return_value=mock_coordinator,
    ):
        result = await async_setup_entry(hass, mock_config_entry)
        assert result is True
        assert DOMAIN in hass.data
        assert mock_config_entry.entry_id in hass.data[DOMAIN]


@pytest.mark.asyncio
async def test_unload_entry(hass: HomeAssistant, mock_config_entry, mock_coordinator):
    """Test unloading the integration."""
    # Setup first
    with patch(
        "custom_components.sungrow_winet_s.SungrowDataCoordinator",
        return_value=mock_coordinator,
    ):
        await async_setup_entry(hass, mock_config_entry)
    
    # Now unload
    mock_coordinator.async_shutdown = AsyncMock()
    result = await async_unload_entry(hass, mock_config_entry)
    assert result is True
    mock_coordinator.async_shutdown.assert_called_once()
