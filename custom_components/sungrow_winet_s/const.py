"""Constants for the Sungrow WINET-S Inverter integration."""
from datetime import timedelta
from typing import Final

# Integration domain
DOMAIN: Final = "sungrow_winet_s"

# Configuration and options
CONF_CONNECTION_TYPE: Final = "connection_type"
CONF_HOST: Final = "host"
CONF_PORT: Final = "port"
CONF_MODBUS_SLAVE_ID: Final = "modbus_slave_id"
CONF_API_KEY: Final = "api_key"
CONF_ACCESS_KEY: Final = "access_key"
CONF_RSA_KEY: Final = "rsa_key"
CONF_USERNAME: Final = "username"
CONF_PASSWORD: Final = "password"
CONF_PLANT_ID: Final = "plant_id"
CONF_DEVICE_SN: Final = "device_sn"
CONF_SCAN_INTERVAL: Final = "scan_interval"

# Connection types
CONNECTION_TYPE_MODBUS: Final = "modbus"
CONNECTION_TYPE_HTTP: Final = "http"
CONNECTION_TYPE_CLOUD: Final = "cloud"

# Defaults
DEFAULT_NAME: Final = "Sungrow Inverter"
DEFAULT_PORT_MODBUS: Final = 502
DEFAULT_PORT_HTTP: Final = 8082
DEFAULT_MODBUS_SLAVE_ID: Final = 1
DEFAULT_SCAN_INTERVAL: Final = 30  # seconds
DEFAULT_SCAN_INTERVAL_CLOUD: Final = 300  # 5 minutes for cloud to avoid rate limits
DEFAULT_TIMEOUT: Final = 10  # seconds

# Update intervals
UPDATE_INTERVAL_LOCAL: Final = timedelta(seconds=DEFAULT_SCAN_INTERVAL)
UPDATE_INTERVAL_CLOUD: Final = timedelta(seconds=DEFAULT_SCAN_INTERVAL_CLOUD)

# API endpoints
CLOUD_API_BASE_URL: Final = "https://augateway.isolarcloud.com"
CLOUD_API_TOKEN_URL: Final = f"{CLOUD_API_BASE_URL}/v1/userService/login"
CLOUD_API_PLANT_LIST_URL: Final = f"{CLOUD_API_BASE_URL}/v1/powerStationService/getPsList"
CLOUD_API_DEVICE_LIST_URL: Final = f"{CLOUD_API_BASE_URL}/v1/devService/getDeviceList"
CLOUD_API_REALTIME_DATA_URL: Final = f"{CLOUD_API_BASE_URL}/v1/devService/getDevicePoint"

# Modbus registers (Sungrow SH-series common registers)
# Format: (register, count, scale, signed)
MODBUS_REGISTERS: Final = {
    # PV Generation
    "pv_power": (5016, 2, 1, False),  # Total DC power (W) - U32
    "daily_pv_generation": (5002, 1, 0.1, False),  # Daily PV generation (kWh) - U16
    "total_pv_generation": (5003, 2, 1, False),  # Total PV generation (kWh) - U32
    
    # Battery
    "battery_soc": (13022, 1, 0.1, False),  # Battery SOC (%) - U16
    "battery_power": (13020, 2, 1, True),  # Battery power (W) - S32, negative=charging
    "battery_voltage": (13000, 1, 0.1, False),  # Battery voltage (V) - U16
    "battery_current": (13001, 1, 0.1, True),  # Battery current (A) - S16
    "battery_temp": (13007, 1, 0.1, True),  # Battery temperature (°C) - S16
    "daily_battery_charge": (13025, 1, 0.1, False),  # Daily charge (kWh) - U16
    "daily_battery_discharge": (13026, 1, 0.1, False),  # Daily discharge (kWh) - U16
    
    # Grid
    "grid_export_power": (13009, 2, 1, True),  # Export power (W) - S32, positive=export
    "daily_grid_export": (13034, 1, 0.1, False),  # Daily export (kWh) - U16
    "daily_grid_import": (13035, 1, 0.1, False),  # Daily import (kWh) - U16
    "total_grid_export": (13044, 2, 1, False),  # Total export (kWh) - U32
    "total_grid_import": (13045, 2, 1, False),  # Total import (kWh) - U32
    
    # Load
    "load_power": (13007, 2, 1, False),  # Load power (W) - U32
    "daily_load_consumption": (13036, 1, 0.1, False),  # Daily load (kWh) - U16
    
    # System status
    "inverter_status": (12999, 1, 1, False),  # Running state - U16
    "inverter_temp": (5007, 1, 0.1, True),  # Internal temperature (°C) - S16
    "daily_running_time": (5112, 1, 1, False),  # Daily running time (minutes) - U16
}

# Inverter status codes
INVERTER_STATUS: Final = {
    0: "Standby",
    1: "Running",
    2: "Fault",
    3: "Permanent Fault",
    4: "Initial Standby",
    5: "Starting",
    6: "Alarm",
}

# Sensor types and configurations
SENSOR_TYPES: Final = {
    "pv_power": {
        "name": "PV Power",
        "icon": "mdi:solar-power",
        "unit": "W",
        "device_class": "power",
        "state_class": "measurement",
    },
    "daily_pv_generation": {
        "name": "Daily PV Generation",
        "icon": "mdi:solar-power",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "total_pv_generation": {
        "name": "Total PV Generation",
        "icon": "mdi:solar-power",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "battery_soc": {
        "name": "Battery SOC",
        "icon": "mdi:battery",
        "unit": "%",
        "device_class": "battery",
        "state_class": "measurement",
    },
    "battery_power": {
        "name": "Battery Power",
        "icon": "mdi:battery-charging",
        "unit": "W",
        "device_class": "power",
        "state_class": "measurement",
    },
    "battery_voltage": {
        "name": "Battery Voltage",
        "icon": "mdi:flash",
        "unit": "V",
        "device_class": "voltage",
        "state_class": "measurement",
    },
    "battery_current": {
        "name": "Battery Current",
        "icon": "mdi:current-dc",
        "unit": "A",
        "device_class": "current",
        "state_class": "measurement",
    },
    "battery_temp": {
        "name": "Battery Temperature",
        "icon": "mdi:thermometer",
        "unit": "°C",
        "device_class": "temperature",
        "state_class": "measurement",
    },
    "daily_battery_charge": {
        "name": "Daily Battery Charge",
        "icon": "mdi:battery-plus",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "daily_battery_discharge": {
        "name": "Daily Battery Discharge",
        "icon": "mdi:battery-minus",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "grid_export_power": {
        "name": "Grid Export Power",
        "icon": "mdi:transmission-tower",
        "unit": "W",
        "device_class": "power",
        "state_class": "measurement",
    },
    "daily_grid_export": {
        "name": "Daily Grid Export",
        "icon": "mdi:transmission-tower-export",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "daily_grid_import": {
        "name": "Daily Grid Import",
        "icon": "mdi:transmission-tower-import",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "total_grid_export": {
        "name": "Total Grid Export",
        "icon": "mdi:transmission-tower-export",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "total_grid_import": {
        "name": "Total Grid Import",
        "icon": "mdi:transmission-tower-import",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "load_power": {
        "name": "Load Power",
        "icon": "mdi:home-lightning-bolt",
        "unit": "W",
        "device_class": "power",
        "state_class": "measurement",
    },
    "daily_load_consumption": {
        "name": "Daily Load Consumption",
        "icon": "mdi:home-lightning-bolt",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "inverter_status": {
        "name": "Inverter Status",
        "icon": "mdi:information",
        "unit": None,
        "device_class": None,
        "state_class": None,
    },
    "inverter_temp": {
        "name": "Inverter Temperature",
        "icon": "mdi:thermometer",
        "unit": "°C",
        "device_class": "temperature",
        "state_class": "measurement",
    },
    "daily_running_time": {
        "name": "Daily Running Time",
        "icon": "mdi:clock",
        "unit": "min",
        "device_class": "duration",
        "state_class": "total_increasing",
    },
}
