"""Test configuration."""
import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def hass():
    """Mock Home Assistant instance."""
    hass_mock = MagicMock()
    hass_mock.data = {}
    hass_mock.config_entries = MagicMock()
    hass_mock.config_entries.async_forward_entry_setups = AsyncMock(return_value=True)
    hass_mock.config_entries.async_unload_platforms = AsyncMock(return_value=True)
    return hass_mock
