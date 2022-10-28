"""
UBX Protocol Polling payload definitions

THESE ARE THE PAYLOAD DEFINITIONS FOR _POLL_ MESSAGES _TO_ THE RECEIVER
(e.g. query configuration; request monitoring, receiver management, logging or sensor fusion status)
Response payloads are defined in UBX_PAYLOADS_GET

NB: Attribute names must be unique within each message class/id

Created on 27 Sep 2020

Information sourced from u-blox Interface Specifications © 2013-2021, u-blox AG

:author: semuadmin
"""

from pyubx2.ubxtypes_core import U1, U2, U4

UBX_PAYLOADS_POLL = {
    # *************************************************
    "CFG-ANT": {},
    "CFG-DAT": {},
    "CFG-DGNSS": {},
    "CFG-GEOFENCE": {},
    "CFG-GNSS": {},
    "CFG-INF": {"protocolID": U1},
    "CFG-ITFM": {},
    "CFG-LOGFILTER": {},
    "CFG-MSG": {"msgClass": U1, "msgID": U1},
    "CFG-NAV5": {},
    "CFG-NAVX5": {},
    "CFG-NMEA": {},
    "CFG-ODO": {},
    "CFG-PRT": {"portID": U1},
    "CFG-PWR": {},
    "CFG-RATE": {},
    "CFG-RINV": {},
    "CFG-TMODE3": {},
    "CFG-TP5": {},  # used if no payload keyword specified
    "CFG-USB": {},
    "CFG-VALGET": {
        "version": U1,
        "layer": U1,
        "position": U2,
        "group": ("None", {"keys": U4}),  # repeating group
    },
    # *************************************************
    "LOG-INFO": {},
    # *************************************************
    "MGA-DBD": {},
    # *************************************************
    "MON-COMMS": {},
    "MON-GNSS": {},
    "MON-HW": {},
    "MON-HW2": {},
    "MON-HW3": {},
    "MON-IO": {},
    "MON-MSGPP": {},
    "MON-PATCH": {},
    "MON-RF": {},
    "MON-RXBUF": {},
    "MON-TXBUF": {},
    "MON-VER": {},
    # *************************************************
    "NAV-CLOCK": {},
    "NAV-DOP": {},
    "NAV-EOE": {},
    "NAV-GEOFENCE": {},
    "NAV-HPPOSECEF": {},
    "NAV-HPPOSLLH": {},
    "NAV-ODO": {},
    "NAV-ORB": {},
    "NAV-PL": {},
    "NAV-POSECEF": {},
    "NAV-POSLLH": {},
    "NAV-PVT": {},
    "NAV-RELPOSNED": {},
    "NAV-RESETODO": {},
    "NAV-SAT": {},
    "NAV-SIG": {},
    "NAV-STATUS": {},
    "NAV-SVIN": {},
    "NAV-TIMEBDS": {},
    "NAV-TIMEGAL": {},
    "NAV-TIMEGLO": {},
    "NAV-TIMEGPS": {},
    "NAV-TIMELS": {},
    "NAV-TIMEUTC": {},
    "NAV-VELECEF": {},
    "NAV-VELNED": {},
    # *************************************************
    "RXM-MEASX": {},
    "RXM-RAWX": {},
    "RXM-RLM": {},
    "RXM-RTCM": {},
    "RXM-SFRBX": {},
    # *************************************************
    "SEC-UNIQID": {},
    # *************************************************
    "TIM-TM2": {},
    "TIM-TP": {},
    "TIM-VRFY": {},
    # *************************************************
    "UPD-SOS": {},
}
