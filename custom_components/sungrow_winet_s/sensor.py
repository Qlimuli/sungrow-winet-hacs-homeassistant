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

    # ===== MONTHLY PV ENERGY =====
    SungrowSensorEntityDescription(
        key="monthly_pv_energy_january",
        data_key="monthly_pv_energy_january",
        name="Monthly PV Energy January",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:solar-power",
        entity_registry_enabled_default=False,
    ),
    SungrowSensorEntityDescription(
        key="monthly_pv_energy_february",
        data_key="monthly_pv_energy_february",
        name="Monthly PV Energy February",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:solar-power",
        entity_registry_enabled_default=False,
    ),
    SungrowSensorEntityDescription(
        key="monthly_pv_energy_march",
        data_key="monthly_pv_energy_march",
        name="Monthly PV Energy March",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:solar-power",
        entity_registry_enabled_default=False,
    ),
    SungrowSensorEntityDescription(
        key="monthly_pv_energy_april",
        data_key="monthly_pv_energy_april",
        name="Monthly PV Energy April",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:solar-power",
        entity_registry_enabled_default=False,
    ),
    SungrowSensorEntityDescription(
        key="monthly_pv_energy_may",
        data_key="monthly_pv_energy_may",
        name="Monthly PV Energy May",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:solar-power",
        entity_registry_enabled_default=False,
    ),
    SungrowSensorEntityDescription(
        key="monthly_pv_energy_june",
        data_key="monthly_pv_energy_june",
        name="Monthly PV Energy June",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:solar-power",
        entity_registry_enabled_default=False,
    ),
    SungrowSensorEntityDescription(
        key="monthly_pv_energy_july",
        data_key="monthly_pv_energy_july",
        name="Monthly PV Energy July",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:solar-power",
        entity_registry_enabled_default=False,
    ),
    SungrowSensorEntityDescription(
        key="monthly_pv_energy_august",
        data_key="monthly_pv_energy_august",
        name="Monthly PV Energy August",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:solar-power",
        entity_registry_enabled_default=False,
    ),
    SungrowSensorEntityDescription(
        key="monthly_pv_energy_september",
        data_key="monthly_pv_energy_september",
        name="Monthly PV Energy September",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:solar-power",
        entity_registry_enabled_default=False,
    ),
    SungrowSensorEntityDescription(
        key="monthly_pv_energy_october",
        data_key="monthly_pv_energy_october",
        name="Monthly PV Energy October",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:solar-power",
        entity_registry_enabled_default=False,
    ),
    SungrowSensorEntityDescription(
        key="monthly_pv_energy_november",
        data_key="monthly_pv_energy_november",
        name="Monthly PV Energy November",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:solar-power",
        entity_registry_enabled_default=False,
    ),
    SungrowSensorEntityDescription(
        key="monthly_pv_energy_december",
        data_key="monthly_pv_energy_december",
        name="Monthly PV Energy December",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:solar-power",
        entity_registry_enabled_default=False,
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
        key="system_clock",
        data_key="system_clock",
        name="System Clock",
        icon="mdi:clock-outline",
        entity_registry_enabled_default=False,
    ),

    # ===== CALCULATED POWER =====
    SungrowSensorEntityDescription(
        key="mppt1_power",
        data_key="mppt1_power",
        name="MPPT 1 Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:solar-power",
        calculated=True,
    ),
    SungrowSensorEntityDescription(
        key="mppt2_power",
        data_key="mppt2_power",
        name="MPPT 2 Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:solar-power",
        calculated=True,
    ),
    SungrowSensorEntityDescription(
        key="mppt3_power",
        data_key="mppt3_power",
        name="MPPT 3 Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:solar-power",
        calculated=True,
        entity_registry_enabled_default=False,
    ),
    SungrowSensorEntityDescription(
        key="mppt4_power",
        data_key="mppt4_power",
        name="MPPT 4 Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:solar-power",
        calculated=True,
        entity_registry_enabled_default=False,
    ),
    SungrowSensorEntityDescription(
        key="total_pv_power",
        data_key="total_pv_power",
        name="Total PV Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:solar-power-variant",
        calculated=True,
    ),
    SungrowSensorEntityDescription(
        key="meter_total_power",
        data_key="meter_total_power",
        name="Meter Total Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:meter-electric",
        calculated=True,
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
        if description.calculated:
            entities.append(SungrowSensor(coordinator, description))
        elif coordinator.data and description.data_key in coordinator.data:
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
            if self.entity_description.calculated:
                return self._calculate_value()
            return self.coordinator.data.get(self.entity_description.data_key)
        return None

    def _calculate_value(self) -> float | None:
        """Calculate derived sensor values."""
        data = self.coordinator.data
        if not data:
            return None

        key = self.entity_description.data_key

        if key == "mppt1_power":
            voltage = data.get("mppt1_voltage")
            current = data.get("mppt1_current")
            if voltage is not None and current is not None:
                return round(voltage * current, 1)

        elif key == "mppt2_power":
            voltage = data.get("mppt2_voltage")
            current = data.get("mppt2_current")
            if voltage is not None and current is not None:
                return round(voltage * current, 1)

        elif key == "mppt3_power":
            voltage = data.get("mppt3_voltage")
            current = data.get("mppt3_current")
            if voltage is not None and current is not None:
                return round(voltage * current, 1)

        elif key == "mppt4_power":
            voltage = data.get("mppt4_voltage")
            current = data.get("mppt4_current")
            if voltage is not None and current is not None:
                return round(voltage * current, 1)

        elif key == "total_pv_power":
            total = 0.0
            for i in range(1, 5):
                voltage = data.get(f"mppt{i}_voltage")
                current = data.get(f"mppt{i}_current")
                if voltage is not None and current is not None:
                    total += voltage * current
            return round(total, 1) if total > 0 else 0.0

        elif key == "meter_total_power":
            total = 0.0
            has_data = False
            for phase in ("a", "b", "c"):
                power = data.get(f"meter_power_phase_{phase}")
                if power is not None:
                    total += power
                    has_data = True
            return round(total, 1) if has_data else None

        return None

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        if self.entity_description.calculated:
            return super().available and self.coordinator.data is not None
        return (
            super().available
            and self.coordinator.data is not None
            and self.entity_description.data_key in self.coordinator.data
        )
