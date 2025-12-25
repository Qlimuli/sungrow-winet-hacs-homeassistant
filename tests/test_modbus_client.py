"""Tests for Modbus client."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.sungrow_winet_s.api.modbus_client import SungrowModbusClient


@pytest.fixture
def mock_modbus_client():
    """Mock pymodbus client."""
    client = MagicMock()
    client.connect = AsyncMock(return_value=True)
    client.connected = True
    client.close = MagicMock()
    return client


@pytest.mark.asyncio
async def test_modbus_connect(mock_modbus_client):
    """Test Modbus connection."""
    with patch(
        "custom_components.sungrow_winet_s.api.modbus_client.AsyncModbusTcpClient",
        return_value=mock_modbus_client,
    ):
        client = SungrowModbusClient(host="192.168.1.100", port=502, slave_id=1)
        result = await client.connect()
        assert result is True
        assert client._client is not None


@pytest.mark.asyncio
async def test_modbus_read_register(mock_modbus_client):
    """Test reading a Modbus register."""
    # Mock register response
    mock_result = MagicMock()
    mock_result.isError.return_value = False
    mock_result.registers = [1000]  # PV power = 1000W
    mock_modbus_client.read_holding_registers = AsyncMock(return_value=mock_result)
    
    with patch(
        "custom_components.sungrow_winet_s.api.modbus_client.AsyncModbusTcpClient",
        return_value=mock_modbus_client,
    ):
        client = SungrowModbusClient(host="192.168.1.100", port=502, slave_id=1)
        await client.connect()
        
        value = await client.read_register(register=5016, count=1, scale=1.0, signed=False)
        assert value == 1000.0


@pytest.mark.asyncio
async def test_modbus_disconnect(mock_modbus_client):
    """Test Modbus disconnection."""
    with patch(
        "custom_components.sungrow_winet_s.api.modbus_client.AsyncModbusTcpClient",
        return_value=mock_modbus_client,
    ):
        client = SungrowModbusClient(host="192.168.1.100", port=502, slave_id=1)
        await client.connect()
        await client.disconnect()
        mock_modbus_client.close.assert_called_once()
