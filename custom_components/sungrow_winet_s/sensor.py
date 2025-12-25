"""Sensor platform for Sungrow WINET-S Inverter integration."""
import logging
from typing import Any, Optional

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SENSOR_TYPES, DEFAULT_NAME
from .coordinator import SungrowDataCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sungrow sensor entities from a config entry.
    
    Args:
        hass: Home Assistant instance
        entry: Config entry
        async_add_entities: Callback to add entities
    """
    coordinator: SungrowDataCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Create sensor entities for all configured sensor types
    entities = []
    for sensor_key, sensor_config in SENSOR_TYPES.items():
        entities.append(
            SungrowSensor(
                coordinator=coordinator,
                entry=entry,
                sensor_key=sensor_key,
                sensor_config=sensor_config,
            )
        )
    
    async_add_entities(entities)
    _LOGGER.info("Added %d Sungrow sensor entities", len(entities))


class SungrowSensor(CoordinatorEntity[SungrowDataCoordinator], SensorEntity):
    """Representation of a Sungrow sensor."""

    def __init__(
        self,
        coordinator: SungrowDataCoordinator,
        entry: ConfigEntry,
        sensor_key: str,
        sensor_config: dict[str, Any],
    ) -> None:
        """Initialize the sensor.
        
        Args:
            coordinator: Data coordinator
            entry: Config entry
            sensor_key: Sensor identifier key
            sensor_config: Sensor configuration dict
        """
        super().__init__(coordinator)
        
        self._sensor_key = sensor_key
        self._attr_name = f"{DEFAULT_NAME} {sensor_config['name']}"
        self._attr_unique_id = f"{entry.entry_id}_{sensor_key}"
        self._attr_icon = sensor_config.get("icon")
        
        # Set native unit of measurement
        unit = sensor_config.get("unit")
        if unit == "W":
            self._attr_native_unit_of_measurement = UnitOfPower.WATT
        elif unit == "kWh":
            self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
        elif unit == "%":
            self._attr_native_unit_of_measurement = PERCENTAGE
        elif unit == "V":
            self._attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT
        elif unit == "A":
            self._attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
        elif unit == "°C":
            self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        elif unit == "min":
            self._attr_native_unit_of_measurement = UnitOfTime.MINUTES
        else:
            self._attr_native_unit_of_measurement = unit
        
        # Set device class
        device_class = sensor_config.get("device_class")
        if device_class == "power":
            self._attr_device_class = SensorDeviceClass.POWER
        elif device_class == "energy":
            self._attr_device_class = SensorDeviceClass.ENERGY
        elif device_class == "battery":
            self._attr_device_class = SensorDeviceClass.BATTERY
        elif device_class == "voltage":
            self._attr_device_class = SensorDeviceClass.VOLTAGE
        elif device_class == "current":
            self._attr_device_class = SensorDeviceClass.CURRENT
        elif device_class == "temperature":
            self._attr_device_class = SensorDeviceClass.TEMPERATURE
        elif device_class == "duration":
            self._attr_device_class = SensorDeviceClass.DURATION
        
        # Set state class
        state_class = sensor_config.get("state_class")
        if state_class == "measurement":
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif state_class == "total_increasing":
            self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        elif state_class == "total":
            self._attr_state_class = SensorStateClass.TOTAL
        
        # Device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=DEFAULT_NAME,
            manufacturer="Sungrow",
            model="WINET-S Compatible Inverter",
            sw_version="1.0.0",
        )
        
        # Add testid for testing
        self._attr_extra_state_attributes = {
            "testid": f"sungrow-{sensor_key.replace('_', '-')}"
        }

    @property
    def native_value(self) -> Optional[float | str]:
        """Return the state of the sensor.
        
        Returns:
            Sensor value from coordinator data
        """
        if self.coordinator.data:
            return self.coordinator.data.get(self._sensor_key)
        return None

    @property
    def available(self) -> bool:
        """Return True if entity is available.
        
        Returns:
            True if coordinator has valid data
        """
        return self.coordinator.last_update_success and self.coordinator.data is not None
