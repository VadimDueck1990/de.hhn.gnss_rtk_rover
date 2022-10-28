"""
UBX Protocol Output payload definitions

THESE ARE THE PAYLOAD DEFINITIONS FOR _GET_ MESSAGES _FROM_ THE RECEIVER
(e.g. Periodic Navigation Data; Poll Responses; Info messages)

Created on 27 Sep 2020

Information sourced from u-blox Interface Specifications © 2013-2021, u-blox AG

:author: semuadmin
"""
# pylint: disable=too-many-lines, line-too-long

from pyubx2.ubxtypes_core import (
    A250,
    A256,
    C2,
    C6,
    C10,
    C30,
    C32,
    CH,
    I1,
    I2,
    I4,
    R4,
    R8,
    U1,
    U2,
    U3,
    U4,
    U5,
    U6,
    U7,
    U8,
    U9,
    U10,
    U11,
    U12,
    U16,
    U20,
    U22,
    U23,
    U24,
    U32,
    U64,
    X1,
    X2,
    X4,
    X24,
    SCAL9,
    SCAL7,
    SCAL6,
    SCAL5,
    SCAL4,
    SCAL3,
    SCAL2,
    SCAL1,
)


UBX_PAYLOADS_GET = {
    "ACK-ACK": {"clsID": U1, "msgID": U1},
    "ACK-NAK": {"clsID": U1, "msgID": U1},
    # ********************************************************************
    # Configuration Input Messages: i.e. Set Dynamic Model, Set DOP Mask, Set Baud Rate, etc..
    # Messages in the CFG class are used to configure the receiver and read out current configuration values. Any
    # messages in the CFG class sent to the receiver are either acknowledged (with message UBX-ACK-ACK) if
    # processed successfully or rejected (with message UBX-ACK-NAK) if processing unsuccessfully.
    "CFG-ANT": {
        "flags": (
            X2,
            {
                "svcs": U1,
                "scd": U1,
                "ocd": U1,
                "pdwnOnSCD": U1,
                "recovery": U1,
            },
        ),
        "pins": (
            X2,
            {
                "pinSwitch": U5,
                "pinSCD": U5,
                "pinOCD": U5,
                "reconfig": U1,
            },
        ),
    },
    "CFG-CFG": {
        "clearMask": X4,
        "saveMask": X4,
        "loadMask": X4,
        "deviceMask": (
            X1,
            {
                "devBBR": U1,
                "devFlash": U1,
                "devEEPROM": U1,
                "reserved1": U1,
                "devSpiFlash": U1,
            },
        ),
    },
    "CFG-DAT": {
        "datumNum": U2,
        "datumName": C6,
        "majA": R8,
        "flat": R8,
        "dX": R4,
        "dY": R4,
        "dZ": R4,
        "rotX": R4,
        "rotY": R4,
        "rotZ": R4,
        "scale": R4,
    },
    "CFG-DGNSS": {
        "dgnssMode": U1,
        "reserved0": U3,
    },
    "CFG-GEOFENCE": {
        "version": U1,
        "numFences": U1,
        "confLvl": U1,
        "reserved0": U1,
        "pioEnabled": U1,
        "pinPolarity": U1,
        "pin": U1,
        "reserved1": U1,
        "group": (
            "numFences",
            {
                "lat": [I4, SCAL7],
                "lon": [I4, SCAL7],
                "radius": [U4, SCAL2],
            },  # repeating group * numFences
        ),
    },
    "CFG-GNSS": {
        "msgVer": U1,
        "numTrkChHw": U1,
        "numTrkChUse": U1,
        "numConfigBlocks": U1,
        "group": (
            "numConfigBlocks",
            {  # repeating group * numConfigBlocks
                "gnssId": U1,
                "resTrkCh": U1,
                "maxTrkCh": U1,
                "reserved0": U1,
                "flags": (
                    X4,
                    {
                        "enable": U1,
                        "reserved1": U7,
                        "reserved2": U8,
                        "sigCfMask": U8,
                        "reserved3": U8,
                    },
                ),
            },
        ),
    },
    "CFG-INF": {
        "protocolID": U1,
        "reserved0": U3,
        "infMaskGroup": (
            6,
            {
                "infMsgMask": (
                    X1,
                    {
                        "enableError": U1,
                        "enableWarning": U1,
                        "enableNotice": U1,
                        "enableTest": U1,
                        "enableDebug": U1,
                    },
                ),
            },
        ),
    },
    "CFG-ITFM": {
        "config": (
            X4,
            {
                "bbThreshold": U4,
                "cwThreshold": U5,
                "algorithmBits": U22,
                "enable": U1,
            },
        ),
        "config2": (
            X4,
            {
                "generalBits": U12,
                "antSetting": U2,
                "enable2": U1,
            },
        ),
    },
    "CFG-LOGFILTER": {
        "version": U1,
        "flags": (
            X1,
            {
                "recordEnabled": U1,
                "psmOncePerWakupEnabled": U1,
                "applyAllFilterSettings": U1,
            },
        ),
        "minInterval": U2,
        "timeThreshold": U2,
        "speedThreshold": U2,
        "positionThreshold": U4,
    },
    "CFG-MSG": {
        "msgClass": U1,
        "msgID": U1,
        "rateDDC": U1,
        "rateUART1": U1,
        "rateUART2": U1,
        "rateUSB": U1,
        "rateSPI": U1,
        "reserved": U1,
    },
    "CFG-NAV5": {
        "mask": (
            X2,
            {
                "dyn": U1,
                "minEl": U1,
                "posFixMode": U1,
                "drLim": U1,
                "posMask": U1,
                "timeMask": U1,
                "staticHoldMask": U1,
                "dgpsMask": U1,
                "cnoThreshold": U1,
                "reserved0": U1,
                "utc": U1,
            },
        ),
        "dynModel": U1,
        "fixMode": U1,
        "fixedAlt": [I4, SCAL2],
        "fixedAltVar": [U4, SCAL4],
        "minElev": I1,
        "drLimit": U1,
        "pDop": [U2, SCAL1],
        "tDop": [U2, SCAL1],
        "pAcc": U2,
        "tAcc": U2,
        "staticHoldThresh": U1,
        "dgnssTimeOut": U1,
        "cnoThreshNumSVs": U1,
        "cnoThresh": U1,
        "reserved0": U2,
        "staticHoldMaxDist": U2,
        "utcStandard": U1,
        "reserved1": U5,
    },
    "CFG-NAVX5": {
        "version": U2,
        "mask1": (
            X2,
            {
                "reserved9": U2,
                "minMax": U1,
                "minCno": U1,
                "reserved10": U2,
                "initial3dfix": U1,
                "reserved11": U2,
                "wknRoll": U1,
                "ackAid": U1,
                "reserved12": U2,
                "ppp": U1,
                "aop": U1,
            },
        ),
        "mask2": (
            X4,
            {
                "reserved13": U6,
                "adr": U1,
                "sigAttenComp": U1,
            },
        ),
        "reserved0": U2,
        "minSVs": U1,
        "maxSVs": U1,
        "minCNO": U1,
        "reserved1": U1,
        "iniFix3D": U1,
        "reserved2": U2,
        "ackAiding": U1,
        "wknRollover": U2,
        "sigAttenCompMode": U1,
        "reserved3": U1,
        "reserved4": U2,
        "reserved5": U2,
        "usePPP": U1,
        "aopCfg": U1,
        "reserved6": U2,
        "aopOrbMaxErr": U2,
        "reserved7": U4,
        "reserved8": U3,
        "useAdr": U1,
    },
    "CFG-NMEA": {  # preferred version length 20
        "filter": (
            X1,
            {
                "posFilt": U1,
                "mskPosFilt": U1,
                "timeFilt": U1,
                "dateFilt": U1,
                "gpsOnlyFilter": U1,
                "trackFilt": U1,
            },
        ),
        "nmeaVersion": U1,
        "numSV": U1,
        "flags": (
            X1,
            {
                "compat": U1,
                "consider": U1,
                "limit82": U1,
                "highPrec": U1,
            },
        ),
        "gnssToFilter": (
            X4,
            {
                "gps": U1,
                "sbas": U1,
                "galileo": U1,
                "reserved2": U1,
                "qzss": U1,
                "glonass": U1,
                "beidou": U1,
            },
        ),
        "svNumbering": U1,
        "mainTalkerId": U1,
        "gsvTalkerId": U1,
        "version": U1,
        "bdsTalkerId": C2,
        "reserved1": U6,
    },
    "CFG-ODO": {
        "version": U1,
        "reserved0": U3,
        "flags": (
            X1,
            {
                "useODO": U1,
                "useCOG": U1,
                "outLPVel": U1,
                "outLPCog": U1,
            },
        ),
        "odoCfg": (
            X1,
            {
                "profile": U3,
            },
        ),
        "reserved1": U6,
        "cogMaxSpeed": [U1, SCAL1],
        "cogMaxPosAcc": U1,
        "reserved2": U2,
        "velLpGain": U1,
        "cogLpGain": U1,
        "reserved3": U2,
    },
    "CFG-PRT": {
        "portID": U1,
        "reserved0": U1,
        "txReady": (
            X2,
            {
                "enable": U1,
                "pol": U1,
                "pin": U5,
                "thres": U9,
            },
        ),
        "UARTmode": (
            X4,
            {
                "reserved2": U6,
                "charLen": U2,
                "reserved3": U1,
                "parity": U3,
                "nStopBits": U2,
            },
        ),
        "baudRate": U4,
        "inProtoMask": (
            X2,
            {
                "inUBX": U1,
                "inNMEA": U1,
                "inRTCM": U1,
                "reserved4": U2,
                "inRTCM3": U1,
            },
        ),
        "outProtoMask": (
            X2,
            {
                "outUBX": U1,
                "outNMEA": U1,
                "reserved5": U3,
                "outRTCM3": U1,
            },
        ),
        "flags": (
            X2,
            {
                "reserved6": U1,
                "extendedTxTimeout": U1,
            },
        ),
        "reserved1": U2,
    },
    "CFG-PWR": {"version": U1, "reserved1": U3, "state": U4},
    "CFG-RATE": {"measRate": U2, "navRate": U2, "timeRef": U2},
    "CFG-RINV": {
        "flags": (
            X1,
            {
                "dump": U1,
                "binary": U1,
            },
        ),
        "group": ("None", {"data": U1}),
    },  # repeating group
    "CFG-TMODE3": {
        "version": U1,
        "reserved0": U1,
        "flags": (
            X2,
            {
                "rcvrMode": U8,
                "lla": U1,
            },
        ),
        "ecefXOrLat": I4,
        "ecefYOrLon": I4,
        "ecefZOrAlt": I4,
        "ecefXOrLatHP": I1,
        "ecefYOrLonHP": I1,
        "ecefZOrAltHP": I1,
        "reserved1": U1,
        "fixedPosAcc": U4,
        "svinMinDur": U4,
        "svinAccLimit": U4,
        "reserved2": U8,
    },
    "CFG-TP5": {
        "tpIdx": U1,
        "version": U1,
        "reserved0": U2,
        "antCableDelay": I2,
        "rfGroupDelay": I2,
        "freqPeriod": U4,
        "freqPeriodLock": U4,
        "pulseLenRatio": U4,
        "pulseLenRatioLock": U4,
        "userConfigDelay": I4,
        "flags": (
            X4,
            {
                "active": U1,
                "lockGnssFreq": U1,
                "lockedOtherSet": U1,
                "isFreq": U1,
                "isLength": U1,
                "alignToTow": U1,
                "polarity": U1,
                "gridUtcGnss": U4,
                "syncMode": U3,
            },
        ),
    },
    "CFG-USB": {
        "vendorID": U2,
        "productID": U2,
        "reserved0": U2,
        "reserved1": U2,
        "powerConsumption": U2,
        "flags": (
            X2,
            {
                "reEnum": U1,
                "powerMode": U1,
            },
        ),
        "vendorString": C32,
        "productString": C32,
        "serialNumber": C32,
    },
    "CFG-VALGET": {
        "version": U1,
        "layer": U1,
        "position": U2,
        "group": ("None", {"cfgData": U1}),  # repeating group
    },
    # ********************************************************************
    # Information Messages: i.e. Printf-Style Messages, with IDs such as Error, Warning, Notice.
    # Messages in the INF class are used to output strings in a printf style from the firmware or application code. All
    # INF messages have an associated type to indicate the kind of message.
    "INF-DEBUG": {"message": CH},
    "INF-ERROR": {"message": CH},
    "INF-NOTICE": {"message": CH},
    "INF-TEST": {"message": CH},
    "INF-WARNING": {"message": CH},
    # ********************************************************************
    # Logging Messages: i.e. Log creation, deletion, info and retrieval.
    # Messages in the LOG class are used to configure and report status information of the logging feature.
    "LOG-FINDTIME": {"version": U1, "type": U1, "reserved0": U2, "entryNumber": U4},
    "LOG-INFO": {
        "version": U1,
        "reserved0": U3,
        "filestoreCapacity": U4,
        "reserved1": U8,
        "currentMaxLogSize": U4,
        "currentLogSize": U4,
        "entryCount": U4,
        "oldestYear": U2,
        "oldestMonth": U1,
        "oldestDay": U1,
        "oldestHour": U1,
        "oldestMinute": U1,
        "oldestSecond": U1,
        "reserved2": U1,
        "newestYear": U2,
        "newestMonth": U1,
        "newestDay": U1,
        "newestHour": U1,
        "newestMinute": U1,
        "newestSecond": U1,
        "reserved3": U1,
        "status": (
            X1,
            {
                "reserved5": U3,
                "recording": U1,
                "inactive": U1,
                "circular": U1,
            },
        ),
        "reserved4": U3,
    },
    "LOG-RETRIEVEPOS": {
        "entryIndex": U4,
        "lon": [I4, SCAL7],
        "lat": [I4, SCAL7],
        "hMSL": I4,
        "hAcc": U4,
        "gSpeed": U4,
        "heading": [U4, SCAL5],
        "version": U1,
        "fixType": U1,
        "year": U2,
        "month": U1,
        "day": U1,
        "hour": U1,
        "minute": U1,
        "second": U1,
        "reserved0": U1,
        "numSV": U1,
        "reserved1": U1,
    },
    "LOG-RETRIEVEPOSEXTRA": {
        "entryIndex": U4,
        "version": U1,
        "reserved0": U1,
        "year": U2,
        "month": U1,
        "day": U1,
        "hour": U1,
        "minute": U1,
        "second": U1,
        "reserved1": U3,
        "distance": U4,
        "reserved2": U12,
    },
    "LOG-RETRIEVESTRING": {
        "entryIndex": U4,
        "version": U1,
        "reserved0": U1,
        "year": U2,
        "month": U1,
        "day": U1,
        "hour": U1,
        "minute": U1,
        "second": U1,
        "reserved1": U1,
        "byteCount": U2,
        "group": ("byteCount", {"bytes": U1}),  # repeating group * byteCount
    },
    # ********************************************************************
    # Multiple GNSS Assistance Messages: i.e. Assistance data for various GNSS.
    # Messages in the MGA class are used for GNSS aiding information from and to the receiver.
    "MGA-ACK-DATA0": {
        "type": U1,
        "version": U1,
        "infoCode": U1,
        "msgId": U1,
        "msgPayloadStart": U4,
    },
    "MGA-DBD": {"reserved1": U12, "group": ("None", {"data": U1})},  # repeating group
    # ********************************************************************
    # Monitoring Messages: i.e. Communication Status, CPU Load, Stack Usage, Task Status.
    # Messages in the MON class are used to report the receiver status, such as CPU load, stack usage, I/O subsystem
    # statistics etc.
    "MON-COMMS": {
        "version": U1,
        "nPorts": U1,
        "txErrors": (
            X1,
            {
                "mem": U1,
                "alloc": U1,
            },
        ),
        "reserved0": U1,
        "protgroup": (
            4,
            {  # repeating group * 4
                "protIds": U1,
            },
        ),
        "portsgroup": (
            "nPorts",
            {  # repeating group * nPorts
                "portId": U2,
                "txPending": U2,
                "txBytes": U4,
                "txUsage": U1,
                "txPeakUsage": U1,
                "rxPending": U2,
                "rxBytes": U4,
                "rxUsage": U1,
                "rxPeakUsage": U1,
                "overrunErrs": U2,
                "msggroup": (
                    4,
                    {
                        "msgs": U2,
                    },
                ),
                "reserved1": U8,
                "skipped": U4,
            },
        ),
    },
    "MON-GNSS": {
        "version": U1,
        "supported": (
            X1,
            {
                "GPSSup": U1,
                "GlonassSup": U1,
                "BeidouSup": U1,
                "GalileoSup": U1,
            },
        ),
        "defaultGnss": (
            X1,
            {
                "GPSDef": U1,
                "GlonassDef": U1,
                "BeidouDef": U1,
                "GalileoDef": U1,
            },
        ),
        "enabled": (
            X1,
            {
                "GPSEna": U1,
                "GlonassEna": U1,
                "BeidouEna": U1,
                "GalileoEna": U1,
            },
        ),
        "simultaneous": U1,
        "reserved0": U3,
    },
    "MON-HW": {
        "pinSel": X4,
        "pinBank": X4,
        "pinDir": X4,
        "pinVal": X4,
        "noisePerMS": U2,
        "agcCnt": U2,
        "aStatus": U1,
        "aPower": U1,
        "flags": (
            X1,
            {
                "rtcCalib": U1,
                "safeBoot": U1,
                "jammingState": U2,
                "xtalAbsent": U1,
            },
        ),
        "reserved0": U1,
        "usedMask": X4,
        "groupVP": (
            17,
            {
                "VP": X1,
            },
        ),  # repeating group * 17
        "jamInd": U1,
        "reserved1": U2,
        "pinIrq": X4,
        "pullH": X4,
        "pullL": X4,
    },
    "MON-HW2": {
        "ofsI": I1,
        "magI": U1,
        "ofsQ": I1,
        "magQ": U1,
        "cfgSource": U1,
        "reserved0": U3,
        "lowLevCfg": U4,
        "reserved1": U8,
        "postStatus": U4,
        "reserved2": U4,
    },
    "MON-HW3": {
        "version": U1,
        "nPins": U1,
        "flags": (
            X1,
            {
                "rtcCalib": U1,
                "safeBoot": U1,
                "xtalAbsent": U1,
            },
        ),
        "hwVersion": C10,
        "reserved0": U9,
        "pingroup": (  # repeating group * nPins
            "nPins",
            {
                "pinId": U2,
                "pinMask": (
                    X2,
                    {
                        "periphPIO": U1,
                        "pinBank": U3,
                        "direction": U1,
                        "pinValue": U1,
                        "vpManager": U1,
                        "pioIrq": U1,
                        "pioPullHigh": U1,
                        "pioPullLow": U1,
                    },
                ),
                "VP": U1,
                "reserved1": U1,
            },
        ),
    },
    "MON-IO": {
        "rxBytes": U4,
        "txBytes": U4,
        "parityErrs": U2,
        "framingErrs": U2,
        "overrunErrs": U2,
        "breakCond": U2,
        "rxBusy": U1,
        "txBusy": U1,
        "reserved1": U2,
    },
    "MON-MSGPP": {
        "groupmsg1": (
            8,
            {
                "msg1": U2,
            },
        ),  # repeating group * 8
        "groupmsg2": (
            8,
            {
                "msg2": U2,
            },
        ),  # repeating group * 8
        "groupmsg3": (
            8,
            {
                "msg3": U2,
            },
        ),  # repeating group * 8
        "groupmsg4": (
            8,
            {
                "msg4": U2,
            },
        ),  # repeating group * 8
        "groupmsg5": (
            8,
            {
                "msg5": U2,
            },
        ),  # repeating group * 8
        "groupmsg6": (
            8,
            {
                "msg6": U2,
            },
        ),  # repeating group * 8
        "groupskipped": (
            6,
            {
                "skipped": U4,
            },
        ),  # repeating group * 6
    },
    "MON-PATCH": {
        "version": U2,
        "nEntries": U2,
        "group": (  # repeating group * nEntries
            "nEntries",
            {
                "patchInfo": (
                    X4,
                    {
                        "activated": U1,
                        "location": U2,
                    },
                ),
                "comparatorNumber": U4,
                "patchAddress": U4,
                "patchData": U4,
            },
        ),
    },
    "MON-RF": {
        "version": U1,
        "nBlocks": U1,
        "reserved0": U2,
        "group": (  # repeating group * nBlocks
            "nBlocks",
            {
                "blockId": U1,
                "flags": (
                    X1,
                    {
                        "jammingState": U1,
                    },
                ),
                "antStatus": U1,
                "antPower": U1,
                "postStatus": U4,
                "reserved1": U4,
                "noisePerMS": U2,
                "agcCnt": U2,
                "jamInd": U1,
                "ofsI": I1,
                "magI": U1,
                "ofsQ": I1,
                "magQ": U1,
                "reserved2": U3,
            },
        ),
    },
    "MON-RXBUF": {
        "groupPending": (
            6,
            {
                "pending": U2,
            },
        ),  # repeating group * 6
        "groupUsage": (
            6,
            {
                "usage": U1,
            },
        ),  # repeating group * 6
        "groupPeakUsage": (
            6,
            {
                "peakUsage": U1,
            },
        ),  # repeating group * 6
    },
    "MON-RXR": {
        "flags": (
            X1,
            {
                "awake": U1,
            },
        ),
    },
    "MON-TXBUF": {
        "groupPending": (  # repeating group * 6
            6,
            {
                "pending": U2,
            },
        ),
        "groupUsage": (  # repeating group * 6
            6,
            {
                "usage": U1,
            },
        ),
        "groupPeakUsage": (  # repeating group * 6
            6,
            {
                "peakUsage": U1,
            },
        ),
        "tUsage": U1,
        "tPeakUsage": U1,
        "errors": (
            X1,
            {
                "limit": U6,
                "lem": U1,
                "alloc": U1,
            },
        ),
        "reserved0": U1,
    },
    "MON-VER": {
        "swVersion": C30,
        "hwVersion": C10,
        "group": ("None", {"extension": C30}),  # repeating group
    },
    "NAV-CLOCK": {"iTOW": U4, "clkB": I4, "clkD": I4, "tAcc": U4, "fAcc": U4},
    "NAV-DOP": {
        "iTOW": U4,
        "gDOP": [U2, SCAL2],
        "pDOP": [U2, SCAL2],
        "tDOP": [U2, SCAL2],
        "vDOP": [U2, SCAL2],
        "hDOP": [U2, SCAL2],
        "nDOP": [U2, SCAL2],
        "eDOP": [U2, SCAL2],
    },
    "NAV-EOE": {"iTOW": U4},
    "NAV-GEOFENCE": {
        "iTOW": U4,
        "version": U1,
        "status": U1,
        "numFences": U1,
        "combState": U1,
        "group": (  # repeating group * numFences
            "numFences",
            {"state": U1, "reserved1": U1},
        ),
    },
    # NB: special handling for NAV-HPPOS* message types;
    # private standard and high precision attributes are
    # combined into a single public attribute in
    # accordance with interface specification
    "NAV-HPPOSECEF": {
        "version": U1,
        "reserved0": U3,
        "iTOW": U4,
        "_ecefX": I4,  # cm
        "_ecefY": I4,  # cm
        "_ecefZ": I4,  # cm
        "_ecefXHp": [I1, SCAL1],  # mm
        "_ecefYHp": [I1, SCAL1],  # mm
        "_ecefZHp": [I1, SCAL1],  # mm
        "flags": (
            X1,
            {
                "invalidEcef": U1,
            },
        ),
        "pAcc": [U4, SCAL1],
    },
    "NAV-HPPOSLLH": {
        "version": U1,
        "reserved0": U2,
        "flags": (
            X1,
            {
                "invalidLlh": U1,
            },
        ),
        "iTOW": U4,
        "_lon": [I4, SCAL7],
        "_lat": [I4, SCAL7],
        "_height": I4,  # mm
        "_hMSL": I4,  # mm
        "_lonHp": [I1, SCAL9],
        "_latHp": [I1, SCAL9],
        "_heightHp": [I1, SCAL1],  # mm
        "_hMSLHp": [I1, SCAL1],  # mm
        "hAcc": [U4, SCAL1],
        "vAcc": [U4, SCAL1],
    },
    "NAV-ODO": {
        "version": U1,
        "reserved0": U3,
        "iTOW": U4,
        "distance": U4,
        "totalDistance": U4,
        "distanceStd": U4,
    },
    "NAV-ORB": {
        "iTOW": U4,
        "version": U1,
        "numSv": U1,
        "reserved0": U2,
        "group": (  # repeating group * numSv
            "numSv",
            {
                "gnssId": U1,
                "svId": U1,
                "svFlag": (
                    X1,
                    {
                        "health": U2,
                        "visibility": U2,
                    },
                ),
                "eph": (
                    X1,
                    {
                        "ephUsability": U5,
                        "ephSource": U3,
                    },
                ),
                "alm": (
                    X1,
                    {
                        "almUsability": U5,
                        "almSource": U3,
                    },
                ),
                "otherOrb": (
                    X1,
                    {
                        "anoAopUsability": U5,
                        "type": U3,
                    },
                ),
            },
        ),
    },
    "NAV-POSECEF": {"iTOW": U4, "ecefX": I4, "ecefY": I4, "ecefZ": I4, "pAcc": U4},
    "NAV-POSLLH": {
        "iTOW": U4,
        "lon": [I4, SCAL7],
        "lat": [I4, SCAL7],
        "height": I4,
        "hMSL": I4,
        "hAcc": U4,
        "vAcc": U4,
    },
    "NAV-PVT": {
        "iTOW": U4,
        "year": U2,
        "month": U1,
        "day": U1,
        "hour": U1,
        "min": U1,
        "second": U1,
        "valid": (
            X1,
            {
                "validDate": U1,
                "validTime": U1,
                "fullyResolved": U1,
                "validMag": U1,
            },
        ),
        "tAcc": U4,
        "nano": I4,
        "fixType": U1,
        "flags": (
            X1,
            {
                "gnssFixOk": U1,
                "difSoln": U1,
                "psmState": U3,
                "headVehValid": U1,
                "carrSoln": U2,
            },
        ),
        "flags2": (
            X1,
            {
                "reserved": U5,
                "confirmedAvai": U1,
                "confirmedDate": U1,
                "confirmedTime": U1,
            },
        ),
        "numSV": U1,
        "lon": [I4, SCAL7],
        "lat": [I4, SCAL7],
        "height": I4,
        "hMSL": I4,
        "hAcc": U4,
        "vAcc": U4,
        "velN": I4,
        "velE": I4,
        "velD": I4,
        "gSpeed": I4,
        "headMot": [I4, SCAL5],
        "sAcc": U4,
        "headAcc": [U4, SCAL5],
        "pDOP": [U2, SCAL2],
        "flags3": (
            X2,
            {
                "invalidLlh": U1,
                "lastCorrectionAge": U4,
            },
        ),
        "reserved0": U4,  # NB this is incorrectly stated as U5 in older documentation
        "headVeh": [I4, SCAL5],
        "magDec": [I2, SCAL2],
        "magAcc": [U2, SCAL2],
    },
    "NAV-RELPOSNED": {
        "version": U1,  # 0x01
        "reserved0": U1,
        "refStationID": U2,
        "iTOW": U4,
        "relPosN": I4,
        "relPosE": I4,
        "relPosD": I4,
        "relPosLength": I4,
        "relPosHeading": [I4, SCAL5],
        "reserved1": U4,
        "relPosHPN": [I1, SCAL1],
        "relPosHPE": [I1, SCAL1],
        "relPosHPD": [I1, SCAL1],
        "relPosHPLength": [I1, SCAL1],
        "accN": [U4, SCAL1],
        "accE": [U4, SCAL1],
        "accD": [U4, SCAL1],
        "accLength": [U4, SCAL1],
        "accHeading": [U4, SCAL5],
        "reserved2": U4,
        "flags": (
            X4,
            {
                "gnssFixOK": U1,
                "diffSoln": U1,
                "relPosValid": U1,
                "carrSoln": U2,
                "isMoving": U1,
                "refPosMiss": U1,
                "refObsMiss": U1,
                "relPosHeadingValid": U1,
                "relPosNormalized": U1,
            },
        ),
    },
    "NAV-SAT": {
        "iTOW": U4,
        "version": U1,
        "numSvs": U1,
        "reserved0": U2,
        "group": (  # repeating group * numSvs
            "numSvs",
            {
                "gnssId": U1,
                "svId": U1,
                "cno": U1,
                "elev": I1,
                "azim": I2,
                "prRes": [I2, SCAL1],
                "flags": (
                    X4,
                    {
                        "qualityInd": U3,
                        "svUsed": U1,
                        "health": U2,
                        "diffCorr": U1,
                        "smoothed": U1,
                        "orbitSource": U3,
                        "ephAvail": U1,
                        "almAvail": U1,
                        "anoAvail": U1,
                        "aopAvail": U1,
                        "reserved13": U1,
                        "sbasCorrUsed": U1,
                        "rtcmCorrUsed": U1,
                        "slasCorrUsed": U1,
                        "spartnCorrUsed": U1,
                        "prCorrUsed": U1,
                        "crCorrUsed": U1,
                        "doCorrUsed": U1,
                    },
                ),
            },
        ),
    },
    "NAV-SIG": {
        "iTOW": U4,
        "version": U1,
        "numSigs": U1,
        "reserved0": U2,
        "group": (
            "numSigs",
            {  # repeating group * numSigs
                "gnssId": U1,
                "svId": U1,
                "sigId": U1,
                "freqId": U1,
                "prRes": [I2, SCAL1],
                "cno": U1,
                "qualityInd": U1,
                "corrSource": U1,
                "ionoModel": U1,
                "sigFlags": (
                    X2,
                    {
                        "health": U2,
                        "prSmoothed": U1,
                        "prUsed": U1,
                        "crUsed": U1,
                        "doUsed": U1,
                        "prCorrUsed": U1,
                        "crCorrUsed": U1,
                        "doCorrUsed": U1,
                    },
                ),
                "reserved1": U4,
            },
        ),
    },
    "NAV-STATUS": {
        "iTOW": U4,
        "gpsFix": U1,
        "flags": (
            X1,
            {
                "gpsFixOk": U1,
                "diffSoln": U1,
                "wknSet": U1,
                "towSet": U1,
            },
        ),
        "fixStat": (
            X1,
            {
                "diffCorr": U1,
                "carrSolnValid": U1,
                "reserved0": U4,
                "mapMatching": U2,
            },
        ),
        "flags2": (
            X1,
            {
                "psmState": U2,
                "reserved1": U1,
                "spoofDetState": U2,
                "reserved2": U1,
                "carrSoln": U2,
            },
        ),
        "ttff": U4,
        "msss": U4,
    },
    "NAV-SVIN": {
        "version": U1,
        "reserved1": U3,
        "iTOW": U4,
        "dur": U4,
        "meanX": I4,
        "meanY": I4,
        "meanZ": I4,
        "meanXHP": I1,
        "meanYHP": I1,
        "meanZHP": I1,
        "reserved2": U1,
        "meanAcc": U4,
        "obs": U4,
        "valid": U1,
        "active": U1,
        "reserved3": U2,
    },
    "NAV-TIMEBDS": {
        "iTOW": U4,
        "SOW": U4,
        "fSOW": I4,
        "week": I2,
        "leapS": I1,
        "valid": (
            X1,
            {
                "sowValid": U1,
                "weekValid": U1,
                "leapSValid": U1,
            },
        ),
        "tAcc": U4,
    },
    "NAV-TIMEGAL": {
        "iTOW": U4,
        "galTow": U4,
        "fGalTow": I4,
        "galWno": I2,
        "leapS": I1,
        "valid": (
            X1,
            {
                "galTowValid": U1,
                "galWnoValid": U1,
                "leapSValid": U1,
            },
        ),
        "tAcc": U4,
    },
    "NAV-TIMEGLO": {
        "iTOW": U4,
        "TOD": U4,
        "fTOD": I4,
        "Nt": U2,
        "N4": U1,
        "valid": (
            X1,
            {
                "todValid": U1,
                "dateValid": U1,
            },
        ),
        "tAcc": U4,
    },
    "NAV-TIMEGPS": {
        "iTOW": U4,
        "fTOW": I4,
        "week": I2,
        "leapS": I1,
        "valid": (
            X1,
            {
                "towValid": U1,
                "weekValid": U1,
                "leapSValid": U1,
            },
        ),
        "tAcc": U4,
    },
    "NAV-TIMELS": {
        "iTOW": U4,
        "version": U1,
        "reserved0": U3,
        "srcOfCurrLs": U1,
        "currLs": I1,
        "srcOfLsChange": U1,
        "lsChange": I1,
        "timeToLsEvent": I4,
        "dateOfLsGpsWn": U2,
        "dateOfLsGpsDn": U2,
        "reserved1": U3,
        "valid": (
            X1,
            {
                "validCurrLs": U1,
                "validTimeToLsEvent": U1,
            },
        ),
    },
    "NAV-TIMEUTC": {
        "iTOW": U4,
        "tAcc": U4,
        "nano": I4,
        "year": U2,
        "month": U1,
        "day": U1,
        "hour": U1,
        "min": U1,
        "sec": U1,
        "validflags": (
            X1,
            {
                "validTOW": U1,
                "validWKN": U1,
                "validUTC": U1,
                "reserved0": U1,
                "utcStandard": U4,
            },
        ),
    },
    "NAV-VELECEF": {"iTOW": U4, "ecefVX": I4, "ecefVY": I4, "ecefVZ": I4, "sAcc": U4},
    "NAV-VELNED": {
        "iTOW": U4,
        "velN": I4,
        "velE": I4,
        "velD": I4,
        "speed": U4,
        "gSpeed": U4,
        "heading": [I4, SCAL5],
        "sAcc": U4,
        "cAcc": [U4, SCAL5],
    },
    # ********************************************************************
    #
    # NAV2 payloads are identical to NAV and are cross-referenced in
    # UBX_PAYLOADS_GET_NAV2 below.
    #
    # ********************************************************************
    # Receiver Manager Messages: i.e. Satellite Status, RTC Status.
    # Messages in the RXM class are used to output status and result data from the Receiver Manager. The output
    # rate is not bound to the navigation/measurement rate and messages can also be generated on events.
    "RXM-MEASX": {
        "version": U1,
        "reserved0": U3,
        "gpsTOW": U4,
        "gloTOW": U4,
        "bdsTOW": U4,
        "reserved1": U4,
        "qzssTOW": U4,
        "gpsTOWacc": [U2, 0.0625],
        "gloTOWacc": [U2, 0.0625],
        "bdsTOWacc": [U2, 0.0625],
        "reserved2": U2,
        "qzssTOWacc": [U2, 0.0625],
        "numSv": U1,
        "flags": (
            X1,
            {
                "towSet": U2,
            },
        ),
        "reserved3": U8,
        "group": (
            "numSv",
            {  # repeating group * numSv
                "gnssId": U1,
                "svId": U1,
                "cNo": U1,
                "mpathIndic": U1,
                "dopplerMS": [I4, 0.04],
                "dopplerHz": [I4, 0.2],
                "wholeChips": U2,
                "fracChips": U2,
                "codePhase": [U4, 2**-21],
                "intCodePhase": U1,
                "pseuRangeRMSErr": U1,
                "reserved4": U2,
            },
        ),
    },
    "RXM-PMP-V0": {
        "version": U1,  # 0x00
        "reserved0": U3,
        "timeTag": U4,
        "uniqueWord1": U4,
        "uniqueWord2": U4,
        "serviceIdentifier": U2,
        "spare": U1,
        "uniqueWordBitErrors": U1,
        "groupUserData": (
            504,
            {
                "userData": U1,
            },
        ),  # repeating group * 504
        "fecBits": U2,
        "ebno": [U1, 0.125],
        "reserved1": U1,
    },
    "RXM-PMP-V1": {
        "version": U1,  # 0x01
        "reserved0": U1,
        "numBytesUserData": U2,
        "timeTag": U4,
        "uniqueWord1": U4,
        "uniqueWord2": U4,
        "serviceIdentifier": U2,
        "spare": U1,
        "uniqueWordBitErrors": U1,
        "fecBits": U2,
        "ebno": [U1, 0.125],
        "reserved1": U1,
        "groupUserData": (
            "numBytesUserData",
            {  # repeating group * numBytesUserData
                "userData": U1,
            },
        ),
    },
    "RXM-RAWX": {
        "rcvTow": R8,
        "week": U2,
        "leapS": I1,
        "numMeas": U1,
        "recStat": (
            X1,
            {
                "leapSec": U1,
                "clkReset": U1,
            },
        ),
        "reserved1": U3,
        "group": (
            "numMeas",
            {  # repeating group * numMeas
                "prMes": R8,
                "cpMes": R8,
                "doMes": R4,
                "gnssId": U1,
                "svId": U1,
                "reserved2": U1,
                "freqId": U1,
                "locktime": U2,
                "cno": U1,
                "prStdev": (
                    X1,  # scaling = 0.01*2^-n
                    {
                        "prStd": U4,
                    },
                ),
                "cpStdev": (
                    X1,  # scaling = 0.004
                    {
                        "cpStd": U4,
                    },
                ),
                "doStdev": (
                    X1,  # scaling = 0.002*2^n
                    {
                        "doStd": U4,
                    },
                ),
                "trkStat": (
                    X1,
                    {
                        "prValid": U1,
                        "cpValid": U1,
                        "halfCyc": U1,
                        "subHalfCyc": U1,
                    },
                ),
                "reserved3": U1,
            },
        ),
    },
    "RXM-RLM-S": {
        "version": U1,  # 0x00
        "type": U1,  # 0x01
        "svId": U1,
        "reserved0": U1,
        "beacon": U8,
        "message": U1,
        "params": U2,
        "reserved1": U1,
    },
    "RXM-RLM-L": {
        "version": U1,  # 0x00
        "type": U1,  # 0x02
        "svId": U1,
        "reserved0": U1,
        "beacon": U8,
        "message": U1,
        "params": U12,
        "reserved1": U3,
    },
    "RXM-RTCM": {
        "version": U1,  # 0x02
        "flags": (
            X1,
            {
                "crcFailed": U1,
                "msgUsed": U2,
            },
        ),
        "subType": U2,
        "refStation": U2,
        "msgType": U2,
    },
    "RXM-SFRBX": {
        "gnssId": U1,
        "svId": U1,
        "reserved0": U1,
        "freqId": U1,
        "numWords": U1,
        "chn": U1,
        "version": U1,
        "reserved1": U1,
        "navdata": ("numWords", {"dwrd": U4}),  # repeating group * numWords
    },
    # ********************************************************************
    # Security Feature Messages
    # Messages in the SEC class are used for security features of the receiver.
    "SEC-UNIQID": {"version": U1, "reserved0": U3, "uniqueId": U5},  # 0x01
    # ********************************************************************
    # Timing Messages: i.e. Time Pulse Output, Time Mark Results.
    # Messages in the TIM class are used to output timing information from the receiver, like Time Pulse and Time
    # Mark measurements.
    "TIM-TM2": {
        "ch": U1,
        "flags": (
            X1,
            {
                "mode": U1,
                "run": U1,
                "newFallingEdge": U1,
                "timeBase": U2,
                "utc": U1,
                "time": U1,
                "newRisingEdge": U1,
            },
        ),
        "count": U2,
        "wnR": U2,
        "wnF": U2,
        "towMsR": U4,
        "towSubMsR": U4,
        "towMsF": U4,
        "towSubMsF": U4,
        "accEst": U4,
    },
    "TIM-TP": {
        "towMS": U4,
        "towSubMS": [U4, 2**-32],
        "qErr": I4,
        "week": U2,
        "flags": (
            X1,
            {
                "timeBase": U1,
                "utc": U1,
                "raim": U2,
                "qErrInvalid": U1,
            },
        ),
        "refinfo": (
            X1,
            {
                "timeRefGnss": U4,
                "utcStandard": U4,
            },
        ),
    },
    "TIM-VRFY": {
        "itow": I4,
        "frac": I4,
        "deltaMs": I4,
        "deltaNs": I4,
        "wno": U2,
        "flags": (
            X1,
            {
                "src": U3,
            },
        ),
        "reserved1": U1,
    },
    # ********************************************************************
    # Firmware Update Messages: i.e. Memory/Flash erase/write, Reboot, Flash identification, etc..
    # Messages in the UPD class are used to update the firmware and identify any attached flash device.
    "UPD-SOS": {  # System restored from backup
        "cmd": U1,
        "reserved0": U3,
        "response": U1,
        "reserved1": U3,
    },
    # ********************************************************************
    # UBX nominal payload definition, used as fallback where no documented
    # payload definition is available.
    "UBX-NOMINAL": {
        "group": (
            "None",
            {
                "data": X1,
            },
        )
    },
    # ********************************************************************
    # Dummy message for error testing
    "FOO-BAR": {"spam": "Z2", "eggs": "Y1"},
}
