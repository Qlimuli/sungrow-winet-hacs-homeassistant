# Sungrow WINET-S Inverter Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/yourusername/sungrow-winet-s)

A complete Home Assistant custom integration for Sungrow inverters (especially SH-series hybrid inverters) using the WINET-S communication device. This integration provides local-first monitoring with intelligent cloud fallback.

## Features

✅ **Multiple Connection Methods**
- **Modbus TCP** (Primary, best performance) - Direct connection via WINET-S on local network
- **HTTP API** (Fallback) - Local HTTP access to WINET-S device
- **iSolarCloud API** (Cloud fallback) - Internet-based monitoring when local access unavailable

✅ **Comprehensive Monitoring**
- Real-time PV power generation
- Battery state of charge (SOC) and power flow
- Grid import/export monitoring
- Load consumption tracking
- Daily and total energy statistics
- Inverter status and temperature
- Automatic unit conversions and proper Home Assistant device classes

✅ **Smart Features**
- Intelligent fallback between connection methods
- Efficient polling with configurable intervals
- Automatic reconnection on failures
- Full async/await implementation
- Energy dashboard compatible

✅ **Easy Setup**
- Configuration via UI (Config Flow)
- No YAML configuration required
- HACS compatible for easy installation and updates

## Supported Inverters

This integration is optimized for Sungrow **SH-series** hybrid inverters:
- SH5K, SH5.0RT
- SH6K, SH6.0RT
- SH8K, SH8.0RT
- SH10RT, SH10.0RT
- Other WINET-S compatible models

**Note**: Modbus register addresses may vary by model. The integration uses common registers for SH-series inverters. If you have a different model, you may need to adjust register mappings in `const.py`.

## Requirements

- Home Assistant 2024.1.0 or newer
- Python 3.11 or newer
- WINET-S dongle connected to your inverter
- For local access: WINET-S on same network as Home Assistant
- For cloud access: iSolarCloud account with inverter registered

## Installation

### Method 1: HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/yourusername/sungrow-winet-s`
6. Select category: "Integration"
7. Click "Add"
8. Search for "Sungrow WINET-S Inverter" and install
9. Restart Home Assistant

### Method 2: Manual Installation

1. Download the latest release from GitHub
2. Extract the `custom_components/sungrow_winet_s` folder
3. Copy it to your Home Assistant `config/custom_components/` directory
4. Restart Home Assistant

## Configuration

### Setup via UI

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Sungrow WINET-S Inverter"
4. Choose your connection method:

#### Option A: Modbus TCP (Recommended for local access)

- **IP Address**: IP address of your WINET-S device (e.g., `192.168.1.100`)
- **Port**: Modbus TCP port (default: `502`)
- **Modbus Slave ID**: Usually `1` (check your inverter manual)

**Finding your WINET-S IP address:**
- Check your router's DHCP client list
- Use the Sungrow app to view WINET-S settings
- Scan your network: `nmap -p 502 192.168.1.0/24`

#### Option B: HTTP API (Alternative local access)

- **IP Address**: IP address of your WINET-S device
- **Port**: HTTP port (default: `8082`)

#### Option C: iSolarCloud (Cloud access)

- **Username**: Your iSolarCloud account email
- **Password**: Your iSolarCloud password
- **API Key**: (Optional) For advanced API features
- **Device Serial Number**: Your inverter's serial number

**Finding your device serial number:**
- Check the inverter label
- Look in the Sungrow app under device details
- Check your iSolarCloud account

5. Click **Submit** - the integration will validate the connection
6. Your Sungrow inverter device will appear with all sensors

### Configuration Options

After setup, you can adjust settings:

1. Go to **Settings** → **Devices & Services**
2. Find "Sungrow WINET-S Inverter"
3. Click **Configure**

**Available Options:**
- **Update Interval**: How often to poll data (default: 30 seconds for local, 300 seconds for cloud)

## Available Entities

The integration creates the following sensor entities:

### Power Generation
| Entity | Description | Unit | Device Class |
|--------|-------------|------|--------------|
| `sensor.sungrow_inverter_pv_power` | Current PV power generation | W | power |
| `sensor.sungrow_inverter_daily_pv_generation` | Today's PV energy | kWh | energy |
| `sensor.sungrow_inverter_total_pv_generation` | Lifetime PV energy | kWh | energy |

### Battery
| Entity | Description | Unit | Device Class |
|--------|-------------|------|--------------|
| `sensor.sungrow_inverter_battery_soc` | Battery state of charge | % | battery |
| `sensor.sungrow_inverter_battery_power` | Battery charge/discharge power | W | power |
| `sensor.sungrow_inverter_battery_voltage` | Battery voltage | V | voltage |
| `sensor.sungrow_inverter_battery_current` | Battery current | A | current |
| `sensor.sungrow_inverter_battery_temp` | Battery temperature | °C | temperature |
| `sensor.sungrow_inverter_daily_battery_charge` | Today's battery charge | kWh | energy |
| `sensor.sungrow_inverter_daily_battery_discharge` | Today's battery discharge | kWh | energy |

### Grid
| Entity | Description | Unit | Device Class |
|--------|-------------|------|--------------|
| `sensor.sungrow_inverter_grid_export_power` | Grid export/import power | W | power |
| `sensor.sungrow_inverter_daily_grid_export` | Today's grid export | kWh | energy |
| `sensor.sungrow_inverter_daily_grid_import` | Today's grid import | kWh | energy |
| `sensor.sungrow_inverter_total_grid_export` | Lifetime grid export | kWh | energy |
| `sensor.sungrow_inverter_total_grid_import` | Lifetime grid import | kWh | energy |

### Load & System
| Entity | Description | Unit | Device Class |
|--------|-------------|------|--------------|
| `sensor.sungrow_inverter_load_power` | Current load consumption | W | power |
| `sensor.sungrow_inverter_daily_load_consumption` | Today's load consumption | kWh | energy |
| `sensor.sungrow_inverter_inverter_status` | Inverter operating status | - | - |
| `sensor.sungrow_inverter_inverter_temp` | Inverter temperature | °C | temperature |
| `sensor.sungrow_inverter_daily_running_time` | Today's running time | min | duration |

**All energy sensors include proper state classes for Home Assistant Energy Dashboard integration.**

## Energy Dashboard Integration

To add your Sungrow inverter to the Home Assistant Energy Dashboard:

1. Go to **Settings** → **Dashboards** → **Energy**
2. **Solar Production**: Add `sensor.sungrow_inverter_daily_pv_generation`
3. **Battery Storage**:
   - Charge: Add `sensor.sungrow_inverter_daily_battery_charge`
   - Discharge: Add `sensor.sungrow_inverter_daily_battery_discharge`
4. **Grid**:
   - Import: Add `sensor.sungrow_inverter_daily_grid_import`
   - Export: Add `sensor.sungrow_inverter_daily_grid_export`
5. **Home Consumption**: Add `sensor.sungrow_inverter_daily_load_consumption`

## Automation Examples

### Notify when battery is low
```yaml
automation:
  - alias: "Battery Low Warning"
    trigger:
      - platform: numeric_state
        entity_id: sensor.sungrow_inverter_battery_soc
        below: 20
    action:
      - service: notify.mobile_app
        data:
          title: "Battery Low"
          message: "Home battery is at {{ states('sensor.sungrow_inverter_battery_soc') }}%"
```

### Track daily solar production
```yaml
automation:
  - alias: "Daily Solar Report"
    trigger:
      - platform: time
        at: "20:00:00"
    action:
      - service: notify.mobile_app
        data:
          title: "Daily Solar Report"
          message: >
            Today's solar production: {{ states('sensor.sungrow_inverter_daily_pv_generation') }} kWh
            Battery charged: {{ states('sensor.sungrow_inverter_daily_battery_charge') }} kWh
```

## Troubleshooting

### Connection Issues

**Modbus connection fails:**
- Verify WINET-S IP address is correct and reachable
- Check that Modbus TCP is enabled on WINET-S (port 502)
- Ensure Home Assistant and WINET-S are on the same network/VLAN
- Try setting a static IP for WINET-S in your router
- Check firewall rules

**HTTP connection fails:**
- Verify WINET-S IP address
- Check HTTP port (usually 8082)
- Some WINET-S firmware versions have limited HTTP API support

**Cloud connection fails:**
- Verify iSolarCloud credentials
- Ensure device serial number is correct
- Check that device is registered in your iSolarCloud account
- Verify internet connectivity

### Sensor Data Issues

**Some sensors show "Unknown" or "Unavailable":**
- Normal during nighttime for PV-related sensors
- Some registers may not be supported by your inverter model
- Check Home Assistant logs for specific errors

**Data not updating:**
- Check the integration status in **Settings** → **Devices & Services**
- Verify update interval in options
- Check Home Assistant logs for connection errors
- Try reloading the integration

### Debug Logging

To enable debug logging, add to `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.sungrow_winet_s: debug
    pymodbus: debug
```

Then restart Home Assistant and check **Settings** → **System** → **Logs**.

## Advanced Configuration

### Customizing Modbus Registers

If your inverter model uses different registers, edit `custom_components/sungrow_winet_s/const.py`:

```python
MODBUS_REGISTERS: Final = {
    "pv_power": (5016, 2, 1, False),  # (register, count, scale, signed)
    # Add or modify registers here
}
```

Format: `(register_address, register_count, scale_factor, is_signed)`

### Fallback Behavior

The integration automatically falls back to alternative connection methods after 3 consecutive failures:
- Modbus → HTTP → Cloud
- HTTP → Modbus → Cloud
- Cloud → (no fallback)

To disable fallback, remove alternative credentials from config.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Known Limitations

- HTTP API support varies by WINET-S firmware version
- Cloud API has rate limits (5-minute minimum update interval recommended)
- Some advanced features (export limits, battery control) not yet implemented
- Register mappings optimized for SH-series; other models may need adjustments

## Roadmap

- [ ] Support for SG series (string inverters without battery)
- [ ] Export limit configuration via HTTP API
- [ ] Battery charge/discharge control
- [ ] Number entities for settings
- [ ] Multi-device support for commercial installations
- [ ] Diagnostic sensors for detailed troubleshooting

## Credits

This integration is inspired by and references:
- [Sungrow Modbus Protocol Documentation](https://www.sungrowpower.com/)
- [Home Assistant Integration Blueprint](https://github.com/jpawlowski/hacs.integration_blueprint)
- [iSolarCloud API Documentation](https://developer-api.isolarcloud.com/)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/sungrow-winet-s/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/sungrow-winet-s/discussions)
- **Home Assistant Community**: [Community Forum](https://community.home-assistant.io/)

## Disclaimer

This integration is not affiliated with or endorsed by Sungrow Power Supply Co., Ltd. Use at your own risk. The authors are not responsible for any damage to your equipment or data loss.

---

**If this integration helps you, consider starring ⭐ the repository!**
