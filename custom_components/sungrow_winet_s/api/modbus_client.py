"""Modbus TCP client for Sungrow inverters."""
from __future__ import annotations

import asyncio
import logging
import struct
from typing import Any

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

from ..const import MODBUS_REGISTERS, RUNNING_STATES

_LOGGER = logging.getLogger(__name__)


class SungrowModbusClient:
    """Client for communicating with Sungrow inverter via Modbus TCP."""

    def __init__(self, host: str, port: int = 502, slave_id: int = 1) -> None:
        """Initialize the Modbus client."""
        self._host = host
        self._port = port
        self._slave_id = slave_id
        self._client: AsyncModbusTcpClient | None = None
        self._lock = asyncio.Lock()

    async def connect(self) -> bool:
        """Establish connection to the inverter."""
        try:
            self._client = AsyncModbusTcpClient(
                host=self._host,
                port=self._port,
                timeout=10,
            )
            connected = await self._client.connect()
            if connected:
                _LOGGER.info("Connected to Sungrow inverter at %s:%s", self._host, self._port)
            return connected
        except Exception as err:
            _LOGGER.error("Failed to connect to Modbus: %s", err)
            return False

    async def disconnect(self) -> None:
        """Disconnect from the inverter."""
        if self._client:
            self._client.close()
            self._client = None
            _LOGGER.info("Disconnected from Sungrow inverter")

    async def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._client is not None and self._client.connected

    async def read_register(
        self,
        address: int,
        count: int = 1,
        scale: float = 1.0,
        signed: bool = False,
    ) -> float | int | None:
        """Read a Modbus register and return scaled value."""
        if not self._client or not await self.is_connected():
            await self.connect()

        if not self._client:
            return None

        async with self._lock:
            try:
                result = await self._client.read_input_registers(
                    address=address,
                    count=count,
                    slave=self._slave_id,
                )

                if result.isError():
                    _LOGGER.warning("Modbus error reading register %s: %s", address, result)
                    return None

                # Combine registers for 32-bit values
                if count == 2:
                    raw_value = (result.registers[0] << 16) | result.registers[1]
                    if signed and raw_value >= 0x80000000:
                        raw_value -= 0x100000000
                else:
                    raw_value = result.registers[0]
                    if signed and raw_value >= 0x8000:
                        raw_value -= 0x10000

                return raw_value * scale

            except ModbusException as err:
                _LOGGER.error("Modbus exception reading register %s: %s", address, err)
                return None
            except Exception as err:
                _LOGGER.error("Error reading register %s: %s", address, err)
                return None

    async def read_all_data(self) -> dict[str, Any]:
        """Read all configured registers and return data dictionary."""
        data: dict[str, Any] = {}

        for key, reg_config in MODBUS_REGISTERS.items():
            value = await self.read_register(
                address=reg_config["address"],
                count=reg_config["count"],
                scale=reg_config["scale"],
                signed=reg_config.get("signed", False),
            )

            if value is not None:
                # Special handling for running state
                if key == "running_state":
                    data[key] = RUNNING_STATES.get(int(value), f"Unknown ({int(value)})")
                else:
                    data[key] = round(value, 2) if isinstance(value, float) else value

        _LOGGER.debug("Read Modbus data: %s", data)
        return data

    async def test_connection(self) -> bool:
        """Test connection by reading a known register."""
        try:
            if not await self.connect():
                return False

            # Try to read PV power register as connection test
            value = await self.read_register(
                address=MODBUS_REGISTERS["pv_power"]["address"],
                count=MODBUS_REGISTERS["pv_power"]["count"],
            )
            return value is not None
        except Exception as err:
            _LOGGER.error("Connection test failed: %s", err)
            return False
