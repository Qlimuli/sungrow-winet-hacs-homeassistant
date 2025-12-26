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
CONF_API_KEY: Final = "api_key"
CONF_ACCESS_KEY: Final = "access_key"
CONF_RSA_PRIVATE_KEY: Final = "rsa_private_key"
CONF_PLANT_ID: Final = "plant_id"
CONF_DEVICE_SN: Final = "device_sn"

# Defaults
DEFAULT_MODBUS_PORT: Final = 502
DEFAULT_MODBUS_SLAVE_ID: Final = 1
DEFAULT_HTTP_PORT: Final = 80
DEFAULT_SCAN_INTERVAL_LOCAL: Final = timedelta(seconds=30)
DEFAULT_SCAN_INTERVAL_CLOUD: Final = timedelta(minutes=5)

# Modbus register addresses (Sungrow standard registers)
MODBUS_REGISTERS: Final = {
    # Input registers (read-only)
    "pv1_voltage": {"address": 5011, "count": 1, "scale": 0.1, "unit": "V"},
    "pv1_current": {"address": 5012, "count": 1, "scale": 0.1, "unit": "A"},
    "pv2_voltage": {"address": 5013, "count": 1, "scale": 0.1, "unit": "V"},
    "pv2_current": {"address": 5014, "count": 1, "scale": 0.1, "unit": "A"},
    "pv_power": {"address": 5016, "count": 2, "scale": 1, "unit": "W", "signed": False},
    "daily_pv_energy": {"address": 5003, "count": 1, "scale": 0.1, "unit": "kWh"},
    "total_pv_energy": {"address": 5004, "count": 2, "scale": 0.1, "unit": "kWh"},
    "grid_frequency": {"address": 5035, "count": 1, "scale": 0.1, "unit": "Hz"},
    "inverter_temp": {"address": 5008, "count": 1, "scale": 0.1, "unit": "°C"},
    "running_state": {"address": 13000, "count": 1, "scale": 1, "unit": None},
    # Battery registers (for hybrid inverters)
    "battery_soc": {"address": 13022, "count": 1, "scale": 0.1, "unit": "%"},
    "battery_power": {"address": 13021, "count": 1, "scale": 1, "unit": "W", "signed": True},
    "battery_voltage": {"address": 13019, "count": 1, "scale": 0.1, "unit": "V"},
    "battery_current": {"address": 13020, "count": 1, "scale": 0.1, "unit": "A", "signed": True},
    "battery_temp": {"address": 13023, "count": 1, "scale": 0.1, "unit": "°C"},
    "daily_battery_charge": {"address": 13026, "count": 1, "scale": 0.1, "unit": "kWh"},
    "daily_battery_discharge": {"address": 13027, "count": 1, "scale": 0.1, "unit": "kWh"},
    # Grid registers
    "grid_power": {"address": 13009, "count": 2, "scale": 1, "unit": "W", "signed": True},
    "daily_import_energy": {"address": 13036, "count": 1, "scale": 0.1, "unit": "kWh"},
    "daily_export_energy": {"address": 13045, "count": 1, "scale": 0.1, "unit": "kWh"},
    "total_import_energy": {"address": 13037, "count": 2, "scale": 0.1, "unit": "kWh"},
    "total_export_energy": {"address": 13046, "count": 2, "scale": 0.1, "unit": "kWh"},
    # Load registers
    "load_power": {"address": 13007, "count": 2, "scale": 1, "unit": "W"},
    "daily_load_energy": {"address": 13028, "count": 1, "scale": 0.1, "unit": "kWh"},
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
