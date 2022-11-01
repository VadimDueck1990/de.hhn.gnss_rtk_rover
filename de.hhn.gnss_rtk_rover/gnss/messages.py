from pynmeagps import  UBXMessage
from pyubx2 import UBX_MSGIDS

# set updaterate
############################################################################################
msgcfg = UBXMessage(
    "CFG",
    "CFG-RATE",
    SET,
    measRate=1000,
    navRate=1,
    timeRef=1
)

for (msgid, msgname) in UBX_MSGIDS.items():
    if msgid[0] == 0x01:  # NAV
        msgnavpvt = UBXMessage(
            "CFG",
            "CFG-MSG",
            SET,
            msgClass=msgid[0],
            msgID=msgid[1],
            rateUART1=1,
            rateUSB=1,
        )
        print(msgnavpvt)
        send_message(serial, serial_lock, msgnavpvt)

# get updaterate
#############################################################################################
msgcfg = UBXMessage(
    "CFG",
    "CFG-RATE",
    GET,
    measRate=1000,
    navRate=1,
    timeRef=1
)

#get satellite systems
#############################################################################################
CONFIG_KEY1 = "CFG_SIGNAL_GPS_ENA"
CONFIG_VAL1 = 1
CONFIG_KEY2 = "CFG_SIGNAL_GAL_ENA"
CONFIG_VAL2 = 0
CONFIG_KEY3 = "CFG_SIGNAL_GLO_ENA"
CONFIG_VAL3 = 0
CONFIG_KEY4 = "CFG_SIGNAL_BDS_ENA"
CONFIG_VAL4 = 0

layer = POLL_LAYER_RAM  # volatile memory
position = 0
keys = [CONFIG_KEY1, CONFIG_KEY2, CONFIG_KEY3, CONFIG_KEY4]
msg = UBXMessage.config_poll(layer, position, keys)
print(msg)
send_message(serial, serial_lock, msg)

# set satellite systems
#############################################################################################
CONFIG_KEY1 = "CFG_SIGNAL_GPS_ENA"
CONFIG_VAL1 = 1
CONFIG_KEY2 = "CFG_SIGNAL_GAL_ENA"
CONFIG_VAL2 = 0
CONFIG_KEY3 = "CFG_SIGNAL_GLO_ENA"
CONFIG_VAL3 = 0
CONFIG_KEY4 = "CFG_SIGNAL_BDS_ENA"
CONFIG_VAL4 = 0

layer = SET_LAYER_RAM  # volatile memory
transaction = 0
cfgData = [(CONFIG_KEY1, CONFIG_VAL1),
           (CONFIG_KEY2, CONFIG_VAL2),
           (CONFIG_KEY3, CONFIG_VAL3),
           (CONFIG_KEY4, CONFIG_VAL4)]
msg = UBXMessage.config_set(layer, transaction, cfgData)
print(msg)
send_message(serial, serial_lock, msg)

# get precision
#############################################################################################
msg = UBXMessage(
    "NAV",
    "NAV-PVT",
    GET
)
print(msg)
send_message(serial, serial_lock, msg)

# get satellites
#############################################################################################
msg = UBXMessage(
    "NAV",
    "NAV-SAT",
    GET
)
print(msg)
send_message(serial, serial_lock, msg)