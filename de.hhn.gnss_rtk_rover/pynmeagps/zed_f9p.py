import machine
import ustruct
import uasyncio as asyncio
from micropython import const

_ADRESS = const(0x42) # ZED-F9P I2C Address
_PAUSE_MS = const(60)  # ZED-F9P acquisition delay
_READ_USER_REG = const(0xE7)