# Quick Start Guide

Get your Sungrow inverter connected to Home Assistant in 5 minutes!

## Prerequisites ✓
- [ ] Home Assistant 2024.1.0+ running
- [ ] HACS installed
- [ ] Sungrow inverter with WINET-S
- [ ] Know your WINET-S IP address OR iSolarCloud credentials

## Installation (2 minutes)

### Step 1: Add to HACS
1. Open HACS → Integrations
2. Click ⋮ (menu) → Custom repositories
3. Paste: `https://github.com/yourusername/sungrow-winet-s`
4. Category: Integration → Add
5. Search "Sungrow WINET-S" → Download
6. **Restart Home Assistant**

### Step 2: Add Integration
1. Settings → Devices & Services → + Add Integration
2. Search "Sungrow WINET-S" → Click it

### Step 3: Configure

**Choose ONE method:**

#### 🚀 Method A: Modbus TCP (Fastest, Local)
```
IP Address: 192.168.1.100  (your WINET-S IP)
Port: 502
Slave ID: 1
```
Click Submit → Done! ✅

#### 🌐 Method B: iSolarCloud (Remote)
```
Username: your.email@example.com
Password: ••••••••
Device SN: WNxxxxxxxx (from inverter label)
API Key: (leave blank)
```
Click Submit → Done! ✅

## Verify (30 seconds)

1. Settings → Devices & Services
2. Find "Sungrow WINET-S Inverter" 
3. Click it → Should see 17+ sensors
4. Check values (during daytime)

**Sensors you'll see:**
- ☀️ PV Power (current solar generation)
- 🔋 Battery SOC (%)
- ⚡ Grid Power (import/export)
- 🏠 Load Power (home consumption)
- 📊 Daily/Total Energy stats

## Add to Energy Dashboard (2 minutes)

Settings → Dashboards → Energy:

1. **Solar**: `sensor.sungrow_inverter_daily_pv_generation`
2. **Battery**:
   - In: `sensor.sungrow_inverter_daily_battery_charge`
   - Out: `sensor.sungrow_inverter_daily_battery_discharge`
3. **Grid**:
   - Import: `sensor.sungrow_inverter_daily_grid_import`
   - Export: `sensor.sungrow_inverter_daily_grid_export`

Save → Wait 2 hours for data to populate.

## Quick Automations

### Battery Low Notification
```yaml
automation:
  - alias: "Low Battery Alert"
    trigger:
      platform: numeric_state
      entity_id: sensor.sungrow_inverter_battery_soc
      below: 20
    action:
      service: notify.mobile_app
      data:
        message: "Battery at {{ states('sensor.sungrow_inverter_battery_soc') }}%"
```

### Daily Solar Report
```yaml
automation:
  - alias: "Evening Solar Summary"
    trigger:
      platform: time
      at: "20:00:00"
    action:
      service: notify.mobile_app
      data:
        message: "Today: {{ states('sensor.sungrow_inverter_daily_pv_generation') }} kWh solar"
```

## Troubleshooting

### ❌ "Cannot connect"
**Modbus:**
- Ping WINET-S: `ping 192.168.1.100`
- Check same network/VLAN
- Try port test: `telnet 192.168.1.100 502`

**Cloud:**
- Verify credentials at portal.isolarcloud.com
- Check device serial number matches exactly

### ❌ Sensors "Unavailable"
- **At night**: Normal for PV sensors
- **Always**: Check integration loaded in Devices & Services
- **Sometimes**: Check WiFi signal to WINET-S

### 🔍 Enable Debug Logs
`configuration.yaml`:
```yaml
logger:
  logs:
    custom_components.sungrow_winet_s: debug
```
Restart → Check Settings → System → Logs

## What's Next?

- ✅ Working sensors
- 📊 Energy dashboard populated
- 🤖 Automations created
- 🎉 Monitoring your solar!

**Optional:**
- Create custom Lovelace dashboard
- Set up battery optimization automations
- Monitor inverter temperature
- Track monthly production

## Need Help?

1. Check [README.md](README.md) - Full documentation
2. Check [INSTALLATION.md](INSTALLATION.md) - Detailed guide
3. [Home Assistant Forum](https://community.home-assistant.io/)
4. [GitHub Issues](https://github.com/yourusername/sungrow-winet-s/issues)

## Finding Your WINET-S IP

**Router Method:**
1. Log into router
2. DHCP clients → Look for "WINET" or "Sungrow"

**Network Scan:**
```bash
nmap -p 502,8082 192.168.1.0/24
```

**Sungrow App:**
1. Open app
2. Device settings → Network/WiFi
3. Note IP address

**Set Static IP (Recommended):**
- Assign static IP in router DHCP settings
- Prevents IP changes

---

**Total Time: 5-10 minutes from start to working sensors!** ⚡
