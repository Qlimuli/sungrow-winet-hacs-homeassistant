"""Fixtures for Sungrow WINET-S tests."""
from __future__ import annotations

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.sungrow_winet_s.const import DOMAIN


@pytest.fixture
def mock_modbus_client() -> Generator[AsyncMock, None, None]:
    """Create a mock Modbus client."""
    with patch(
        "custom_components.sungrow_winet_s.api.modbus_client.SungrowModbusClient",
        autospec=True,
    ) as mock:
        client = mock.return_value
        client.connect = AsyncMock(return_value=True)
        client.disconnect = AsyncMock()
        client.test_connection = AsyncMock(return_value=True)
        client.read_all_data = AsyncMock(
            return_value={
                "pv_power": 5000,
                "daily_pv_energy": 25.5,
                "total_pv_energy": 15000.0,
                "battery_soc": 85.0,
                "battery_power": -1500,
                "grid_power": 200,
                "load_power": 3300,
                "inverter_temp": 45.5,
                "running_state": "Running",
            }
        )
        yield client


@pytest.fixture
def mock_http_client() -> Generator[AsyncMock, None, None]:
    """Create a mock HTTP client."""
    with patch(
        "custom_components.sungrow_winet_s.api.http_client.SungrowHttpClient",
        autospec=True,
    ) as mock:
        client = mock.return_value
        client.connect = AsyncMock(return_value=True)
        client.disconnect = AsyncMock()
        client.test_connection = AsyncMock(return_value=True)
        client.read_all_data = AsyncMock(
            return_value={
                "pv_power": 4800,
                "daily_pv_energy": 24.0,
                "battery_soc": 80.0,
            }
        )
        yield client


@pytest.fixture
def mock_cloud_client() -> Generator[AsyncMock, None, None]:
    """Create a mock Cloud client."""
    with patch(
        "custom_components.sungrow_winet_s.api.cloud_client.SungrowCloudClient",
        autospec=True,
    ) as mock:
        client = mock.return_value
        client.connect = AsyncMock(return_value=True)
        client.disconnect = AsyncMock()
        client.test_connection = AsyncMock(return_value=True)
        client.plant_id = "12345"
        client.device_sn = "ABC123456"
        client.read_all_data = AsyncMock(
            return_value={
                "pv_power": 4500,
                "daily_pv_energy": 22.0,
                "total_pv_energy": 14000.0,
            }
        )
        yield client
