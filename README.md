# Sungrow WINET-S Inverter Integration for Home Assistant

[![HACS Badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Home Assistant custom integration for Sungrow inverters (SHx series, SG series) using the WINET-S communication device.

## Features

- **Local Modbus TCP** (Primary): Direct communication with your inverter for real-time data
- **Local HTTP API** (Fallback): Alternative local access via WINET-S HTTP endpoints
- **iSolarCloud API** (Cloud Fallback): Cloud-based access when local methods are unavailable
- **Comprehensive Sensors**: PV power, daily/total energy, battery SOC, grid import/export, temperatures, and more
- **Automatic Failover**: Seamlessly switches between communication methods
- **Configurable Polling**: Adjustable update intervals for local (30s default) and cloud (5 min default) modes

## Supported Models

- SH5K-20, SH5K-30, SH8K-20, SH10RT
- SG5K-D, SG8K-D, SG10KTL-M
- Other Sungrow inverters with WINET-S dongle

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL and select "Integration" as the category
6. Click "Add"
7. Search for "Sungrow WINET-S" and install
8. Restart Home Assistant

### Manual Installation

1. Download the `custom_components/sungrow_winet_s` folder
2. Copy it to your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant

## Configuration

### Setup via UI

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Sungrow WINET-S Inverter"
4. Choose your connection method:
   - **Local (Modbus TCP)**: Enter your inverter's IP address
   - **Local (HTTP API)**: Enter IP and optional credentials
   - **Cloud (iSolarCloud)**: Enter API credentials from developer portal

### Local Mode (Recommended)

For local Modbus TCP connection:
- **Host**: IP address of your WINET-S device
- **Port**: 502 (default Modbus TCP port)
- **Slave ID**: 1 (default)

### Cloud Mode

For iSolarCloud API access:
1. Register at [iSolarCloud Developer Portal](https://developer-api.isolarcloud.com/)
2. Create an application to get:
   - API Key
   - Access Key  
   - RSA Private Key
3. Enter these credentials during setup

## Entities

| Entity | Description | Unit | Device Class |
|--------|-------------|------|--------------|
| `sensor.sungrow_pv_power` | Current PV generation | W | power |
| `sensor.sungrow_daily_pv_energy` | Today's PV generation | kWh | energy |
| `sensor.sungrow_total_pv_energy` | Total PV generation | kWh | energy |
| `sensor.sungrow_battery_soc` | Battery state of charge | % | battery |
| `sensor.sungrow_battery_power` | Battery charge/discharge | W | power |
| `sensor.sungrow_grid_power` | Grid import/export | W | power |
| `sensor.sungrow_load_power` | House consumption | W | power |
| `sensor.sungrow_inverter_temp` | Inverter temperature | °C | temperature |
| `sensor.sungrow_inverter_status` | Running state | - | enum |

## Troubleshooting

### Connection Issues

- Ensure WINET-S is connected to your network
- Verify the IP address is correct and reachable
- Check that Modbus TCP port 502 is not blocked
- For cloud mode, verify API credentials are correct

### No Data

- Some registers may not be available on all models
- Check Home Assistant logs for specific errors
- Try switching between local and cloud modes

## License

MIT License - see [LICENSE](LICENSE) file
