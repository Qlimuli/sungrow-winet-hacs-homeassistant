# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-XX

### Added
- Initial release
- Modbus TCP support for local communication
- HTTP API support as fallback
- iSolarCloud API support for remote monitoring
- Intelligent fallback between connection methods
- Config Flow for UI-based setup
- 17+ sensor entities covering:
  - PV power and energy
  - Battery SOC, power, voltage, current, temperature
  - Grid import/export
  - Load consumption
  - Inverter status and temperature
- Energy Dashboard integration
- Proper Home Assistant device classes and state classes
- Support for SH-series hybrid inverters
- Async/await implementation
- Configurable update intervals
- Comprehensive documentation
- Unit tests
- HACS compatibility

### Technical Details
- Based on pymodbus 3.6.4
- Uses aiohttp for HTTP/cloud requests
- Implements DataUpdateCoordinator pattern
- Full type hints
- MIT License

## [Unreleased]

### Planned Features
- Support for SG series inverters (string inverters)
- Battery charge/discharge control
- Export limit configuration
- Multi-inverter support
- Additional diagnostic sensors
- Switch entities for control features

---

[1.0.0]: https://github.com/yourusername/sungrow-winet-s/releases/tag/v1.0.0
