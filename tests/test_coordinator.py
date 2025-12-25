"""Tests for coordinator."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.sungrow_winet_s.coordinator import SungrowDataCoordinator
from custom_components.sungrow_winet_s.const import CONNECTION_TYPE_MODBUS


@pytest.fixture
def mock_modbus_client():
    """Mock Modbus client."""
    client = MagicMock()
    client.read_all_data = AsyncMock(return_value={"pv_power": 1500.0, "battery_soc": 85.0})
    client.disconnect = AsyncMock()
    return client


@pytest.mark.asyncio
async def test_coordinator_fetch_data(hass: HomeAssistant, mock_modbus_client):
    """Test coordinator fetching data."""
    config_data = {
        "connection_type": CONNECTION_TYPE_MODBUS,
        "host": "192.168.1.100",
        "port": 502,
        "modbus_slave_id": 1,
    }
    
    with patch(
        "custom_components.sungrow_winet_s.coordinator.SungrowModbusClient",
        return_value=mock_modbus_client,
    ):
        coordinator = SungrowDataCoordinator(hass, config_data)
        
        # Manually trigger update
        await coordinator._async_update_data()
        
        assert coordinator.data is not None
        assert coordinator.data["pv_power"] == 1500.0
        assert coordinator.data["battery_soc"] == 85.0


@pytest.mark.asyncio
async def test_coordinator_handles_failures(hass: HomeAssistant, mock_modbus_client):
    """Test coordinator handling connection failures."""
    # Make client fail
    mock_modbus_client.read_all_data = AsyncMock(side_effect=Exception("Connection error"))
    
    config_data = {
        "connection_type": CONNECTION_TYPE_MODBUS,
        "host": "192.168.1.100",
        "port": 502,
        "modbus_slave_id": 1,
    }
    
    with patch(
        "custom_components.sungrow_winet_s.coordinator.SungrowModbusClient",
        return_value=mock_modbus_client,
    ):
        coordinator = SungrowDataCoordinator(hass, config_data)
        
        # Should raise UpdateFailed
        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()
