"""Raw Modbus TCP client for Sungrow inverters.

Based on working implementation that uses raw socket communication
instead of pymodbus library for better Sungrow compatibility.
"""
from __future__ import annotations

import asyncio
import logging
import socket
import ssl
import struct
import time
from typing import Any

from ..const import MODBUS_REGISTERS, MODBUS_HOLDING_REGISTERS, RUNNING_STATES

_LOGGER = logging.getLogger(__name__)

# Modbus Function Codes
FC_READ_HOLDING_REGISTERS = 0x03
FC_READ_INPUT_REGISTERS = 0x04

# Validation limits for sensor values - only reject truly impossible values
# Values of 0 are generally allowed (inverter might be off/idle)
# Use very generous limits to avoid false positives
VALUE_LIMITS: dict[str, tuple[float, float]] = {
    # Temperature limits (in °C) - allow wide range
    "inverter_temp": (-50, 150),
    # Voltage limits (in V) - 0 is valid when off
    "mppt1_voltage": (0, 2000),
    "mppt2_voltage": (0, 2000),
    "mppt3_voltage": (0, 2000),
    "mppt4_voltage": (0, 2000),
    "grid_voltage_a": (0, 1000),
    "grid_voltage_b": (0, 1000),
    "grid_voltage_c": (0, 1000),
    # Current limits (in A) - 0 is valid
    "mppt1_current": (0, 100),
    "mppt2_current": (0, 100),
    "mppt3_current": (0, 100),
    "mppt4_current": (0, 100),
    "battery_current": (-500, 500),
    # Power limits (in W) - 0 is valid
    "total_dc_power": (0, 500000),
    "battery_power": (-100000, 100000),
    "meter_power_phase_a": (-100000, 100000),
    "meter_power_phase_b": (-100000, 100000),
    "meter_power_phase_c": (-100000, 100000),
    # Frequency limits (in Hz) - 0 is valid when not connected to grid
    "grid_frequency": (0, 70),
    "grid_frequency_high_precision": (0, 70),
    # Power factor - can be 0
    "power_factor": (-1.5, 1.5),
    # Energy limits (in kWh) - allow very high values for large systems
    "daily_pv_energy": (0, 10000),
    "total_pv_energy": (0, 1000000000),  # 1 TWh should cover any system
    # Nominal power (in kW)
    "nominal_power": (0, 10000),
}


class SungrowModbusClient:
    """Client for communicating with Sungrow inverter via raw Modbus TCP."""

    def __init__(
        self,
        host: str,
        port: int = 502,
        slave_id: int = 1,
        use_tls: bool = False,
    ) -> None:
        """Initialize the Modbus client."""
        self._host = host
        self._port = int(port)
        self._slave_id = int(slave_id)
        self._use_tls = use_tls
        self._socket: socket.socket | ssl.SSLSocket | None = None
        self._lock = asyncio.Lock()
        self._transaction_id = 0
        self._timeout = 10
        self._retry_count = 2  # Reduced retries to speed up reads
        self._retry_delay = 0.5
        self._last_valid_data: dict[str, Any] = {}
        self._last_successful_read: float = 0
        self._consecutive_total_failures = 0  # Only count complete failures
        self._max_consecutive_failures = 10  # More tolerant

    def _get_next_transaction_id(self) -> int:
        """Get next transaction ID (wraps at 65535)."""
        self._transaction_id = (self._transaction_id + 1) & 0xFFFF
        return self._transaction_id

    def _build_modbus_request(
        self,
        function_code: int,
        address: int,
        count: int,
    ) -> bytes:
        """Build a Modbus TCP request frame."""
        transaction_id = self._get_next_transaction_id()
        protocol_id = 0
        # Unit ID (1 byte) + Function Code (1 byte) + Address (2 bytes) + Count (2 bytes)
        data = struct.pack(">HH", address, count)
        length = 1 + 1 + len(data)  # unit_id + function_code + data

        # MBAP Header + PDU
        header = struct.pack(
            ">HHHBB",
            transaction_id,
            protocol_id,
            length,
            self._slave_id,
            function_code,
        )
        return header + data

    def _parse_modbus_response(self, response: bytes) -> dict | None:
        """Parse a Modbus TCP response frame."""
        if len(response) < 9:
            _LOGGER.warning("Response too short: %d bytes", len(response))
            return None

        transaction_id, protocol_id, length = struct.unpack(">HHH", response[:6])
        unit_id = response[6]
        function_code = response[7]

        if len(response) < 6 + length:
            _LOGGER.warning(
                "Incomplete response: expected %d bytes, got %d",
                6 + length,
                len(response),
            )
            return None

        # Check for exception response
        if function_code & 0x80:
            exception_code = response[8] if len(response) > 8 else 0
            _LOGGER.warning(
                "Modbus exception: function=%02x, exception=%02x",
                function_code,
                exception_code,
            )
            return None

        # Data starts after byte count (response[8])
        byte_count = response[8]
        data = response[9 : 9 + byte_count]

        return {
            "transaction_id": transaction_id,
            "unit_id": unit_id,
            "function_code": function_code,
            "data": data,
        }

    async def _send_request(self, request: bytes) -> bytes:
        """Send request and receive response."""
        loop = asyncio.get_event_loop()

        def _sync_send_receive() -> bytes:
            if not self._socket:
                raise ConnectionError("Socket not connected")

            self._socket.settimeout(self._timeout)
            self._socket.sendall(request)

            response = b""
            while True:
                try:
                    chunk = self._socket.recv(1024)
                    if not chunk:
                        break
                    response += chunk
                    # Check if we have complete response
                    if len(response) >= 6:
                        _, _, length = struct.unpack(">HHH", response[:6])
                        if len(response) >= 6 + length:
                            break
                except socket.timeout:
                    break

            return response

        return await loop.run_in_executor(None, _sync_send_receive)

    async def connect(self) -> bool:
        """Establish connection to the inverter."""
        async with self._lock:
            try:
                loop = asyncio.get_event_loop()

                def _sync_connect() -> socket.socket | ssl.SSLSocket:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(self._timeout)
                    sock.connect((self._host, self._port))

                    if self._use_tls:
                        context = ssl.create_default_context()
                        context.check_hostname = False
                        context.verify_mode = ssl.CERT_NONE
                        return context.wrap_socket(sock, server_hostname=self._host)

                    return sock

                self._socket = await loop.run_in_executor(None, _sync_connect)
                conn_type = "TLS" if self._use_tls else "Plain TCP"
                _LOGGER.info(
                    "Connected to Sungrow inverter at %s:%s (%s)",
                    self._host,
                    self._port,
                    conn_type,
                )
                return True

            except Exception as err:
                _LOGGER.error("Failed to connect to Modbus: %s", err)
                self._socket = None
                return False

    async def disconnect(self) -> None:
        """Disconnect from the inverter."""
        async with self._lock:
            if self._socket:
                try:
                    self._socket.close()
                except Exception:
                    pass
                self._socket = None
                _LOGGER.info("Disconnected from Sungrow inverter")

    async def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._socket is not None

    async def read_input_register(
        self,
        doc_address: int,
        count: int = 1,
        scale: float = 1.0,
        signed: bool = False,
        data_type: str = "u16",
    ) -> float | int | str | None:
        """Read an input register (FC 04).

        Args:
            doc_address: The documented address (1-based from Sungrow docs)
            count: Number of registers to read
            scale: Scale factor to apply to the value
            signed: Whether the value is signed
            data_type: Data type (u16, s16, u32, s32, string)
        """
        return await self._read_register(
            FC_READ_INPUT_REGISTERS,
            doc_address,
            count,
            scale,
            signed,
            data_type,
        )

    async def read_holding_register(
        self,
        doc_address: int,
        count: int = 1,
        scale: float = 1.0,
        signed: bool = False,
        data_type: str = "u16",
    ) -> float | int | str | None:
        """Read a holding register (FC 03).

        Args:
            doc_address: The documented address (1-based from Sungrow docs)
            count: Number of registers to read
            scale: Scale factor to apply to the value
            signed: Whether the value is signed
            data_type: Data type (u16, s16, u32, s32, string)
        """
        return await self._read_register(
            FC_READ_HOLDING_REGISTERS,
            doc_address,
            count,
            scale,
            signed,
            data_type,
        )

    async def _read_register(
        self,
        function_code: int,
        doc_address: int,
        count: int,
        scale: float,
        signed: bool,
        data_type: str,
    ) -> float | int | str | None:
        """Read a Modbus register."""
        if not await self.is_connected():
            if not await self.connect():
                return None

        protocol_address = doc_address - 1

        async with self._lock:
            try:
                request = self._build_modbus_request(
                    function_code,
                    protocol_address,
                    count,
                )

                response = await self._send_request(request)

                if not response:
                    _LOGGER.warning("No response for register %d", doc_address)
                    return None

                parsed = self._parse_modbus_response(response)
                if not parsed:
                    return None

                return self._parse_register_data(
                    parsed["data"],
                    count,
                    scale,
                    signed,
                    data_type,
                )

            except Exception as err:
                _LOGGER.error("Error reading register %d: %s", doc_address, err)
                # Disconnect on error to force reconnect
                await self.disconnect()
                return None

    def _parse_register_data(
        self,
        data: bytes,
        count: int,
        scale: float,
        signed: bool,
        data_type: str,
    ) -> float | int | str | None:
        """Parse register data based on type."""
        if len(data) < count * 2:
            _LOGGER.warning(
                "Invalid data length: expected %d, got %d",
                count * 2,
                len(data),
            )
            return None

        try:
            if data_type == "string":
                return data.decode("utf-8", errors="ignore").strip("\x00").strip()

            if data_type in ("u32", "s32") or count == 2:
                high_word = struct.unpack(">H", data[0:2])[0]
                low_word = struct.unpack(">H", data[2:4])[0]
                raw_value = (high_word << 16) | low_word

                if signed or data_type == "s32":
                    if raw_value >= 0x80000000:
                        raw_value -= 0x100000000

            else:
                # 16-bit value
                if signed or data_type == "s16":
                    raw_value = struct.unpack(">h", data[0:2])[0]
                else:
                    raw_value = struct.unpack(">H", data[0:2])[0]

            return raw_value * scale

        except Exception as err:
            _LOGGER.error("Error parsing register data: %s", err)
            return None

    def _validate_value(self, key: str, value: float | int | str | None) -> bool:
        """Validate if a value is within expected limits.
        
        This is a soft validation - values outside limits are logged but still accepted
        unless they are truly impossible (like negative energy or extreme outliers).
        """
        if value is None:
            return False
        
        if isinstance(value, str):
            # String values are valid if not empty
            return len(value.strip()) > 0
        
        if isinstance(value, (int, float)):
            # Only reject truly impossible values
            # 0xFFFF (65535) or 0xFFFFFFFF often indicate read errors
            if value == 65535 or value == 4294967295:
                _LOGGER.debug(
                    "Rejecting likely error value for %s: %s (0xFFFF pattern)",
                    key,
                    value,
                )
                return False
            
            # Check against limits but only log, don't reject unless extreme
            if key in VALUE_LIMITS:
                min_val, max_val = VALUE_LIMITS[key]
                if not (min_val <= value <= max_val):
                    # Log as debug, not warning - these might be valid edge cases
                    _LOGGER.debug(
                        "Value outside expected range for %s: %s (expected %s to %s)",
                        key,
                        value,
                        min_val,
                        max_val,
                    )
                    # Only reject if extremely out of range (10x the limit)
                    if value < min_val * 10 - abs(max_val) * 10 or value > max_val * 10:
                        return False
        
        return True

    async def _read_register_with_retry(
        self,
        key: str,
        reg_config: dict,
        is_holding: bool = False,
    ) -> tuple[str, Any]:
        """Read a single register with retry logic."""
        read_func = self.read_holding_register if is_holding else self.read_input_register
        
        for attempt in range(self._retry_count):
            try:
                value = await read_func(
                    doc_address=reg_config["address"],
                    count=reg_config["count"],
                    scale=reg_config["scale"],
                    signed=reg_config.get("signed", False),
                    data_type=reg_config.get("type", "u16"),
                )
                
                # Validate the value
                if value is not None and self._validate_value(key, value):
                    return key, value
                
                # If invalid, try again after a short delay
                if attempt < self._retry_count - 1:
                    await asyncio.sleep(self._retry_delay * (attempt + 1))
                    
            except Exception as err:
                _LOGGER.debug(
                    "Attempt %d failed for %s: %s",
                    attempt + 1,
                    key,
                    err,
                )
                if attempt < self._retry_count - 1:
                    await asyncio.sleep(self._retry_delay * (attempt + 1))
        
        # All retries failed, return cached value if available
        if key in self._last_valid_data:
            _LOGGER.debug(
                "Using cached value for %s: %s",
                key,
                self._last_valid_data[key],
            )
            return key, self._last_valid_data[key]
        
        return key, None

    async def read_all_data(self) -> dict[str, Any]:
        """Read all configured registers and return data dictionary."""
        data: dict[str, Any] = {}
        errors = 0
        total_reads = 0

        # Read input registers
        for key, reg_config in MODBUS_REGISTERS.items():
            total_reads += 1
            result_key, value = await self._read_register_with_retry(key, reg_config, is_holding=False)

            if value is not None:
                # Special handling for running state
                if key == "running_state":
                    data[key] = RUNNING_STATES.get(
                        int(value), f"Unknown ({int(value)})"
                    )
                elif isinstance(value, float):
                    data[key] = round(value, 2)
                else:
                    data[key] = value
                
                # Cache valid values
                self._last_valid_data[key] = data[key]
            else:
                errors += 1
                # Use cached value if available
                if key in self._last_valid_data:
                    data[key] = self._last_valid_data[key]
                    _LOGGER.debug("Using cached value for %s", key)

        # Read holding registers for system clock
        clock_parts = {}
        for key, reg_config in MODBUS_HOLDING_REGISTERS.items():
            total_reads += 1
            result_key, value = await self._read_register_with_retry(key, reg_config, is_holding=True)
            
            if value is not None:
                clock_parts[key] = int(value)
            else:
                errors += 1

        if all(k in clock_parts for k in [
            "system_clock_year", "system_clock_month", "system_clock_day",
            "system_clock_hour", "system_clock_minute", "system_clock_second"
        ]):
            data["system_clock"] = (
                f"{clock_parts['system_clock_year']:04d}-"
                f"{clock_parts['system_clock_month']:02d}-"
                f"{clock_parts['system_clock_day']:02d} "
                f"{clock_parts['system_clock_hour']:02d}:"
                f"{clock_parts['system_clock_minute']:02d}:"
                f"{clock_parts['system_clock_second']:02d}"
            )

        # Track error rate - only log if significant portion of reads failed
        error_rate = errors / total_reads * 100 if total_reads > 0 else 0
        
        if error_rate > 50:
            # More than half of reads failed - this is a real problem
            self._consecutive_total_failures += 1
            _LOGGER.warning(
                "High error rate: %d/%d reads failed (%.1f%%), consecutive failures: %d",
                errors,
                total_reads,
                error_rate,
                self._consecutive_total_failures,
            )
            
            # Force reconnect only if most reads are failing consistently
            if self._consecutive_total_failures >= self._max_consecutive_failures:
                _LOGGER.warning(
                    "Too many consecutive high-error cycles (%d), forcing reconnect",
                    self._consecutive_total_failures,
                )
                await self.disconnect()
                self._consecutive_total_failures = 0
        elif error_rate > 0:
            # Some errors but not critical - just log at debug level
            _LOGGER.debug(
                "Read completed with %d/%d errors (%.1f%%)",
                errors,
                total_reads,
                error_rate,
            )
            # Reset failure counter if we're getting mostly good reads
            if error_rate < 25:
                self._consecutive_total_failures = 0
        else:
            # All reads successful
            self._consecutive_total_failures = 0
            self._last_successful_read = time.time()

        _LOGGER.debug("Read Modbus data: %s", data)
        return data

    async def test_connection(self) -> bool:
        """Test connection by reading serial number register."""
        try:
            if not await self.connect():
                return False

            # Read serial number as connection test (doc_addr 4990)
            value = await self.read_input_register(
                doc_address=4990,
                count=10,
                data_type="string",
            )
            if value:
                _LOGGER.info("Connected to inverter with serial: %s", value)
                return True
            return False

        except Exception as err:
            _LOGGER.error("Connection test failed: %s", err)
            return False
