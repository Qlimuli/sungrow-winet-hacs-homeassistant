"""The Sungrow WINET-S Inverter integration."""
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .coordinator import SungrowDataCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Sungrow WINET-S Inverter from a config entry.
    
    Args:
        hass: Home Assistant instance
        entry: Config entry
        
    Returns:
        True if setup was successful
    """
    hass.data.setdefault(DOMAIN, {})
    
    # Create coordinator
    coordinator = SungrowDataCoordinator(hass, entry.data)
    
    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()
    
    if not coordinator.last_update_success:
        raise ConfigEntryNotReady("Failed to connect to Sungrow inverter")
    
    # Store coordinator
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Set up options update listener
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    
    _LOGGER.info("Sungrow WINET-S integration setup complete")
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry.
    
    Args:
        hass: Home Assistant instance
        entry: Config entry
        
    Returns:
        True if unload was successful
    """
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        # Shutdown coordinator
        coordinator: SungrowDataCoordinator = hass.data[DOMAIN][entry.entry_id]
        await coordinator.async_shutdown()
        
        # Remove coordinator from hass.data
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry.
    
    Args:
        hass: Home Assistant instance
        entry: Config entry
    """
    await hass.config_entries.async_reload(entry.entry_id)
