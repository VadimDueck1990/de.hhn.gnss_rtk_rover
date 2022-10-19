"""
NMEA Protocol Output payload definitions

THESE ARE THE PAYLOAD DEFINITIONS FOR _GET_ MESSAGES _FROM_ THE RECEIVER
(e.g. Periodic Navigation Data; Poll Responses; Info messages).

NB: Attribute names must be unique within each message id.
NB: Avoid reserved names 'msgID', 'talker', 'payload', 'checksum'.

NB: Repeating groups must be defined as a tuple thus
    'group': ('numr', {dict})
    where
    - 'numr' is either:
       a) an integer representing a fixed number of repeats e.g 32
       b) a string representing the name of a preceding attribute
          containing the number of repeats e.g. 'numCh'
       c) 'None' for an indeterminate repeating group
          (only one such group is permitted per message type)
    - {dict} is the nested dictionary containing the repeating
      attributes

Created on 4 Mar Sep 2021

While the NMEA 0183 © protocol is proprietary, the information here
has been collated from public domain sources.

:author: semuadmin
"""

from collections import OrderedDict
from pynmeagps.nmeatypes_core import (
    CH,
    DE,
    DT,
    HX,
    IN,
    LA,
    LN,
    ST,
    TM,
)

NMEA_PAYLOADS_GET = OrderedDict({
    # *********************************************
    # STANDARD MESSAGES
    # *********************************************
    "AAM": OrderedDict({
        "arrce": CH,
        "perp": CH,
        "crad": DE,
        "cUnit": CH,
        "wpt": ST,
    }),
    "APA": OrderedDict({
        "LCgwarn": CH,
        "LCcwarn": CH,
        "ctrkerr": DE,
        "dirs": CH,
        "ctrkUnit": CH,
        "aalmcirc": CH,
        "aalmperp": CH,
        "bearP2D": DE,
        "bearP2Du": CH,
        "wpt": ST,
    }),
    "APB": OrderedDict({
        "LCgwarn": CH,
        "LCcwarn": CH,
        "ctrkerr": DE,
        "dirs": CH,
        "ctrkUnit": CH,
        "aalmcirc": CH,
        "aalmperp": CH,
        "bearO2D": DE,
        "bearO2Du": CH,
        "wpt": ST,
        "bearD": DE,
        "bearDu": CH,
        "bearS": DE,
        "bearSu": CH,
    }),
    "BOD": OrderedDict({
        "bearT": DE,
        "bearTu": CH,
        "bearM": DE,
        "bearMu": CH,
        "wptD": ST,
        "wptO": ST,
    }),
    "BWC": OrderedDict({
        "fixutc": ST,
        "lat": LA,
        "NS": CH,
        "lon": LN,
        "EW": CH,
        "bearT": DE,
        "bearTu": CH,
        "bearM": DE,
        "bearMu": CH,
        "dist": DE,
        "distUnit": CH,
        "wpt": ST,
    }),
    "DTM": OrderedDict({
        "datum": ST,
        "subDatum": ST,
        "latOfset": DE,
        "NS": CH,
        "lonOfset": DE,
        "EW": CH,
        "alt": DE,
        "refDatum": ST,
    }),
    "GBS": OrderedDict({
        "time": TM,
        "errLat": DE,
        "errLon": DE,
        "errAlt": DE,
        "svid": IN,
        "prob": DE,
        "bias": DE,
        "stddev": DE,
        "systemId": HX,  # NMEA >=4.10 only
        "signalId": HX,  # NMEA >=4.10 only
    }),
    "GGA": OrderedDict({
        "time": TM,
        "lat": LA,
        "NS": CH,
        "lon": LN,
        "EW": CH,
        "quality": IN,
        "numSV": IN,
        "HDOP": DE,
        "alt": DE,  # altitude above sea level in m
        "altUnit": CH,
        "sep": DE,
        "sepUnit": CH,
        "diffAge": DE,
        "diffStation": IN,
    }),
    "GLL": OrderedDict({
        "lat": LA,
        "NS": CH,
        "lon": LN,
        "EW": CH,
        "time": TM,
        "status": ST,
        "posMode": ST,
    }),
    "GNS": OrderedDict({
        "time": TM,
        "lat": LA,
        "NS": CH,
        "lon": LN,
        "EW": CH,
        "posMode": ST,
        "numSV": IN,
        "HDOP": DE,
        "alt": DE,
        "sep": DE,
        "diffAge": DE,
        "diffStation": IN,
        "navStatus": CH,  # NMEA >=4.10 only
    }),
    "GRS": OrderedDict({
        "time": TM,
        "mode": IN,
        "groupSV": (
            12,
            {  # repeating group * 12
                "residual": DE,
            },
        ),
        "systemId": HX,  # NMEA >=4.10 only
        "signalId": HX,  # NMEA >=4.10 only
    }),
    "GSA": OrderedDict({
        "opMode": CH,
        "navMode": IN,
        "groupSV": (
            12,
            OrderedDict({  # repeating group * 12
                "svid": IN,
            }),
        ),
        "PDOP": DE,
        "HDOP": DE,
        "VDOP": DE,
        "systemId": HX,  # NMEA >=4.10 only
    }),
    "GST": OrderedDict({
        "time": TM,
        "rangeRms": DE,
        "stdMajor": DE,
        "stdMinor": DE,
        "orient": DE,
        "stdLat": DE,
        "stdLong": DE,
        "stdAlt": DE,
    }),
    "GSV": OrderedDict([
        ("numMsg", IN),
        ("msgNum", IN),
        ("numSV", IN),
        ("group_sv", (
            "None",
            OrderedDict([  # repeating group * 1..4
                ("svid", IN),
                ("elv", DE),  # elevation
                ("az", IN),  # azimuth
                ("cno", IN)  # signal strength
            ])
        )),
        ("signalID", HX)  # NMEA >=4.10 only
    ]),
    "HDG": OrderedDict({
        "heading": DE,
        "MT": CH,  # 'M'
    }),
    "HDM": OrderedDict({
        "heading": DE,
        "devm": DE,
        "devEW": CH,
        "varm": DE,
        "varEW": CH,
    }),
    "HDT": OrderedDict({
        "heading": DE,
        "MT": CH,  # 'T'
    }),
    "MSK": OrderedDict({
        "freq": DE,
        "fmode": CH,
        "beacbps": IN,
        "bpsmode": CH,
        "MMSfreq": DE,
    }),
    "MSS": OrderedDict({
        "strength": IN,
        "snr": IN,
        "freq": DE,
        "beacbps": IN,
    }),
    "RLM": OrderedDict({
        "beacon": HX,
        "time": TM,
        "code": CH,
        "body": HX,
    }),
    "RMA": OrderedDict({
        "status": CH,
        "lat": LA,
        "NS": CH,
        "lon": LN,
        "EW": CH,
        "reserved1": ST,
        "reserved2": ST,
        "sog": DE,
        "cog": DE,
        "var": DE,
        "dirvar": CH,
    }),
    "RMB": OrderedDict({
        "status": CH,
        "ctrkerr": DE,
        "dirs": CH,
        "wptO": CH,
        "wptD": CH,
        "lat": LA,  # of wptD
        "NS": CH,
        "lon": LN,  # of wptD
        "EW": CH,
        "range": DE,
        "bearing": DE,
        "velclos": DE,
        "arrstatus": CH,
        "valstatus": CH,
    }),
    "RMC": OrderedDict({
        "time": TM,
        "status": CH,
        "lat": LA,
        "NS": CH,
        "lon": LN,
        "EW": CH,
        "spd": DE,  # speed in knots
        "cog": DE,  # course over ground
        "date": DT,
        "mv": DE,
        "mvEW": ST,
        "posMode": CH,
        "navStatus": CH,  # NMEA >=4.10 only
    }),
    "RTE": OrderedDict({
        "numMsg": IN,
        "msgNum": IN,
        "status": CH,  # 'c'/'w'
        "active": ST,
        "group_wp": (
            "None",
            {  # repeating group
                "wpt": ST,
            },
        ),
    }),
    "STN": OrderedDict({
        "talkerId": ST,
    }),
    "THS": OrderedDict({
        "headt": DE,
        "mi": CH,
    }),
    "TRF": OrderedDict({
        "time": TM,
        "date": DT,
        "lat": LA,
        "NS": CH,
        "lon": LN,
        "EW": CH,
        "elangle": DE,
        "iter": DE,
        "Dopint": DE,
        "dist": DE,
        "svid": IN,
    }),
    "TXT": OrderedDict({
        "numMsg": IN,
        "msgNum": IN,
        "msgType": IN,
        "text": ST,
    }),
    "VBW": OrderedDict({
        "wlspd": DE,
        "wtspd": DE,
        "wstatus": CH,
        "glspd": DE,
        "gtspd": DE,
        "gstatus": CH,
    }),
    "VLW": OrderedDict({
        "twd": DE,
        "twdUnit": CH,
        "wd": DE,
        "wdUnit": CH,
        "tgd": DE,  # NMEA >=4.00 only
        "tgdUnit": CH,  # NMEA >=4.00 only
        "gd": DE,  # NMEA >=4.00 only
        "gdUnit": CH,  # NMEA >=4.00 only
    }),
    "VTG": OrderedDict({
        "cogt": DE,  # course over ground (true)
        "cogtUnit": CH,
        "cogm": DE,  # course over ground (magnetic)
        "cogmUnit": CH,
        "sogn": DE,  # speed over ground knots
        "sognUnit": CH,
        "sogk": DE,  # speed over ground kmph
        "sogkUnit": CH,
        "posMode": CH,  # NMEA >=2.3 only
    }),
    "WPL": OrderedDict({
        "lat": LA,
        "NS": CH,
        "lon": LN,
        "EW": CH,
        "wpt": ST,
    }),
    "XTE": OrderedDict({
        "gwarn": CH,
        "LCcwarn": CH,
        "ctrkerr": DE,
        "dirs": CH,
        "disUnit": CH,
    }),
    "ZDA": OrderedDict({
        "time": TM,
        "day": IN,
        "month": IN,
        "year": IN,
        "ltzh": ST,
        "ltzn": ST,
    }),
    # *********************************************
    # GARMIN PROPRIETARY MESSAGES
    # *********************************************
    "GRME": OrderedDict({  # estimated error information
        "HPE": DE,
        "HPEUnit": CH,
        "VPE": DE,
        "VPEUnit": CH,
        "EPE": DE,
        "EPEUnit": CH,
    }),
    "GRMF": OrderedDict({  # GPS fix data sentence
        "week": IN,
        "secs": IN,
        "date": DT,
        "time": TM,
        "leapsec": IN,
        "lat": LA,
        "NS": CH,
        "lon": LN,
        "EW": CH,
        "mode": CH,
        "fix": IN,
        "spd": DE,
        "course": IN,
        "PDOP": DE,
        "TDOP": DE,
    }),
    "GRMH": OrderedDict({  # aviation height and VNAV data
        "status": CH,
        "vspd": DE,
        "verr": DE,
        "spdtgt": DE,
        "spdwpt": DE,
        "height": DE,
        "trk": DE,
        "course": DE,
    }),
    "GRMM": OrderedDict({  # map datum
        "dtm": ST,
    }),
    "GRMT": OrderedDict({  # sensor status information
        "ver": ST,
        "ROMtest": CH,
        "rcvrtest": CH,
        "stortest": CH,
        "rtctest": CH,
        "osctest": CH,
        "datatest": CH,
        "temp": DE,
        "cfgdata": CH,
    }),
    "GRMV": OrderedDict({  # 3D velocity information
        "velE": DE,
        "velN": DE,
        "velZ": DE,
    }),
    "GRMZ": OrderedDict({  # altitude
        "alt": DE,
        "altUnit": CH,
        "fix": IN,
    }),
    "GRMB": OrderedDict({  # DGPS Beacon information
        "freq": DE,
        "bps": IN,
        "snr": IN,
        "quality": IN,
        "dist": DE,
        "status": IN,
        "fixsrc": CH,
        "mode": CH,
    }),
    # *********************************************
    # U-BLOX PROPRIETARY MESSAGES
    # *********************************************
    "UBX00": OrderedDict({
        "msgId": ST,  # '00'
        "time": TM,
        "lat": LA,
        "NS": CH,
        "lon": LN,
        "EW": CH,
        "altRef": DE,
        "navStat": ST,
        "hAcc": DE,
        "vAcc": DE,
        "SOG": DE,
        "COG": DE,
        "vVel": DE,
        "diffAge": DE,
        "HDOP": DE,
        "VDOP": DE,
        "PDOP": DE,
        "numSVs": IN,
        "reserved": IN,
        "DR": IN,
    }),
    "UBX03": OrderedDict({
        "msgId": ST,  # '03'
        "numSv": IN,
        "groupSV": (
            "numSv",
            OrderedDict({  # repeating group * numSv
                "svid": IN,
                "status": CH,
                "azi": DE,
                "ele": DE,
                "cno": IN,
                "lck": IN,
            }),
        ),
    }),
    "UBX04": OrderedDict({
        "msgId": ST,  # '04'
        "time": TM,
        "date": DT,
        "utcTow": ST,
        "utcWk": ST,
        "leapSec": ST,
        "clkBias": DE,
        "clkDrift": DE,
        "tpGran": IN,
    }),
    "UBX05": OrderedDict({  # deprecated, for backwards compat only
        "msgId": ST,  # '05'
        "pulses": IN,
        "period": IN,
        "gyroMean": IN,
        "temperature": DE,
        "direction": CH,
        "pulseScaleCS": IN,
        "gyroScaleCS": IN,
        "gyroBiasCS": IN,
        "pulseScale": DE,
        "gyroBias": DE,
        "gyroScale": DE,
        "pulseScaleAcc": IN,
        "gyroBiasAcc": IN,
        "gyroScaleAcc": IN,
        "measUsed": HX,
    }),
    # *********************************************
    # Dummy message for error testing
    # *********************************************
    "FOO": OrderedDict({"spam": "Z2", "eggs": "Y1"}),
})

