# Installation Guide

## Quick Start

This guide will help you set up the Sungrow WINET-S integration in Home Assistant.

## Prerequisites

- Home Assistant 2024.1.0 or newer
- HACS installed (for easiest installation)
- Sungrow inverter with WINET-S communication device
- Network access to WINET-S (for local methods) OR iSolarCloud account (for cloud method)

## Step 1: Install via HACS

1. Open Home Assistant
2. Go to **HACS** → **Integrations**
3. Click the **three dots** (⋮) in the top right
4. Select **Custom repositories**
5. Add repository URL: `https://github.com/yourusername/sungrow-winet-s`
6. Category: **Integration**
7. Click **Add**
8. Search for "**Sungrow WINET-S**"
9. Click **Download**
10. **Restart Home Assistant**

## Step 2: Find Your WINET-S IP Address

### Method A: Check Router
1. Log into your router
2. Look for DHCP client list
3. Find device named "WINET" or "Sungrow"
4. Note the IP address (e.g., `192.168.1.100`)

### Method B: Network Scan
Run this command from a computer on your network:
```bash
nmap -p 502,8082 192.168.1.0/24
```
Look for devices with open ports 502 (Modbus) or 8082 (HTTP).

### Method C: Sungrow App
1. Open the Sungrow app on your phone
2. Go to device settings
3. Look for network/WiFi settings
4. Note the IP address

## Step 3: Add Integration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "**Sungrow WINET-S**"
4. Click on it

## Step 4: Choose Connection Method

### Option A: Modbus TCP (Recommended)

**Best for**: Fast updates, local control, no internet required

**Configuration:**
- **IP Address**: Your WINET-S IP (e.g., `192.168.1.100`)
- **Port**: `502` (default Modbus port)
- **Modbus Slave ID**: `1` (usually)

**Test**: Click Submit. If successful, you'll see "Success!" message.

**Troubleshooting:**
- ❌ "Cannot connect"
  - Verify IP address is correct
  - Check WINET-S is powered on
  - Ensure Home Assistant and WINET-S are on same network
  - Try setting static IP for WINET-S in router

### Option B: HTTP API

**Best for**: When Modbus is blocked, simpler setup

**Configuration:**
- **IP Address**: Your WINET-S IP
- **Port**: `8082` (default HTTP port)

**Note**: HTTP API has limited data compared to Modbus.

### Option C: iSolarCloud (Cloud)

**Best for**: Remote monitoring, when local access not available

**Configuration:**
- **Username**: Your iSolarCloud email
- **Password**: Your iSolarCloud password  
- **API Key**: (Optional - leave blank unless you have one)
- **Device Serial Number**: Found on inverter label or in app

**Finding Serial Number:**
1. Check physical label on inverter
2. Or open Sungrow app → Device Details
3. Or log into iSolarCloud web portal

**Note**: Cloud polling is slower (5 min intervals) to respect rate limits.

## Step 5: Verify Sensors

1. Go to **Settings** → **Devices & Services**
2. Find "**Sungrow WINET-S Inverter**"
3. Click on it
4. You should see your inverter device
5. Click the device
6. Verify sensors are showing data:
   - PV Power
   - Battery SOC
   - Grid Power
   - etc.

**During nighttime**: PV sensors will show 0 or unavailable - this is normal!

## Step 6: Add to Energy Dashboard (Optional)

1. Go to **Settings** → **Dashboards** → **Energy**
2. Click **Add Solar Production**
   - Select: `sensor.sungrow_inverter_daily_pv_generation`
3. Click **Add Battery System**
   - Energy in: `sensor.sungrow_inverter_daily_battery_charge`
   - Energy out: `sensor.sungrow_inverter_daily_battery_discharge`
4. Click **Add Grid Consumption**
   - Consumption: `sensor.sungrow_inverter_daily_grid_import`
   - Return: `sensor.sungrow_inverter_daily_grid_export`
5. **Save**

Wait 2 hours for initial energy dashboard data to appear.

## Step 7: Adjust Settings (Optional)

1. Go to **Settings** → **Devices & Services**
2. Find "Sungrow WINET-S Inverter"
3. Click **Configure**
4. Adjust **Update Interval**:
   - Local: 30 seconds (default) - can go as low as 10s
   - Cloud: 300 seconds (5 min) - don't go lower to avoid rate limits

## Common Issues

### "Cannot connect" Error

**For Modbus:**
1. Ping the WINET-S: `ping 192.168.1.100`
2. Check port is open: `telnet 192.168.1.100 502`
3. Verify no firewall blocking port 502
4. Try HTTP method instead

**For HTTP:**
1. Test in browser: `http://192.168.1.100:8082`
2. Should see some response (even error page)
3. If timeout, check firewall

**For Cloud:**
1. Verify credentials in iSolarCloud web portal
2. Check device serial number is exact match
3. Ensure device is online in iSolarCloud

### Sensors Show "Unavailable"

- **At night**: Normal for PV sensors
- **All the time**: Check connection in Devices & Services
- **Intermittent**: Check WiFi signal to WINET-S

### Data Not Updating

1. Check integration status (should be "Loaded")
2. Look at last update time on sensors
3. Check Home Assistant logs for errors:
   - **Settings** → **System** → **Logs**
   - Search for "sungrow"
4. Try reloading integration
5. Try restarting Home Assistant

## Next Steps

- Create automations (see README for examples)
- Add sensors to Lovelace dashboards
- Set up notifications for low battery, high production, etc.
- Explore advanced features

## Getting Help

If you're stuck:

1. Check the [README](README.md) for detailed documentation
2. Enable debug logging (see README)
3. Post on [Home Assistant Community Forum](https://community.home-assistant.io/)
4. Open an issue on [GitHub](https://github.com/yourusername/sungrow-winet-s/issues)

When asking for help, include:
- Your inverter model
- Connection method used
- Relevant log entries
- What you've already tried
