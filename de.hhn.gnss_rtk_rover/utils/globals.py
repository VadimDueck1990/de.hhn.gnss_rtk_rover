"""
Global variables for gnss rtk rover.

Created on 27 Oct 2022

:author: vdueck
"""
from utils import logging

# UART
UART1_TX = 0
UART1_RX = 1

# WiFi
# WIFI_SSID = "WLAN-L45XAB"
# WIFI_PW = "7334424916822832"
WIFI_SSID = "huawei_p30_lite"
WIFI_PW = "99999999"
WIFI_CHECK_TIME = 5

# NTRIP
OUTPORT = 50010
MIN_NMEA_PAYLOAD = 3  # minimum viable length of NMEA message payload
EARTH_RADIUS = 6371  # km
DEFAULT_BUFSIZE = 4096  # buffer size for NTRIP client
MAXPORT = 65535  # max valid TCP port
FORMAT_PARSED = 1
FORMAT_BINARY = 2
FORMAT_HEX = 4
FORMAT_HEXTABLE = 8
FORMAT_PARSEDSTRING = 16
FORMAT_JSON = 32
VERBOSITY_LOW = 0
VERBOSITY_MEDIUM = 1
VERBOSITY_HIGH = 2
DISCONNECTED = 0
CONNECTED = 1
LOGLIMIT = 1000  # max lines in logfile
NOGGA = -1

NTRIP_USER = "HHN1"
NTRIP_PW = "sap21hhN"
NTRIP_SERVER = "sapos-ntrip.rlp.de"
OUTPORT_NTRIP = 2101
MOUNTPOINT = "VRS_3_2G_RP"
GGA_INTERVAL = 10
REF_LAT = "50.390281"
REF_LON = "7.3161025"
REF_ALT = "269.7"


GNSSLIST = {
    0: "GPS",
    1: "SBAS",
    2: "Galileo",
    3: "BeiDou",
    4: "IMES",
    5: "QZSS",
    6: "GLONASS",
}
