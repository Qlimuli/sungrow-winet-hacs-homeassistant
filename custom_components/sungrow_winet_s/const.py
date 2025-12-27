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
DEFAULT_SCAN_INTERVAL_LOCAL: Final = timedelta(seconds=30)
DEFAULT_SCAN_INTERVAL_CLOUD: Final = timedelta(minutes=5)

# Note: addresses are "doc_addr" (1-based as in Sungrow documentation)
# The client will subtract 1 to get the protocol address
MODBUS_REGISTERS: Final = {
    # Input registers (FC 04) - Inverter data
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
        "scale": 1,
        "type": "u32",
        "unit": "kWh",
    },
    "total_running_time": {
        "address": 5006,
        "count": 2,
        "scale": 1,
        "type": "u32",
        "unit": "h",
    },
    "inverter_temp": {
        "address": 5008,
        "count": 1,
        "scale": 0.1,
        "type": "s16",
        "signed": True,
        "unit": "°C",
    },
    "pv1_voltage": {
        "address": 5011,
        "count": 1,
        "scale": 0.1,
        "type": "u16",
        "unit": "V",
    },
    "pv1_current": {
        "address": 5012,
        "count": 1,
        "scale": 0.1,
        "type": "u16",
        "unit": "A",
    },
    "pv_power": {
        "address": 5017,
        "count": 2,
        "scale": 1,
        "type": "u32",
        "unit": "W",
    },
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
    "grid_current_a": {
        "address": 5022,
        "count": 1,
        "scale": 0.1,
        "type": "u16",
        "unit": "A",
    },
    "grid_current_b": {
        "address": 5023,
        "count": 1,
        "scale": 0.1,
        "type": "u16",
        "unit": "A",
    },
    "grid_current_c": {
        "address": 5024,
        "count": 1,
        "scale": 0.1,
        "type": "u16",
        "unit": "A",
    },
    "active_power": {
        "address": 5031,
        "count": 2,
        "scale": 1,
        "type": "u32",
        "unit": "W",
    },
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
    "running_state": {
        "address": 5038,
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
