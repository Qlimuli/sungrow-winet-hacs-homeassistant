"""Sensor platform for Sungrow WINET-S integration."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfElectricPotential,
    UnitOfElectricCurrent,
    UnitOfFrequency,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SungrowDataUpdateCoordinator


@dataclass(frozen=True, kw_only=True)
class SungrowSensorEntityDescription(SensorEntityDescription):
    """Describes a Sungrow sensor entity."""

    data_key: str


SENSOR_DESCRIPTIONS: tuple[SungrowSensorEntityDescription, ...] = (
    # Device Info
    SungrowSensorEntityDescription(
        key="serial_number",
        data_key="serial_number",
        name="Serial Number",
        icon="mdi:identifier",
        entity_registry_enabled_default=False,
    ),
    SungrowSensorEntityDescription(
        key="device_type_code",
        data_key="device_type_code",
        name="Device Type Code",
        icon="mdi:information-outline",
        entity_registry_enabled_default=False,
    ),
    SungrowSensorEntityDescription(
        key="nominal_power",
        data_key="nominal_power",
        name="Nominal Power",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:flash",
        entity_registry_enabled_default=False,
    ),
    # PV Sensors
    SungrowSensorEntityDescription(
        key="pv_power",
        data_key="pv_power",
        name="PV Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:solar-power",
    ),
    SungrowSensorEntityDescription(
        key="daily_pv_energy",
        data_key="daily_pv_energy",
        name="Daily PV Energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:solar-power-variant",
    ),
    SungrowSensorEntityDescription(
        key="total_pv_energy",
        data_key="total_pv_energy",
        name="Total PV Energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:solar-power-variant",
    ),
    SungrowSensorEntityDescription(
        key="total_running_time",
        data_key="total_running_time",
        name="Total Running Time",
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:timer-outline",
        entity_registry_enabled_default=False,
    ),
    SungrowSensorEntityDescription(
        key="pv1_voltage",
        data_key="pv1_voltage",
        name="PV1 Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:flash",
        entity_registry_enabled_default=False,
    ),
    SungrowSensorEntityDescription(
        key="pv1_current",
        data_key="pv1_current",
        name="PV1 Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:current-dc",
        entity_registry_enabled_default=False,
    ),
    # Grid Sensors
    SungrowSensorEntityDescription(
        key="grid_voltage_a",
        data_key="grid_voltage_a",
        name="Grid Voltage Phase A",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:flash",
        entity_registry_enabled_default=False,
    ),
    SungrowSensorEntityDescription(
        key="grid_voltage_b",
        data_key="grid_voltage_b",
        name="Grid Voltage Phase B",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:flash",
        entity_registry_enabled_default=False,
    ),
    SungrowSensorEntityDescription(
        key="grid_voltage_c",
        data_key="grid_voltage_c",
        name="Grid Voltage Phase C",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:flash",
        entity_registry_enabled_default=False,
    ),
    SungrowSensorEntityDescription(
        key="grid_current_a",
        data_key="grid_current_a",
        name="Grid Current Phase A",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:current-ac",
        entity_registry_enabled_default=False,
    ),
    SungrowSensorEntityDescription(
        key="grid_current_b",
        data_key="grid_current_b",
        name="Grid Current Phase B",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:current-ac",
        entity_registry_enabled_default=False,
    ),
    SungrowSensorEntityDescription(
        key="grid_current_c",
        data_key="grid_current_c",
        name="Grid Current Phase C",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:current-ac",
        entity_registry_enabled_default=False,
    ),
    SungrowSensorEntityDescription(
        key="active_power",
        data_key="active_power",
        name="Active Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:flash",
    ),
    SungrowSensorEntityDescription(
        key="reactive_power",
        data_key="reactive_power",
        name="Reactive Power",
        native_unit_of_measurement="var",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:flash",
        entity_registry_enabled_default=False,
    ),
    SungrowSensorEntityDescription(
        key="power_factor",
        data_key="power_factor",
        name="Power Factor",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:angle-acute",
        entity_registry_enabled_default=False,
    ),
    SungrowSensorEntityDescription(
        key="grid_frequency",
        data_key="grid_frequency",
        name="Grid Frequency",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:sine-wave",
        entity_registry_enabled_default=False,
    ),
    # Inverter Sensors
    SungrowSensorEntityDescription(
        key="inverter_temp",
        data_key="inverter_temp",
        name="Inverter Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
    ),
    SungrowSensorEntityDescription(
        key="running_state",
        data_key="running_state",
        name="Inverter Status",
        icon="mdi:information-outline",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sungrow sensors based on a config entry."""
    coordinator: SungrowDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SungrowSensor] = []

    for description in SENSOR_DESCRIPTIONS:
        # Only add sensor if data is available
        if coordinator.data and description.data_key in coordinator.data:
            entities.append(SungrowSensor(coordinator, description))

    async_add_entities(entities)


class SungrowSensor(CoordinatorEntity[SungrowDataUpdateCoordinator], SensorEntity):
    """Representation of a Sungrow sensor."""

    entity_description: SungrowSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SungrowDataUpdateCoordinator,
        description: SungrowSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{description.key}"
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get(self.entity_description.data_key)
        return None

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return (
            super().available
            and self.coordinator.data is not None
            and self.entity_description.data_key in self.coordinator.data
        )
