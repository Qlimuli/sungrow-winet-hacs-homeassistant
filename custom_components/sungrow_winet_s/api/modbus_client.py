"""Modbus TCP client for Sungrow inverters via WINET-S."""
import asyncio
import logging
from typing import Any, Optional

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder

from ..const import (
    DEFAULT_TIMEOUT,
    INVERTER_STATUS,
    MODBUS_REGISTERS,
)

_LOGGER = logging.getLogger(__name__)


class SungrowModbusClient:
    """Client for Modbus TCP communication with Sungrow inverter."""

    def __init__(
        self,
        host: str,
        port: int = 502,
        slave_id: int = 1,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize the Modbus client.
        
        Args:
            host: IP address or hostname of the WINET-S device
            port: Modbus TCP port (default: 502)
            slave_id: Modbus slave ID of the inverter (default: 1)
            timeout: Connection timeout in seconds
        """
        self.host = host
        self.port = port
        self.slave_id = slave_id
        self.timeout = timeout
        self._client: Optional[AsyncModbusTcpClient] = None
        self._lock = asyncio.Lock()

    async def connect(self) -> bool:
        """Connect to the Modbus device.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self._client = AsyncModbusTcpClient(
                host=self.host,
                port=self.port,
                timeout=self.timeout,
            )
            await self._client.connect()
            if self._client.connected:
                _LOGGER.info("Connected to Sungrow inverter via Modbus at %s:%s", self.host, self.port)
                return True
            _LOGGER.error("Failed to connect to Modbus at %s:%s", self.host, self.port)
            return False
        except Exception as err:
            _LOGGER.error("Error connecting to Modbus: %s", err)
            return False

    async def disconnect(self) -> None:
        """Disconnect from the Modbus device."""
        if self._client:
            self._client.close()
            self._client = None
            _LOGGER.info("Disconnected from Modbus")

    async def read_register(
        self,
        register: int,
        count: int = 1,
        scale: float = 1.0,
        signed: bool = False,
    ) -> Optional[float]:
        """Read a Modbus register and return scaled value.
        
        Args:
            register: Starting register address
            count: Number of registers to read (1 or 2)
            scale: Scale factor to apply to raw value
            signed: Whether the value is signed
            
        Returns:
            Scaled register value or None if read failed
        """
        async with self._lock:
            try:
                if not self._client or not self._client.connected:
                    if not await self.connect():
                        return None

                result = await self._client.read_input_registers(
                    address=register,
                    count=count,
                    slave=self.slave_id,
                )

                if result.isError():
                    _LOGGER.error("Error reading register %s: %s", register, result)
                    return None

                # Decode based on count
                if count == 1:
                    value = result.registers[0]
                    if signed and value > 32767:
                        value -= 65536
                elif count == 2:
                    # 32-bit value (big-endian)
                    decoder = BinaryPayloadDecoder.fromRegisters(
                        result.registers,
                        byteorder=Endian.BIG,
                        wordorder=Endian.BIG,
                    )
                    if signed:
                        value = decoder.decode_32bit_int()
                    else:
                        value = decoder.decode_32bit_uint()
                else:
                    _LOGGER.error("Unsupported register count: %s", count)
                    return None

                # Apply scale
                return value * scale

            except Exception as err:
                _LOGGER.error("Exception reading register %s: %s", register, err)
                return None

    async def read_all_data(self) -> dict[str, Any]:
        """Read all configured registers and return data dictionary.
        
        Returns:
            Dictionary with sensor keys and values
        """
        data = {}
        
        for sensor_key, (register, count, scale, signed) in MODBUS_REGISTERS.items():
            value = await self.read_register(register, count, scale, signed)
            
            if value is not None:
                # Special handling for inverter status
                if sensor_key == "inverter_status":
                    status_code = int(value)
                    data[sensor_key] = INVERTER_STATUS.get(status_code, f"Unknown ({status_code})")
                else:
                    data[sensor_key] = round(value, 2)
            else:
                data[sensor_key] = None
                
        return data

    async def test_connection(self) -> bool:
        """Test if connection to inverter is working.
        
        Returns:
            True if connection test successful
        """
        try:
            # Try to read a basic register (inverter status)
            value = await self.read_register(
                MODBUS_REGISTERS["inverter_status"][0],
                count=1,
            )
            return value is not None
        except Exception as err:
            _LOGGER.error("Connection test failed: %s", err)
            return False
