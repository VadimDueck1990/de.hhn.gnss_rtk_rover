"""
NMEA Protocol Set payload definitions

THESE ARE THE PAYLOAD DEFINITIONS FOR _SET_ MESSAGES _TO_ THE RECEIVER
(e.g. Configuration commands).

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
    HX,
    IN,
    ST,
)

NMEA_PAYLOADS_SET = OrderedDict({
    # *********************************************
    # STANDARD MESSAGES
    # *********************************************
    # No standard SET messages that I'm aware of
    # *********************************************
    # U-BLOX PROPRIETARY MESSAGES
    # *********************************************
    "UBX40": OrderedDict({  # set message rates per port
        "msgId": ST,  # '40'
        "id": IN,
        "rddc": IN,  # I2C
        "rus1": IN,  # UART1
        "rus2": IN,  # UART2
        "rusb": IN,  # USB
        "rspi": IN,  # SPI
        "reserved": IN,
    }),
    "UBX41": OrderedDict({  # configure port protocols
        "msgId": ST,  # '41'
        "portId": IN,
        "inProto": HX,
        "outProto": HX,
        "baudRate": IN,
        "autobauding": IN,
    }),
})
