"""Sensor platform for Sungrow WINET-S integration."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import logging

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

from .const import DOMAIN, MODBUS_REGISTERS
from .coordinator import SungrowDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

@dataclass(frozen=True, kw_only=True)
class SungrowSensorEntityDescription(SensorEntityDescription):
    """Describes a Sungrow sensor entity."""

    data_key: str
    calculated: bool = False


SENSOR_DESCRIPTIONS: tuple[SungrowSensorEntityDescription, ...] = (
    # ===== DEVICE INFO =====
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
        key="arm_software_version",
        data_key="arm_software_version",
        name="ARM Software Version",
        icon="mdi:chip",
        entity_registry_enabled_default=False,
    ),
    SungrowSensorEntityDescription(
        key="dsp_software_version",
        data_key="dsp_software_version",
        name="DSP Software Version",
        icon="mdi:chip",
        entity_registry_enabled_default=False,
    ),
    SungrowSensorEntityDescription(
        key="protocol_no",
        data_key="protocol_no",
        name="Protocol Number",
        icon="mdi:protocol",
        entity_registry_enabled_default=False,
    ),
    SungrowSensorEntityDescription(
        key="protocol_version",
        data_key="protocol_version",
        name="Protocol Version",
        icon="mdi:protocol",
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
    SungrowSensorEntityDescription(
        key="output_type",
        data_key="output_type",
        name="Output Type",
        icon="mdi:information-outline",
        entity_registry_enabled_default=False,
    ),
    
    # ===== ENERGY =====
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
    
    # ===== TEMPERATURE =====
    SungrowSensorEntityDescription(
        key="inverter_temp",
        data_key="inverter_temp",
        name="Inverter Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
    ),
    
    # ===== MPPT 1 =====
    SungrowSensorEntityDescription(
        key="mppt1_voltage",
        data_key="mppt1_voltage",
        name="MPPT 1 Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:flash",
    ),
    SungrowSensorEntityDescription(
        key="mppt1_current",
        data_key="mppt1_current",
        name="MPPT 1 Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:current-dc",
    ),
    
    # ===== MPPT 2 =====
    SungrowSensorEntityDescription(
        key="mppt2_voltage",
        data_key="mppt2_voltage",
        name="MPPT 2 Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:flash",
    ),
    SungrowSensorEntityDescription(
        key="mppt2_current",
        data_key="mppt2_current",
        name="MPPT 2 Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:current-dc",
    ),
    
    # ===== MPPT 3 =====
    SungrowSensorEntityDescription(
        key="mppt3_voltage",
        data_key="mppt3_voltage",
        name="MPPT 3 Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:flash",
        entity_registry_enabled_default=False,
    ),
    SungrowSensorEntityDescription(
        key="mppt3_current",
        data_key="mppt3_current",
        name="MPPT 3 Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:current-dc",
        entity_registry_enabled_default=False,
    ),
    
    # ===== MPPT 4 =====
    SungrowSensorEntityDescription(
        key="mppt4_voltage",
        data_key="mppt4_voltage",
        name="MPPT 4 Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:flash",
        entity_registry_enabled_default=False,
    ),
    SungrowSensorEntityDescription(
        key="mppt4_current",
        data_key="mppt4_current",
        name="MPPT 4 Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:current-dc",
        entity_registry_enabled_default=False,
    ),
    
    # ===== DC POWER =====
    SungrowSensorEntityDescription(
        key="total_dc_power",
        data_key="total_dc_power",
        name="Total DC Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:solar-power",
    ),
    
    # ===== GRID VOLTAGE =====
    SungrowSensorEntityDescription(
        key="grid_voltage_a",
        data_key="grid_voltage_a",
        name="Grid Voltage Phase A",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:flash",
    ),
    SungrowSensorEntityDescription(
        key="grid_voltage_b",
        data_key="grid_voltage_b",
        name="Grid Voltage Phase B",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:flash",
    ),
    SungrowSensorEntityDescription(
        key="grid_voltage_c",
        data_key="grid_voltage_c",
        name="Grid Voltage Phase C",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:flash",
    ),
    
    # ===== POWER =====
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
    ),
    SungrowSensorEntityDescription(
        key="grid_frequency",
        data_key="grid_frequency",
        name="Grid Frequency",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:sine-wave",
    ),
    SungrowSensorEntityDescription(
        key="grid_frequency_high_precision",
        data_key="grid_frequency_high_precision",
        name="Grid Frequency (High Precision)",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:sine-wave",
        entity_registry_enabled_default=False,
    ),
    
    # ===== BATTERY =====
    SungrowSensorEntityDescription(
        key="battery_power",
        data_key="battery_power",
        name="Battery Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery",
    ),
    SungrowSensorEntityDescription(
        key="battery_current",
        data_key="battery_current",
        name="Battery Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:current-dc",
    ),
    SungrowSensorEntityDescription(
        key="bdc_rated_power",
        data_key="bdc_rated_power",
        name="BDC Rated Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery",
        entity_registry_enabled_default=False,
    ),
    SungrowSensorEntityDescription(
        key="max_charging_current_bms",
        data_key="max_charging_current_bms",
        name="Max Charging Current (BMS)",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery-charging",
        entity_registry_enabled_default=False,
    ),
    SungrowSensorEntityDescription(
        key="max_discharging_current_bms",
        data_key="max_discharging_current_bms",
        name="Max Discharging Current (BMS)",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery-minus",
        entity_registry_enabled_default=False,
    ),
    
    # ===== METER =====
    SungrowSensorEntityDescription(
        key="meter_power_phase_a",
        data_key="meter_power_phase_a",
        name="Meter Power Phase A",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:meter-electric",
    ),
    SungrowSensorEntityDescription(
        key="meter_power_phase_b",
        data_key="meter_power_phase_b",
        name="Meter Power Phase B",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:meter-electric",
    ),
    SungrowSensorEntityDescription(
        key="meter_power_phase_c",
        data_key="meter_power_phase_c",
        name="Meter Power Phase C",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:meter-electric",
    ),
    
    # ===== EXPORT LIMITS =====
    SungrowSensorEntityDescription(
        key="export_limit_min",
        data_key="export_limit_min",
        name="Export Limit Min",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:transmission-tower-export",
        entity_registry_enabled_default=False,
    ),
    SungrowSensorEntityDescription(
        key="export_limit_max",
        data_key="export_limit_max",
        name="Export Limit Max",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:transmission-tower-export",
        entity_registry_enabled_default=False,
    ),
    
    # ===== SYSTEM CLOCK =====
    SungrowSensorEntityDescription(
        key="system_clock_year",
        data_key="system_clock_year",
        name="System Clock Year",
        icon="mdi:calendar",
        entity_registry_enabled_default=False,
    ),
    SungrowSensorEntityDescription(
        key="system_clock_month",
        data_key="system_clock_month",
        name="System Clock Month",
        icon="mdi:calendar",
        entity_registry_enabled_default=False,
    ),
    SungrowSensorEntityDescription(
        key="system_clock_day",
        data_key="system_clock_day",
        name="System Clock Day",
        icon="mdi:calendar",
        entity_registry_enabled_default=False,
    ),
    SungrowSensorEntityDescription(
        key="system_clock_hour",
        data_key="system_clock_hour",
        name="System Clock Hour",
        icon="mdi:clock",
        entity_registry_enabled_default=False,
    ),
    SungrowSensorEntityDescription(
        key="system_clock_minute",
        data_key="system_clock_minute",
        name="System Clock Minute",
        icon="mdi:clock",
        entity_registry_enabled_default=False,
    ),
    SungrowSensorEntityDescription(
        key="system_clock_second",
        data_key="system_clock_second",
        name="System Clock Second",
        icon="mdi:clock",
        entity_registry_enabled_default=False,
    ),
)

class SungrowSensor(CoordinatorEntity[SungrowDataUpdateCoordinator], SensorEntity):
    """Basis-Sensor für Modbus-Werte."""

    entity_description: SungrowSensorEntityDescription

    def __init__(
        self,
        coordinator: SungrowDataUpdateCoordinator,
        description: SungrowSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"
        self._attr_name = description.name

    @property
    def native_value(self) -> Any:
        """Return the value of the sensor."""
        return self.coordinator.data.get(self.entity_description.data_key)

class SungrowMPPTPowerSensor(CoordinatorEntity[SungrowDataUpdateCoordinator], SensorEntity):
    """Berechneter Power-Sensor für jeden MPPT."""

    def __init__(
        self,
        coordinator: SungrowDataUpdateCoordinator,
        mppt_num: int,
        voltage_key: str,
        current_key: str,
    ) -> None:
        """Initialize the calculated MPPT power sensor."""
        super().__init__(coordinator)
        self._mppt_num = mppt_num
        self._voltage_key = voltage_key
        self._current_key = current_key
        self._attr_name = f"MPPT {mppt_num} Power"
        self._attr_native_unit_of_measurement = UnitOfPower.WATT
        self._attr_device_class = SensorDeviceClass.POWER
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_mppt{mppt_num}_power"

    @property
    def native_value(self) -> float | None:
        """Berechne Power = Voltage * Current."""
        voltage = self.coordinator.data.get(self._voltage_key)
        current = self.coordinator.data.get(self._current_key)
        if voltage is not None and current is not None:
            return round(voltage * current, 0)  # In Watt, ganzzahlig
        return None

class SungrowTotalPVPowerSensor(CoordinatorEntity[SungrowDataUpdateCoordinator], SensorEntity):
    """Total PV Power als Summe aller MPPT Powers."""

    def __init__(
        self,
        coordinator: SungrowDataUpdateCoordinator,
        mppt_power_keys: list[str],
    ) -> None:
        """Initialize the total PV power sensor."""
        super().__init__(coordinator)
        self._mppt_power_keys = mppt_power_keys  # z.B. ['mppt1_power', 'mppt2_power', ...]
        self._attr_name = "Total PV Power"
        self._attr_native_unit_of_measurement = UnitOfPower.WATT
        self._attr_device_class = SensorDeviceClass.POWER
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_total_pv_power"

    @property
    def native_value(self) -> float | None:
        """Summe aller MPPT Powers."""
        total = 0.0
        for key in self._mppt_power_keys:
            value = self.coordinator.data.get(key)
            if value is not None:
                total += value
        return round(total, 0) if total > 0 else None

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator: SungrowDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[SensorEntity] = []

    # Direkte Modbus-Sensoren hinzufügen
    for description in SENSOR_DESCRIPTIONS:
        entities.append(SungrowSensor(coordinator, description))

    # Berechnete MPPT Power-Sensoren hinzufügen (für MPPT 1-4)
    entities.append(
        SungrowMPPTPowerSensor(coordinator, 1, "mppt1_voltage", "mppt1_current")
    )
    entities.append(
        SungrowMPPTPowerSensor(coordinator, 2, "mppt2_voltage", "mppt2_current")
    )
    entities.append(
        SungrowMPPTPowerSensor(coordinator, 3, "mppt3_voltage", "mppt3_current")
    )
    entities.append(
        SungrowMPPTPowerSensor(coordinator, 4, "mppt4_voltage", "mppt4_current")
    )

    # Total PV Power hinzufügen
    mppt_power_keys = ["mppt1_power", "mppt2_power", "mppt3_power", "mppt4_power"]
    entities.append(SungrowTotalPVPowerSensor(coordinator, mppt_power_keys))

    async_add_entities(entities)
