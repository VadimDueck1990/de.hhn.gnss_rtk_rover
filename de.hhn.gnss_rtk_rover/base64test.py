import micropython
import gc
print("imported micropython, gc")
micropython.mem_info()
gc.mem_free()
gc.mem_alloc()

import time
print("imported time")
micropython.mem_info()
gc.mem_free()
gc.mem_alloc()

import binascii
print("imported binascii")
micropython.mem_info()
gc.mem_free()
gc.mem_alloc()

import uasyncio
print("imported uasyncio")
micropython.mem_info()
gc.mem_free()
gc.mem_alloc()

from uasyncio import Event
print("from uasyncio import Event")
micropython.mem_info()
gc.mem_free()
gc.mem_alloc()

from machine import UART
print("from machine import UART")
micropython.mem_info()
gc.mem_free()
gc.mem_alloc()

from primitives.queue import Queue
print("from primitives.queue import Queue")
micropython.mem_info()
gc.mem_free()
gc.mem_alloc()

import socket
print("import socket")
micropython.mem_info()
gc.mem_free()
gc.mem_alloc()

# from pyubx2.ubxreader import UBXReader
# print("from pyubx2.ubxreader import UBXReader")
# micropython.mem_info()
# gc.mem_free()
# gc.mem_alloc()

from pyubx2.ubxtypes_core import RTCM3_PROTOCOL, ERR_IGNORE
print("from pyubx2.ubxtypes_core import RTCM3_PROTOCOL, ERR_IGNORE")
micropython.mem_info()
gc.mem_free()
gc.mem_alloc()

from pyrtcm.exceptions import (
    RTCMParseError,
    RTCMMessageError,
    RTCMTypeError,
)
print("from pyrtcm import (RTCMParseError etc)")
micropython.mem_info()
gc.mem_free()
gc.mem_alloc()

from pynmeagps import NMEAMessage, GET
print("from pynmeagps import NMEAMessage, GET")
micropython.mem_info()
gc.mem_free()
gc.mem_alloc()

import utils.logging as logging
print("import utils.logging as logging")
micropython.mem_info()
gc.mem_free()
gc.mem_alloc()

from utils.globals import (
    DEFAULT_BUFSIZE,
    NOGGA,
    OUTPORT_NTRIP,
    NTRIP_USER,
    NTRIP_PW,
    NTRIP_SERVER,
    MOUNTPOINT,
    GGA_INTERVAL,
    REF_LAT,
    REF_LON,
    REF_ALT,
)
print("from utils.globals import ...")
micropython.mem_info()
gc.mem_free()
gc.mem_alloc()

from gnss._version import __version__ as VERSION
print("from gnss._version import __version__ as VERSION")
micropython.mem_info()
gc.mem_free()
gc.mem_alloc()

from gnss.helpers import find_mp_distance
print("from gnss.helpers import find_mp_distance")
micropython.mem_info()
gc.mem_free()
gc.mem_alloc()
print("finished")
