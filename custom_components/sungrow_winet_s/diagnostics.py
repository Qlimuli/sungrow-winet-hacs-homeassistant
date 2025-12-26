"""Diagnostics support for Sungrow WINET-S integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant

from .const import (
    CONF_ACCESS_KEY,
    CONF_API_KEY,
    CONF_RSA_PRIVATE_KEY,
    DOMAIN,
)
from .coordinator import SungrowDataUpdateCoordinator

TO_REDACT = {
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_API_KEY,
    CONF_ACCESS_KEY,
    CONF_RSA_PRIVATE_KEY,
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: SungrowDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    return {
        "entry": {
            "title": entry.title,
            "data": async_redact_data(entry.data, TO_REDACT),
            "options": dict(entry.options),
        },
        "coordinator_data": coordinator.data if coordinator.data else {},
        "last_update_success": coordinator.last_update_success,
    }
