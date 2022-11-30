"""
GnssHandler class.

Connects the ucontroller to the GNSS receiver and handles the connection.

Queries different ublox messages from the GNSSreceiver and handles incoming data


Created on 4 Sep 2022

:author: vdueck
"""
import gc

import micropython
import network
from primitives.queue import Queue
from pyubx2.ubxmessage import UBXMessage
from pyubx2.ubxtypes_configdb import SET_LAYER_RAM, POLL_LAYER_RAM
from pyubx2.ubxtypes_core import POLL, SET, GET, UBX_MSGIDS

gc.collect()
class GnssHandler:
    """
    GnssHandler class.
    """
    _app = None
    _gga_q = None
    _cfg_response_q = None
    _nav_msg_q = None
    _ack_nack_q = None
    _msg_q = None
    _pos_q = None

    # predefined strings
    _config_key_gps = "CFG_SIGNAL_GPS_ENA"
    _config_key_gal = "CFG_SIGNAL_GAL_ENA"
    _config_key_glo = "CFG_SIGNAL_GLO_ENA"
    _config_key_bds = "CFG_SIGNAL_BDS_ENA"
    _config_key_hpm = "CFG-NMEA-HIGHPREC"
    _config_key_uart2_baud = "CFG_UART2_BAUDRATE"

    _nav_cls = "NAV"
    _cfg_cls = "CFG"
    _cfg_rate = "CFG-RATE"
    _cfg_msg = "CFG-MSG"
    _nav_pvt = "NAV-PVT"
    _nav_sat = "NAV-SAT"

    @classmethod
    def initialize(cls,
                   app: object,
                   gga_q: Queue,
                   cfg_resp_q: Queue,
                   nav_pvt_q: Queue,
                   ack_nack_q: Queue,
                   msg_q: Queue,
                   pos_q: Queue):
        """Initialization method.
        :param object app: The calling app
        :param primitives.queue.Queue gga_q: queue for incoming gga messages
        :param primitives.queue.Queue cfg_resp_q: queue for ubx responses to configuration messages
        :param primitives.queue.Queue nav_pvt_q: queue for incoming ubx NAV-PVT get messaged
        :param primitives.queue.Queue ack_nack_q: queue for incoming ubx ACK-NACK messages
        :param primitives.queue.Queue msg_q: queue for outgoing ubx messages
        """
        cls._app = app
        cls._gga_q = gga_q
        cls._cfg_response_q = cfg_resp_q
        cls._nav_msg_q = nav_pvt_q
        cls._ack_nack_q = ack_nack_q
        cls._msg_q = msg_q
        cls._pos_q = pos_q

        gc.collect()

    @classmethod
    async def set_update_rate(cls, update_rate: int) -> bool:
        """
        ASYNC: Sets the update rate of the GNSS receiver(how often a GGA sentence is sent over UART1)

        :param int update_rate: the update rate in ms. min=50 max=5000
        :return: True if successful, False if failed
        :rtype: bool
        """

        await cls._flush_receive_qs()
        if update_rate < 50:
            update_rate = 50
        if update_rate > 5000:
            update_rate = 5000

        msg = UBXMessage(
            cls._cfg_cls,
            cls._cfg_rate,
            SET,
            measRate=update_rate,
            navRate=1,
            timeRef=1
        )
        await cls._msg_q.put(msg.serialize())
        ack = await cls._ack_nack_q.get()
        if ack.msg_id == b'\x01':  # ACK-ACK
            gc.collect()
            return True
        else:
            gc.collect()
            return False  # ACK-NACK

    @classmethod
    async def get_update_rate(cls) -> int:
        """
        ASYNC: Gets the update rate of the GNSS receiver(how often a GGA sentence is sent over UART1)

        :return: number representing ms between updates
        :rtype: int
        """
        await cls._flush_receive_qs()
        msg = UBXMessage(
            cls._cfg_cls,
            cls._cfg_rate,
            GET,
        )
        await cls._msg_q.put(msg.serialize())
        cfg = await cls._cfg_response_q.get()
        result = cfg.__dict__["measRate"]
        gc.collect()
        return int(result)

    @classmethod
    async def set_satellite_systems(cls,
                                    gps: int,
                                    gal: int,
                                    glo: int,
                                    bds: int) -> bool:
        """
        ASYNC: Configure the satellite systems the GNSS receiver should use in his navigation computing

        :param int gps: GPS On=1 / Off=0
        :param int glo: GLONASS On=1 / Off=0
        :param int gal: Galileo On=1 / Off=0
        :param int bds: BeiDou On=1 / Off=0
        :return: True if successful, False if failed
        :rtype: bool
        """
        await cls._flush_receive_qs()
        layer = SET_LAYER_RAM  # volatile memory
        transaction = 0
        cfg_data = [(cls._config_key_gps, gps),
                    (cls._config_key_gal, gal),
                    (cls._config_key_glo, glo),
                    (cls._config_key_bds, bds)]
        msg = UBXMessage.config_set(layer, transaction, cfg_data)
        await cls._msg_q.put(msg.serialize())
        ack = await cls._ack_nack_q.get()
        if ack.msg_id == b'\x01':  # ACK-ACK
            gc.collect()
            return True
        else:
            gc.collect()
            return False  # ACK-NACK

    @classmethod
    async def get_satellite_systems(cls) -> dict:
        """
        ASYNC: Get the satellite systems the GNSS receiver uses in his navigation computing
        e.g.:
        {
            "gps": 1,
            "glo": 0,
            "gal": 1,
            "bds": 0
        }
        :return: Dictionary with satellite systems and values
        :rtype: dict if successful, None if failed
        """

        await cls._flush_receive_qs()
        layer = POLL_LAYER_RAM  # volatile memory
        position = 0
        keys = [cls._config_key_gps, cls._config_key_gal, cls._config_key_glo, cls._config_key_bds]
        msg = UBXMessage.config_poll(layer, position, keys)
        await cls._msg_q.put(msg.serialize())
        cfg = await cls._cfg_response_q.get()
        val_gps = cfg.__dict__[cls._config_key_gps]
        val_glo = cfg.__dict__[cls._config_key_glo]
        val_gal = cfg.__dict__[cls._config_key_gal]
        val_bds = cfg.__dict__[cls._config_key_bds]
        result = {
            "gps": int(val_gps),
            "glo": int(val_glo),
            "gal": int(val_gal),
            "bds": int(val_bds),
        }
        gc.collect()
        return result

    @classmethod
    async def get_precision(cls) -> tuple:
        """
        ASYNC: Gets precision of measurement

        :return: hAcc, Vacc
        :rtype: int, int
        """
        await cls._flush_receive_qs()
        msg = UBXMessage(
            cls._nav_cls,
            cls._nav_pvt,
            GET
        )
        await cls._msg_q.put(msg.serialize())
        nav = await cls._nav_msg_q.get()
        # if ack.msg_id == b'\x01':  # ACK-ACK
        h_acc = nav.__dict__["hAcc"]
        v_acc = nav.__dict__["vAcc"]
        gc.collect()
        print("nav pvt: " + str(nav))
        return h_acc, v_acc

    @classmethod
    async def get_fixtype(cls) -> int:
        """
        ASYNC: Gets fix type of navigation

        :return: fixtype
        :rtype: int
        """
        await cls._flush_receive_qs()
        position = await cls._pos_q.get()
        return position["fixType"]

    @classmethod
    async def get_precision_position(cls):
        """
        ASYNC: Gets "NAV-HPPOSLLH" message

        :return: fixtype
        :rtype: int
        """
        await cls._flush_receive_qs()
        msg = UBXMessage(
            cls._nav_cls,
            "NAV-HPPOSLLH",
            GET
        )
        await cls._msg_q.put(msg.serialize())
        nav = await cls._nav_msg_q.get()
        print(str(nav))

    @classmethod
    async def get_satellites_in_use(cls) -> UBXMessage:
        """
        ASYNC: Get the satellites used in navigation
        ATTENTION: Method does not work yet. Uses to much heap to create NAV-SAT Message!!!!!!!!
        :return: UBXMessage NAV-SAT containing satellites with details
        :rtype: UBXMessage
        """
        gc.collect()
        await cls._flush_receive_qs()
        msg = UBXMessage(
            cls._nav_cls,
            cls._nav_sat,
            GET
        )
        await cls._msg_q.put(msg.serialize())
        nav = await cls._nav_msg_q.get()
        gc.collect()
        return nav

    @classmethod
    async def set_high_precision_mode(cls, enable: int) -> bool:
        """
        ASYNC: Enable/Disable High Precision mode

        :param int enable: 0 = enable / 1 = disable
        :return: True if successful, False if failed
        :rtype: bool
        """
        await cls._flush_receive_qs()
        layer = SET_LAYER_RAM  # volatile memory
        transaction = 0
        cfg_data = [(cls._config_key_hpm, enable)]
        msg = UBXMessage.config_set(layer, transaction, cfg_data)
        await cls._msg_q.put(msg.serialize())
        ack = await cls._ack_nack_q.get()
        if ack.msg_id == b'\x01':  # ACK-ACK
            gc.collect()
            return True
        else:
            gc.collect()
            return False  # ACK-NACK

    @classmethod
    async def set_uart2_baudrate(cls, rate: int) -> bool:
        """
        ASYNC: Enable/Disable High Precision mode

        :param int enable: 0 = enable / 1 = disable
        :return: True if successful, False if failed
        :rtype: bool
        """
        await cls._flush_receive_qs()
        layer = SET_LAYER_RAM  # volatile memory
        transaction = 0
        cfg_data = [(cls._config_key_hpm, rate)]
        msg = UBXMessage.config_set(layer, transaction, cfg_data)
        await cls._msg_q.put(msg.serialize())
        ack = await cls._ack_nack_q.get()
        if ack.msg_id == b'\x01':  # ACK-ACK
            gc.collect()
            return True
        else:
            gc.collect()
            return False  # ACK-NACK

    @classmethod
    async def set_rtcm_status_update(cls) -> bool:
        """
        ASYNC: Gets "NAV-HPPOSLLH" message

        :return: fixtype
        :rtype: int
        """
        await cls._flush_receive_qs()
        for (msgid, msgname) in UBX_MSGIDS.items():
            if msgid[0] == 0x02:  # RXM
                if msgid[1] == 0x32:  # RXM-RTCM
                    msgnmea = UBXMessage(
                        cls._cfg_cls,
                        cls._cfg_msg,
                        SET,
                        msgClass=msgid[0],
                        msgID=msgid[1],
                        rateUART1=1,
                        rateUSB=0,
                    )
                    print(str(msgnmea))
                    await cls._msg_q.put(msgnmea.serialize())
                    gc.collect()
        ack = await cls._ack_nack_q.get()
        if ack.msg_id == b'\x01':  # ACK-ACK
            gc.collect()
            return True
        else:
            gc.collect()
            return False  # ACK-NACK

    @classmethod
    async def set_minimum_nmea_msgs(cls):
        """
        ASYNC: Deactivate all NMEA messages on UART1, except NMEA-GGA
        """
        await cls._flush_receive_qs()
        count = 0
        for (msgid, msgname) in UBX_MSGIDS.items():
            if msgid[0] == 0xf0:  # NMEA
                if msgid[1] == 0x00:  # NMEA-GGA
                    rate = 1
                else:
                    rate = 0
                msgnmea = UBXMessage(
                    cls._cfg_cls,
                    cls._cfg_msg,
                    SET,
                    msgClass=msgid[0],
                    msgID=msgid[1],
                    rateUART1=rate,
                    rateUSB=0,
                )
                await cls._msg_q.put(msgnmea.serialize())
                count = count + 1
                gc.collect()
        while not cls._ack_nack_q.empty:
            await cls._ack_nack_q.get()

        gc.collect()

    @classmethod
    async def run_get_precision(cls, wifi: network.WLAN):
        """
        ASYNC: Empty all receiving queues
        """
        while wifi.isconnected():
            await cls.get_precision_position()

    @classmethod
    async def _flush_receive_qs(cls):
        """
        ASYNC: Empty all receiving queues
        """
        while not cls._ack_nack_q.empty:
            await cls._ack_nack_q.get()
        while not cls._nav_msg_q.empty:
            await cls._nav_msg_q.get()
        while not cls._cfg_response_q.empty:
            await cls._cfg_response_q.get()


