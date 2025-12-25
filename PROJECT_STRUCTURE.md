# Project Structure

This document describes the organization of the Sungrow WINET-S integration codebase.

## Directory Tree

```
sungrow-winet-s/
├── .github/
│   └── workflows/
│       └── ci.yml                    # GitHub Actions CI/CD pipeline
├── custom_components/
│   └── sungrow_winet_s/              # Main integration package
│       ├── api/                       # API client modules
│       │   ├── __init__.py
│       │   ├── modbus_client.py      # Modbus TCP client
│       │   ├── http_client.py        # HTTP API client
│       │   └── cloud_client.py       # iSolarCloud client
│       ├── translations/              # Localization files
│       │   └── en.json               # English translations
│       ├── __init__.py               # Integration setup
│       ├── config_flow.py            # Config Flow (UI setup)
│       ├── const.py                  # Constants and configs
│       ├── coordinator.py            # Data update coordinator
│       ├── manifest.json             # Integration metadata
│       ├── sensor.py                 # Sensor platform
│       └── strings.json              # Translation strings
├── tests/                            # Unit tests
│   ├── conftest.py                   # Test configuration
│   ├── test_init.py                  # Integration tests
│   ├── test_modbus_client.py         # Modbus tests
│   └── test_coordinator.py           # Coordinator tests
├── .gitignore                        # Git ignore patterns
├── CHANGELOG.md                      # Version history
├── CONTRIBUTING.md                   # Contribution guide
├── hacs.json                         # HACS metadata
├── INSTALLATION.md                   # Installation guide
├── LICENSE                           # MIT license
├── PROJECT_STRUCTURE.md              # This file
├── pyproject.toml                    # Python project config
├── README.md                         # Main documentation
└── requirements.txt                  # Dependencies
```

## Key Files Explained

### Core Integration

#### `__init__.py`
- Entry point for Home Assistant
- Sets up coordinator and platforms
- Handles entry setup/unload/reload
- **Key functions**: `async_setup_entry`, `async_unload_entry`

#### `manifest.json`
- Integration metadata for Home Assistant
- Defines dependencies, version, IoT class
- Required for Home Assistant to recognize the integration

#### `const.py`
- All constants in one place
- Modbus register definitions
- Sensor configurations
- API endpoints
- Default values
- **Easy to modify** for different inverter models

#### `config_flow.py`
- UI-based setup wizard
- Validates connections
- Supports three connection types
- Options flow for settings
- **Key classes**: `SungrowConfigFlow`, `SungrowOptionsFlow`

#### `coordinator.py`
- Manages data fetching
- Implements intelligent fallback logic
- Handles update intervals
- Error recovery
- **Key class**: `SungrowDataCoordinator`

#### `sensor.py`
- Creates sensor entities
- Maps data to Home Assistant sensors
- Sets device classes and state classes
- **Key class**: `SungrowSensor`

### API Clients

#### `api/modbus_client.py`
- **SungrowModbusClient**: Modbus TCP communication
- Reads holding registers
- Handles 16-bit and 32-bit values
- Automatic reconnection
- **Primary local method**

#### `api/http_client.py`
- **SungrowHTTPClient**: HTTP API access
- Local WINET-S HTTP endpoints
- Limited data availability
- **Fallback local method**

#### `api/cloud_client.py`
- **SungrowCloudClient**: iSolarCloud API
- OAuth 2.0 authentication
- MD5 signature generation
- Rate limit friendly (5 min intervals)
- **Cloud fallback method**

### Documentation

#### `README.md`
- Main documentation
- Feature overview
- Comprehensive setup guide
- Entity descriptions
- Troubleshooting
- Examples
- **Start here**

#### `INSTALLATION.md`
- Step-by-step installation
- Connection method guides
- Common issues and solutions
- Energy dashboard setup
- **For end users**

#### `CONTRIBUTING.md`
- Development setup
- Code style guidelines
- Testing procedures
- PR process
- **For developers**

#### `CHANGELOG.md`
- Version history
- Release notes
- Breaking changes
- **Track changes**

### Configuration

#### `pyproject.toml`
- Python project metadata
- Build configuration
- Tool settings (black, isort, mypy)
- Development dependencies

#### `requirements.txt`
- Runtime dependencies
- Specific versions for reproducibility
- Used by Home Assistant

#### `hacs.json`
- HACS metadata
- Integration category
- Minimum Home Assistant version
- **Required for HACS**

### Tests

#### `tests/conftest.py`
- Pytest configuration
- Common fixtures
- Mock Home Assistant instance

#### `tests/test_*.py`
- Unit tests for each module
- Mock external dependencies
- Test success and failure cases

### CI/CD

#### `.github/workflows/ci.yml`
- Automated testing
- Code quality checks (black, isort, mypy)
- HACS validation
- Hassfest validation
- Runs on push and PR

## Code Flow

### Setup Process
```
User adds integration
    ↓
config_flow.py validates connection
    ↓
__init__.py creates coordinator
    ↓
coordinator.py fetches initial data
    ↓
sensor.py creates entities
    ↓
Sensors appear in Home Assistant
```

### Data Update Cycle
```
Coordinator timer triggers
    ↓
coordinator._async_update_data()
    ↓
API client reads data (Modbus/HTTP/Cloud)
    ↓
Data stored in coordinator.data
    ↓
Sensors automatically update
```

### Fallback Logic
```
Primary method fails 3 times
    ↓
coordinator attempts fallback
    ↓
Try alternative local method
    ↓
If that fails, try cloud method
    ↓
If all fail, raise UpdateFailed
```

## Modifying the Integration

### Adding a New Sensor

1. **Add register to `const.py`**:
   ```python
   MODBUS_REGISTERS: Final = {
       # ...existing...
       "new_sensor": (register, count, scale, signed),
   }
   ```

2. **Add sensor config to `const.py`**:
   ```python
   SENSOR_TYPES: Final = {
       # ...existing...
       "new_sensor": {
           "name": "New Sensor",
           "icon": "mdi:icon-name",
           "unit": "unit",
           "device_class": "class",
           "state_class": "state_class",
       },
   }
   ```

3. **Test**: Reload integration, sensor appears automatically

### Changing Update Interval

Edit `const.py`:
```python
DEFAULT_SCAN_INTERVAL: Final = 30  # Change to desired seconds
```

### Supporting New Inverter Model

1. Research Modbus registers for your model
2. Update `MODBUS_REGISTERS` in `const.py`
3. Test and document
4. Submit PR with model details

## Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test
```bash
pytest tests/test_modbus_client.py -v
```

### With Coverage
```bash
pytest tests/ --cov=custom_components.sungrow_winet_s
```

## Code Quality

### Format Code
```bash
black custom_components/sungrow_winet_s
isort custom_components/sungrow_winet_s
```

### Type Check
```bash
mypy custom_components/sungrow_winet_s
```

## Architecture Principles

1. **Local First**: Prioritize local Modbus/HTTP over cloud
2. **Fault Tolerant**: Intelligent fallback, graceful degradation
3. **Async Everything**: Non-blocking operations
4. **Type Safe**: Type hints throughout
5. **Testable**: Mock external dependencies
6. **Maintainable**: Clear structure, good documentation
7. **HA Best Practices**: Follow Home Assistant guidelines

## Dependencies

- **pymodbus** (3.6.4): Modbus TCP communication
- **aiohttp** (3.9.3): Async HTTP client
- **cryptography** (42.0.5): RSA signing for cloud API

## Compatibility

- **Home Assistant**: 2024.1.0+
- **Python**: 3.11+
- **HACS**: 1.6.0+

## Resources

- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [pymodbus Documentation](https://pymodbus.readthedocs.io/)
- [Sungrow Protocol Docs](https://www.sungrowpower.com/)

## Questions?

- Check [README.md](README.md) for usage
- Check [INSTALLATION.md](INSTALLATION.md) for setup
- Check [CONTRIBUTING.md](CONTRIBUTING.md) for development
- Open an issue on GitHub
- Ask on Home Assistant Community Forum
