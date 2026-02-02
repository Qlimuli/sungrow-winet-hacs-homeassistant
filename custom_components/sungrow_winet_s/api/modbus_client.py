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

# Validation limits for sensor values
VALUE_LIMITS: dict[str, tuple[float, float]] = {
    # Temperature limits (in °C)
    "inverter_temp": (-40, 100),
    # Voltage limits (in V)
    "mppt1_voltage": (0, 1500),
    "mppt2_voltage": (0, 1500),
    "mppt3_voltage": (0, 1500),
    "mppt4_voltage": (0, 1500),
    "grid_voltage_a": (0, 500),
    "grid_voltage_b": (0, 500),
    "grid_voltage_c": (0, 500),
    # Current limits (in A)
    "mppt1_current": (0, 50),
    "mppt2_current": (0, 50),
    "mppt3_current": (0, 50),
    "mppt4_current": (0, 50),
    "battery_current": (-200, 200),
    # Power limits (in W)
    "total_dc_power": (0, 100000),
    "battery_power": (-50000, 50000),
    "meter_power_phase_a": (-50000, 50000),
    "meter_power_phase_b": (-50000, 50000),
    "meter_power_phase_c": (-50000, 50000),
    # Frequency limits (in Hz)
    "grid_frequency": (45, 65),
    "grid_frequency_high_precision": (45, 65),
    # Power factor
    "power_factor": (-1.1, 1.1),
    # Energy limits (in kWh)
    "daily_pv_energy": (0, 500),
    "total_pv_energy": (0, 10000000),
    # Nominal power (in kW)
    "nominal_power": (0, 500),
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
        self._retry_count = 3
        self._retry_delay = 1.0
        self._last_valid_data: dict[str, Any] = {}
        self._last_successful_read: float = 0
        self._consecutive_errors = 0
        self._max_consecutive_errors = 5

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
        """Validate if a value is within expected limits."""
        if value is None:
            return False
        
        if isinstance(value, str):
            # String values are valid if not empty
            return len(value.strip()) > 0
        
        if key in VALUE_LIMITS:
            min_val, max_val = VALUE_LIMITS[key]
            if not (min_val <= value <= max_val):
                _LOGGER.warning(
                    "Value out of range for %s: %s (expected %s to %s)",
                    key,
                    value,
                    min_val,
                    max_val,
                )
                return False
        
        # Check for common invalid values (0xFFFF often indicates error)
        if isinstance(value, (int, float)):
            # Very large numbers often indicate read errors
            if abs(value) > 1e9:
                _LOGGER.warning(
                    "Suspiciously large value for %s: %s",
                    key,
                    value,
                )
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

        # Track error rate
        if errors > 0:
            self._consecutive_errors += 1
            error_rate = errors / total_reads * 100
            _LOGGER.warning(
                "Read completed with %d/%d errors (%.1f%%), consecutive error cycles: %d",
                errors,
                total_reads,
                error_rate,
                self._consecutive_errors,
            )
            
            # Force reconnect if too many consecutive errors
            if self._consecutive_errors >= self._max_consecutive_errors:
                _LOGGER.warning(
                    "Too many consecutive error cycles (%d), forcing reconnect",
                    self._consecutive_errors,
                )
                await self.disconnect()
                self._consecutive_errors = 0
        else:
            self._consecutive_errors = 0
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
