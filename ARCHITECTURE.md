# Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                       HOME ASSISTANT                             │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │          Sungrow WINET-S Integration                       │  │
│  │                                                            │  │
│  │  ┌──────────────────────────────────────────────────┐    │  │
│  │  │           Config Flow (Setup UI)                  │    │  │
│  │  │  - Choose: Modbus / HTTP / Cloud                 │    │  │
│  │  │  - Validate connection                            │    │  │
│  │  │  - Store config securely                          │    │  │
│  │  └──────────────────────────────────────────────────┘    │  │
│  │                        ↓                                   │  │
│  │  ┌──────────────────────────────────────────────────┐    │  │
│  │  │      Data Update Coordinator                      │    │  │
│  │  │  - Polls data every 30s (local) / 5min (cloud)   │    │  │
│  │  │  - Manages update cycle                           │    │  │
│  │  │  - Handles errors & fallback                      │    │  │
│  │  │  - Stores current data                            │    │  │
│  │  └──────────────────────────────────────────────────┘    │  │
│  │              ↓              ↓              ↓               │  │
│  │    ┌─────────────┐  ┌─────────────┐  ┌──────────────┐   │  │
│  │    │   Modbus    │  │    HTTP     │  │    Cloud     │   │  │
│  │    │   Client    │  │   Client    │  │   Client     │   │  │
│  │    │  (Primary)  │  │ (Fallback)  │  │ (Fallback)   │   │  │
│  │    └─────────────┘  └─────────────┘  └──────────────┘   │  │
│  │           ↓                ↓                 ↓            │  │
│  │  ┌──────────────────────────────────────────────────┐    │  │
│  │  │         17+ Sensor Entities                       │    │  │
│  │  │  - PV Power, Energy                               │    │  │
│  │  │  - Battery SOC, Power, Voltage, Current, Temp    │    │  │
│  │  │  - Grid Import/Export                             │    │  │
│  │  │  - Load Consumption                               │    │  │
│  │  │  - Inverter Status, Temperature                   │    │  │
│  │  └──────────────────────────────────────────────────┘    │  │
│  └────────────────────────────────────────────────────────────┘  │
│                               ↓                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Home Assistant Features                        │ │
│  │  - Energy Dashboard                                        │ │
│  │  - Lovelace Cards                                          │ │
│  │  - Automations                                             │ │
│  │  - History / Statistics                                    │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SYSTEMS                              │
│                                                                  │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐  │
│  │  WINET-S     │      │  WINET-S     │      │ iSolarCloud  │  │
│  │  Modbus TCP  │      │  HTTP API    │      │  Cloud API   │  │
│  │  Port: 502   │      │  Port: 8082  │      │  OAuth 2.0   │  │
│  │  (Local)     │      │  (Local)     │      │  (Internet)  │  │
│  └──────────────┘      └──────────────┘      └──────────────┘  │
│         ↓                       ↓                      ↓         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Sungrow Inverter                            │   │
│  │              (SH-Series Hybrid)                          │   │
│  │   ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐      │   │
│  │   │   PV   │  │Battery │  │  Grid  │  │  Load  │      │   │
│  │   │ Panels │  │ System │  │        │  │        │      │   │
│  │   └────────┘  └────────┘  └────────┘  └────────┘      │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Setup Phase

```
User → Config Flow → Choose Method → Validate Connection → Create Entry
                                            ↓
                        Coordinator Created → Initial Data Fetch
                                            ↓
                          Sensors Created → Values Populated
```

### Runtime Phase (Every 30 seconds)

```
Timer Triggers
    ↓
Coordinator: _async_update_data()
    ↓
Try Primary Method (Modbus/HTTP/Cloud)
    ↓
┌──── Success? ──┐
│ YES            │ NO
↓                ↓
Data Stored      Retry Count++
↓                ↓
Sensors Update   3 Failures?
                 ↓
              Try Fallback Method
                 ↓
              Success/Fail
                 ↓
              Update Sensors or Mark Unavailable
```

## Fallback Logic

```
┌─────────────────────────────────────────────────────────┐
│               Primary: Modbus TCP                        │
│  • Register: 5016 (PV Power)                            │
│  • Read every 30s                                       │
│  • Host: 192.168.1.100:502                              │
└─────────────────────────────────────────────────────────┘
                    ↓ (3 failures)
┌─────────────────────────────────────────────────────────┐
│            Fallback 1: HTTP API                          │
│  • Endpoint: /runtime/get                               │
│  • Host: 192.168.1.100:8082                             │
│  • Limited data available                               │
└─────────────────────────────────────────────────────────┘
                    ↓ (failures)
┌─────────────────────────────────────────────────────────┐
│         Fallback 2: iSolarCloud API                      │
│  • OAuth 2.0 Authentication                             │
│  • Endpoint: /v1/devService/getDevicePoint              │
│  • Slower (5 min intervals)                             │
└─────────────────────────────────────────────────────────┘
```

## Component Interaction

```
┌────────────────┐         ┌──────────────────┐
│  Config Entry  │────────▶│   Coordinator    │
│  (User Config) │         │  (Data Manager)  │
└────────────────┘         └──────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ↓               ↓               ↓
            ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
            │   Modbus     │ │     HTTP     │ │    Cloud     │
            │   Client     │ │    Client    │ │   Client     │
            └──────────────┘ └──────────────┘ └──────────────┘
                    │               │               │
                    └───────────────┼───────────────┘
                                    ↓
                          ┌──────────────────┐
                          │   Data Dict      │
                          │  {pv_power: 1500}│
                          │  {battery_soc: 85}│
                          └──────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ↓                               ↓
            ┌──────────────┐              ┌──────────────┐
            │  Sensor 1    │              │  Sensor 17   │
            │  (PV Power)  │     ...      │ (Inverter T) │
            └──────────────┘              └──────────────┘
```

## File Structure & Responsibilities

```
custom_components/sungrow_winet_s/
│
├── __init__.py                  → Integration setup & lifecycle
│   • async_setup_entry()       → Create coordinator, load platforms
│   • async_unload_entry()      → Cleanup on removal
│   • async_reload_entry()      → Reload on config change
│
├── config_flow.py               → User interface setup
│   • async_step_user()         → Choose connection type
│   • async_step_modbus()       → Modbus config
│   • async_step_http()         → HTTP config
│   • async_step_cloud()        → Cloud config
│   • validate_*_connection()   → Test connections
│
├── coordinator.py               → Data management
│   • _async_update_data()      → Fetch data on schedule
│   • _fetch_from_primary()     → Try main method
│   • _fetch_from_fallback()    → Try alternatives
│   • async_shutdown()          → Cleanup connections
│
├── sensor.py                    → Entity definitions
│   • async_setup_entry()       → Create sensor entities
│   • SungrowSensor class       → Individual sensor
│   • native_value property     → Get data from coordinator
│
├── const.py                     → Configuration
│   • MODBUS_REGISTERS          → Register mappings
│   • SENSOR_TYPES              → Sensor configurations
│   • Connection constants      → Defaults, timeouts
│
├── api/
│   ├── modbus_client.py        → Modbus implementation
│   │   • connect()             → Connect to device
│   │   • read_register()       → Read single register
│   │   • read_all_data()       → Read all sensors
│   │
│   ├── http_client.py          → HTTP implementation
│   │   • get_runtime_data()    → Get current values
│   │   • get_device_info()     → Get device details
│   │
│   └── cloud_client.py         → Cloud implementation
│       • authenticate()         → OAuth login
│       • get_realtime_data()   → Get current values
│       • _generate_signature() → MD5 signing
│
└── manifest.json                → HA metadata
    • domain, version, requirements
```

## State Management

```
┌─────────────────────────────────────────────────────────┐
│              Home Assistant State Machine                │
│                                                          │
│  Entity: sensor.sungrow_inverter_pv_power               │
│  State: 1500                                            │
│  Attributes:                                            │
│    - unit_of_measurement: W                             │
│    - device_class: power                                │
│    - state_class: measurement                           │
│    - friendly_name: Sungrow Inverter PV Power          │
│  Device:                                                │
│    - identifiers: {sungrow_winet_s, entry_id}          │
│    - name: Sungrow Inverter                            │
│    - manufacturer: Sungrow                              │
│    - model: WINET-S Compatible Inverter                │
└─────────────────────────────────────────────────────────┘
```

## Energy Dashboard Integration

```
┌──────────────────────────────────────────────────────┐
│         Home Assistant Energy Dashboard               │
│                                                       │
│  Solar Production:                                    │
│    sensor.sungrow_inverter_daily_pv_generation      │
│                                                       │
│  Battery:                                            │
│    In:  sensor.sungrow_inverter_daily_battery_charge│
│    Out: sensor.sungrow_inverter_daily_battery_discharge│
│                                                       │
│  Grid:                                               │
│    Import: sensor.sungrow_inverter_daily_grid_import│
│    Export: sensor.sungrow_inverter_daily_grid_export│
│                                                       │
│  Home Consumption:                                    │
│    sensor.sungrow_inverter_daily_load_consumption   │
└──────────────────────────────────────────────────────┘
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────┐
│               GitHub Repository                      │
│  github.com/yourusername/sungrow-winet-s           │
│                                                     │
│  Releases:                                          │
│    - v1.0.0 (tagged)                               │
│    - Source code (zip)                             │
│    - Release notes                                 │
└─────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────┐
│                    HACS                              │
│  Home Assistant Community Store                     │
│                                                     │
│  Integration Discovery:                             │
│    - Custom repository URL                          │
│    - Auto-update notifications                      │
│    - One-click installation                         │
└─────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────┐
│          Home Assistant Instance                     │
│  /config/custom_components/sungrow_winet_s/        │
│                                                     │
│  Loaded on startup:                                 │
│    - Manifest validated                             │
│    - Dependencies installed                         │
│    - Integration registered                         │
└─────────────────────────────────────────────────────┘
```

---

**This integration follows Home Assistant architecture best practices:**
- Async/await throughout
- DataUpdateCoordinator pattern
- Config Flow (no YAML)
- Proper device/entity registry
- State classes for statistics
- Device classes for UI
- Error handling & recovery
- Localization support
