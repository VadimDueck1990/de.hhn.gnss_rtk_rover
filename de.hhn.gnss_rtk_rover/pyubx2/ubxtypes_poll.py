"""
UBX Protocol Polling payload definitions
THESE ARE THE PAYLOAD DEFINITIONS FOR _POLL_ MESSAGES _TO_ THE RECEIVER
(e.g. query configuration; request monitoring, receiver management, logging or sensor fusion status)
Response payloads are defined in UBX_PAYLOADS_GET
Created on 27 Sep 2020
:author: semuadmin
"""
from pyubx2.ubxtypes_core import U1, U2, U4
from collections import OrderedDict

UBX_PAYLOADS_POLL = {
    "CFG-MSG": {"msgClass": U1, "msgID": U1},
    "CFG-NMEA": {},
    "CFG-RATE": {},
    "CFG-VALGET": OrderedDict({
        "version": U1,
        "layer": U1,
        "position": U2,
        "group": ("None", {"keys": U4}),  # repeating group
    }),
    "NAV-PVT": {},
    "NAV-SAT": {},
    "NAV-SIG": {},
    "NAV-STATUS": {},
    "NAV-SVIN": {},
    "UPD-SOS": {},
}
