# pylint: disable=line-too-long
"""
NMEA Protocol core globals and constants

Created on 4 Mar 2021

While the NMEA 0183 © protocol is proprietary, the information here
has been collated from public domain sources.

:author: semuadmin
"""
from collections import OrderedDict

NMEA_HDR = [b"\x24\x47", b"\x24\x50"]  # standard, proprietary
INPUT = 1
OUTPUT = 0
GET = 0
SET = 1
POLL = 2
VALNONE = 0
VALCKSUM = 1
VALMSGID = 2

GNSSLIST = OrderedDict({
    0: "GPS",
    1: "SBAS",
    2: "Galileo",
    3: "BeiDou",
    4: "IMES",
    5: "QZSS",
    6: "GLONASS",
})

# ***************************************************
# THESE ARE THE NMEA PROTOCOL PAYLOAD ATTRIBUTE TYPES
# ***************************************************
CH = "CH"  # Character
DE = "DE"  # Decimal
DT = "DT"  # Date ddmmyy
HX = "HX"  # Hexadecimal Integer
IN = "IN"  # Integer
LA = "LA"  # Latitude value ddmm.mmmmm
LN = "LN"  # Longitude value dddmm.mmmmm
ST = "ST"  # String
TM = "TM"  # Time hhmmss.ss

VALID_TYPES = (CH, DE, DT, HX, IN, LA, LN, ST, TM)

# *****************************************
# THESE ARE THE NMEA V4 PROTOCOL TALKER IDS
# *****************************************
NMEA_TALKERS = OrderedDict({
    # ***************************************************************
    # Navigation System Satellite Receivers:
    # ***************************************************************
    "GA": "Galileo Positioning System",
    "GB": "BDS (BeiDou System) ",
    "GI": "NavIC (IRNSS)",
    "GL": "GLONASS Receiver",
    "GN": "Global Navigation Satellite System (GNSS)",
    "GP": "Global Positioning System (GPS)",
    "GQ": "QZSS",
    "P": "Proprietary",
})

# ****************************************************************************
# THESE ARE THE NMEA PROTOCOL CORE MESSAGE IDENTITIES
# Payloads for each of these identities are defined in the nmeatypes_* modules
# ****************************************************************************
NMEA_MSGIDS = OrderedDict({
    # ***************************************************************
    # NMEA Standard message types
    # ***************************************************************
    "DTM": "Datum Reference",
    "GAQ": "Poll Standard Message - Talker ID GA (Galileo)",
    "GBQ": "Poll Standard Message - Talker ID GB (BeiDou)",
    "GBS": "GNSS Satellite Fault Detection",
    "GGA": "Global positioning system fix data",
    "GLL": "Latitude and longitude, with time of position fix and status",
    "GLQ": "Poll Standard Message - Talker ID GL (GLONASS)",
    "GNQ": "Poll Standard Message - Talker ID GN (Any GNSS)",
    "GNS": "GNSS Fix Data",
    "GPQ": "Poll Standard Message - Talker ID GP (GPS, SBAS)",
    "GRS": "GNSS Range Residuals",
    "GSA": "GNSS DOP and Active Satellites",
    "GST": "GNSS Pseudo Range Error Statistics",
    "GSV": "GNSS Satellites in View",
    "RMC": "Recommended Minimum data",
    "TXT": "Text Transmission",
    "VLW": "Dual Ground Water Distance",
    "VTG": "Course over ground and Groundspeed",
    "ZDA": "Time and Date",
})
NMEA_MSGIDS_PROP = OrderedDict({
    # ***************************************************************
    # NMEA Proprietary message types
    # ***************************************************************
    # ***************************************************************
    # U-BLOX Proprietary message types
    # ***************************************************************
    "UBX00": "PUBX-POSITION Lat/Long Position Data",
    "UBX03": "PUBX-SVSTATUS Satellite Status",
    "UBX04": "PUBX-TIME Time of Day and Clock Information",
    "UBX05": "Lat/Long Position Data",
    "UBX06": "Lat/Long Position Data",
    "UBX40": "Set NMEA message output rate",
    "UBX41": "PUBX-CONFIG Set Protocols and Baudrate",
    # ***************************************************************
    # Dummy message for testing only
    # ***************************************************************
    "FOO": "Dummy message",
})
