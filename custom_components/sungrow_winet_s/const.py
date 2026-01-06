"""Constants for the Sungrow WINET-S integration."""
from __future__ import annotations

from datetime import timedelta
from typing import Final

# Domain
DOMAIN: Final = "sungrow_winet_s"

# Connection modes
CONNECTION_MODE_MODBUS: Final = "modbus"
CONNECTION_MODE_HTTP: Final = "http"
CONNECTION_MODE_CLOUD: Final = "cloud"

# Config keys
CONF_CONNECTION_MODE: Final = "connection_mode"
CONF_MODBUS_PORT: Final = "modbus_port"
CONF_MODBUS_SLAVE_ID: Final = "modbus_slave_id"
CONF_MODBUS_USE_TLS: Final = "modbus_use_tls"
CONF_API_KEY: Final = "api_key"
CONF_ACCESS_KEY: Final = "access_key"
CONF_RSA_PRIVATE_KEY: Final = "rsa_private_key"
CONF_PLANT_ID: Final = "plant_id"
CONF_DEVICE_SN: Final = "device_sn"

# Defaults
DEFAULT_MODBUS_PORT: Final = 502
DEFAULT_MODBUS_SLAVE_ID: Final = 1
DEFAULT_MODBUS_USE_TLS: Final = False
DEFAULT_HTTP_PORT: Final = 80
DEFAULT_SCAN_INTERVAL_LOCAL: Final = timedelta(seconds=10)
DEFAULT_SCAN_INTERVAL_CLOUD: Final = timedelta(minutes=5)

# Note: addresses are "doc_addr" (1-based as in Sungrow documentation)
# The client will subtract 1 to get the protocol address
MODBUS_REGISTERS: Final = {
    # ===== DEVICE INFO =====
    "protocol_no": {
        "address": 4950,
        "count": 2,
        "scale": 1,
        "type": "u32",
        "unit": None,
    },
    "protocol_version": {
        "address": 4952,
        "count": 2,
        "scale": 1,
        "type": "u32",
        "unit": None,
    },
    "arm_software_version": {
        "address": 4954,
        "count": 15,
        "scale": 1,
        "type": "string",
        "unit": None,
    },
    "dsp_software_version": {
        "address": 4969,
        "count": 15,
        "scale": 1,
        "type": "string",
        "unit": None,
    },
    "serial_number": {
        "address": 4990,
        "count": 10,
        "scale": 1,
        "type": "string",
        "unit": None,
    },
    "device_type_code": {
        "address": 5000,
        "count": 1,
        "scale": 1,
        "type": "u16",
        "unit": None,
    },
    "nominal_power": {
        "address": 5001,
        "count": 1,
        "scale": 0.1,
        "type": "u16",
        "unit": "kW",
    },
    "output_type": {
        "address": 5002,
        "count": 1,
        "scale": 1,
        "type": "u16",
        "unit": None,
    },
    
    # ===== ENERGY =====
    "daily_pv_energy": {
        "address": 5003,
        "count": 1,
        "scale": 0.1,
        "type": "u16",
        "unit": "kWh",
    },
    "total_pv_energy": {
        "address": 5004,
        "count": 2,
        "scale": 0.1,
        "type": "u32",
        "unit": "kWh",
    },
    "monthly_pv_energy": {
        "address": 6238,
        "count": 1,
        "scale": 0.1,
        "type": "u16",
        "unit": "kWh",
    },
    
    # ===== TEMPERATURE =====
    "inverter_temp": {
        "address": 5008,
        "count": 1,
        "scale": 0.1,
        "type": "s16",
        "signed": True,
        "unit": "°C",
    },
    
    # ===== MPPT 1 =====
    "mppt1_voltage": {
        "address": 5011,
        "count": 1,
        "scale": 0.1,
        "type": "u16",
        "unit": "V",
    },
    "mppt1_current": {
        "address": 5012,
        "count": 1,
        "scale": 0.1,
        "type": "u16",
        "unit": "A",
    },
    
    # ===== MPPT 2 =====
    "mppt2_voltage": {
        "address": 5013,
        "count": 1,
        "scale": 0.1,
        "type": "u16",
        "unit": "V",
    },
    "mppt2_current": {
        "address": 5014,
        "count": 1,
        "scale": 0.1,
        "type": "u16",
        "unit": "A",
    },
    
    # ===== MPPT 3 =====
    "mppt3_voltage": {
        "address": 5015,
        "count": 1,
        "scale": 0.1,
        "type": "u16",
        "unit": "V",
    },
    "mppt3_current": {
        "address": 5016,
        "count": 1,
        "scale": 0.1,
        "type": "u16",
        "unit": "A",
    },
    
    # ===== MPPT 4 =====
    "mppt4_voltage": {
        "address": 5115,
        "count": 1,
        "scale": 0.1,
        "type": "u16",
        "unit": "V",
    },
    "mppt4_current": {
        "address": 5116,
        "count": 1,
        "scale": 0.1,
        "type": "u16",
        "unit": "A",
    },
    
    # ===== DC POWER =====
    "total_dc_power": {
        "address": 5017,
        "count": 2,
        "scale": 1,
        "type": "u32",
        "unit": "W",
    },
    
    # ===== GRID VOLTAGE =====
    "grid_voltage_a": {
        "address": 5019,
        "count": 1,
        "scale": 0.1,
        "type": "u16",
        "unit": "V",
    },
    "grid_voltage_b": {
        "address": 5020,
        "count": 1,
        "scale": 0.1,
        "type": "u16",
        "unit": "V",
    },
    "grid_voltage_c": {
        "address": 5021,
        "count": 1,
        "scale": 0.1,
        "type": "u16",
        "unit": "V",
    },
    
    # ===== POWER =====
    "reactive_power": {
        "address": 5033,
        "count": 2,
        "scale": 1,
        "type": "s32",
        "signed": True,
        "unit": "var",
    },
    "power_factor": {
        "address": 5035,
        "count": 1,
        "scale": 0.001,
        "type": "s16",
        "signed": True,
        "unit": None,
    },
    "grid_frequency": {
        "address": 5036,
        "count": 1,
        "scale": 0.1,
        "type": "u16",
        "unit": "Hz",
    },
    
    # ===== HIGH PRECISION GRID FREQUENCY =====
    "grid_frequency_high_precision": {
        "address": 5242,
        "count": 1,
        "scale": 0.01,
        "type": "u16",
        "unit": "Hz",
    },
    
    # ===== BATTERY =====
    "battery_power": {
        "address": 5214,
        "count": 2,
        "scale": 1,
        "type": "s32",
        "signed": True,
        "unit": "W",
    },
    "battery_current": {
        "address": 5631,
        "count": 1,
        "scale": 0.1,
        "type": "s16",
        "signed": True,
        "unit": "A",
    },
    "bdc_rated_power": {
        "address": 5628,
        "count": 1,
        "scale": 100,
        "type": "u16",
        "unit": "W",
    },
    "max_charging_current_bms": {
        "address": 5635,
        "count": 1,
        "scale": 1,
        "type": "u16",
        "unit": "A",
    },
    "max_discharging_current_bms": {
        "address": 5636,
        "count": 1,
        "scale": 1,
        "type": "u16",
        "unit": "A",
    },
    
    # ===== METER =====
    "meter_power_phase_a": {
        "address": 5603,
        "count": 2,
        "scale": 1,
        "type": "s32",
        "signed": True,
        "unit": "W",
    },
    "meter_power_phase_b": {
        "address": 5605,
        "count": 2,
        "scale": 1,
        "type": "s32",
        "signed": True,
        "unit": "W",
    },
    "meter_power_phase_c": {
        "address": 5607,
        "count": 2,
        "scale": 1,
        "type": "s32",
        "signed": True,
        "unit": "W",
    },
    
    # ===== EXPORT LIMITS =====
    "export_limit_min": {
        "address": 5622,
        "count": 1,
        "scale": 10,
        "type": "u16",
        "unit": "W",
    },
    "export_limit_max": {
        "address": 5623,
        "count": 1,
        "scale": 10,
        "type": "u16",
        "unit": "W",
    },
}

# Holding Registers (FC 03) - System clock
MODBUS_HOLDING_REGISTERS: Final = {
    "system_clock_year": {
        "address": 5000,
        "count": 1,
        "scale": 1,
        "type": "u16",
        "unit": None,
    },
    "system_clock_month": {
        "address": 5001,
        "count": 1,
        "scale": 1,
        "type": "u16",
        "unit": None,
    },
    "system_clock_day": {
        "address": 5002,
        "count": 1,
        "scale": 1,
        "type": "u16",
        "unit": None,
    },
    "system_clock_hour": {
        "address": 5003,
        "count": 1,
        "scale": 1,
        "type": "u16",
        "unit": None,
    },
    "system_clock_minute": {
        "address": 5004,
        "count": 1,
        "scale": 1,
        "type": "u16",
        "unit": None,
    },
    "system_clock_second": {
        "address": 5005,
        "count": 1,
        "scale": 1,
        "type": "u16",
        "unit": None,
    },
}

# Running state mapping
RUNNING_STATES: Final = {
    0x0000: "Stop",
    0x0002: "Starting",
    0x0008: "Running",
    0x0010: "Fault",
    0x0020: "Standby",
    0x0040: "Initial Standby",
    0x0100: "Emergency Stop",
    0x8000: "Key Stop",
}

# iSolarCloud API endpoints
ISOLARCLOUD_BASE_URL: Final = "https://gateway.isolarcloud.com"
ISOLARCLOUD_API_ENDPOINTS: Final = {
    "plant_list": "/v1/powerStationService/getPsList",
    "device_list": "/v1/deviceService/getDeviceList",
    "device_points": "/v1/deviceService/getDevicePointMinute",
    "realtime_data": "/v1/deviceService/getDevicePointData",
}
