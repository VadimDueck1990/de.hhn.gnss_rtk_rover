"""
GnssHandler class.

Connects the ucontroller to the GNSS receiver and handles the connection.

Queries different ublox messages from the GNSSreceiver and handles incoming data


Created on 4 Sep 2022

:author: vdueck
"""
import gc
import uasyncio
from primitives.queue import Queue
import utils.logging as logging
from pyubx2.ubxmessage import UBXMessage
from pyubx2.ubxtypes_configdb import SET_LAYER_RAM, POLL_LAYER_RAM
from pyubx2.ubxtypes_core import POLL, SET, GET, UBX_MSGIDS

_logger = logging.getLogger("gnss_handler")


class GnssHandler:
    """
    GnssHandler class.
    """

    def __init__(self, app: object,
                 gga_q: Queue,
                 cfg_resp_q: Queue,
                 nav_pvt_q: Queue,
                 ack_nack_q: Queue,
                 msg_q: Queue):
        """Constructor.
        :param object app: The calling app
        :param primitives.queue.Queue gga_q: queue for incoming gga messages
        :param primitives.queue.Queue cfg_resp_q: queue for ubx responses to configuration messages
        :param primitives.queue.Queue nav_pvt_q: queue for incoming ubx NAV-PVT get messaged
        :param primitives.queue.Queue ack_nack_q: queue for incoming ubx ACK-NACK messages
        :param primitives.queue.Queue ack_nack_q: queue for outgoing ubx messages
        """
        self._app = app
        self._gga_q = gga_q
        self._cfg_response_q = cfg_resp_q
        self._nav_msg_q = nav_pvt_q
        self._ack_nack_q = ack_nack_q
        self._msg_q = msg_q

    async def set_update_rate(self, update_rate: int) -> bool:
        """
        ASYNC: Sets the update rate of the GNSS receiver(how often a GGA sentence is sent over UART1)

        :param int update_rate: the update rate in ms. min=50 max=5000
        :return: True if successful, False if failed
        :rtype: bool
        """
        if update_rate < 50:
            update_rate = 50
        if update_rate > 5000:
            update_rate = 5000

        msg = UBXMessage(
            "CFG",
            "CFG-RATE",
            SET,
            measRate=update_rate,
            navRate=1,
            timeRef=1
        )
        await self._msg_q.put(msg)
        ack = await self._ack_nack_q.get()
        if ack.msg_id == b'\x01':  # ACK-ACK
            return True
        else:
            return False  # ACK-NACK

    async def get_update_rate(self) -> int:
        """
        ASYNC: Gets the update rate of the GNSS receiver(how often a GGA sentence is sent over UART1)

        :return: number representing ms between updates
        :rtype: int
        """

        msg = UBXMessage(
            "CFG",
            "CFG-RATE",
            GET,
        )
        await self._msg_q.put(msg)
        ack = await self._ack_nack_q.get()
        if ack.msg_id == b'\x01':  # ACK-ACK
            cfg = await self._cfg_response_q.get()
            result = cfg.__dict__["measRate"]
            return int(result)
        else:  # ACK-NACK
            while not self._cfg_response_q.empty():
                await self._cfg_response_q.get()
            return 0

    async def set_satellite_systems(self,
                                    GPS: int,
                                    GLONASS: int,
                                    Galileo: int,
                                    BeiDou: int) -> bool:
        """
        ASYNC: Configure the satellite systems the GNSS receiver should use in his navigation computing

        :param int GPS: GPS On=1 / Off=0
        :param int GLONASS: GLONASS On=1 / Off=0
        :param int Galileo: Galileo On=1 / Off=0
        :param int BeiDou: BeiDou On=1 / Off=0
        :return: True if successful, False if failed
        :rtype: bool
        """
        config_key_gps = "CFG_SIGNAL_GPS_ENA"
        val_gps = GPS
        config_key_gal = "CFG_SIGNAL_GAL_ENA"
        val_gal = Galileo
        config_key_glo = "CFG_SIGNAL_GLO_ENA"
        val_glo = GLONASS
        config_key_bds = "CFG_SIGNAL_BDS_ENA"
        val_bds = BeiDou

        layer = SET_LAYER_RAM  # volatile memory
        transaction = 0
        cfg_data = [(config_key_gps, val_gps),
                   (config_key_gal, val_gal),
                   (config_key_glo, val_glo),
                   (config_key_bds, val_bds)]
        msg = UBXMessage.config_set(layer, transaction, cfg_data)
        await self._msg_q.put(msg)
        ack = await self._ack_nack_q.get()
        if ack.msg_id == b'\x01':  # ACK-ACK
            return True
        else:
            return False  # ACK-NACK

    async def get_satellite_systems(self) -> dict:
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
        config_key_gps = "CFG_SIGNAL_GPS_ENA"
        config_key_gal = "CFG_SIGNAL_GAL_ENA"
        config_key_glo = "CFG_SIGNAL_GLO_ENA"
        config_key_bds = "CFG_SIGNAL_BDS_ENA"

        layer = POLL_LAYER_RAM  # volatile memory
        position = 0
        keys = [config_key_gps, config_key_gal, config_key_glo, config_key_bds]
        msg = UBXMessage.config_poll(layer, position, keys)
        await self._msg_q.put(msg)
        ack = await self._ack_nack_q.get()
        if ack.msg_id == b'\x01':  # ACK-ACK
            cfg = await self._cfg_response_q.get()
            val_gps = cfg.__dict__[config_key_gps]
            val_glo = cfg.__dict__[config_key_glo]
            val_gal = cfg.__dict__[config_key_gal]
            val_bds = cfg.__dict__[config_key_bds]
            result = {
                "gps": int(val_gps),
                "glo": int(val_glo),
                "gal": int(val_gal),
                "bds": int(val_bds),
            }
            return result
        else:  # ACK-NACK
            while not self._cfg_response_q.empty():
                await self._cfg_response_q.get()
            return {}

    async def get_precision(self) -> tuple:
        """
        ASYNC: Gets precision of measurement

        :return: hAcc, Vacc
        :rtype: int, int
        """
        msg = UBXMessage(
            "NAV",
            "NAV-PVT",
            GET
        )
        await self._msg_q.put(msg)
        ack = await self._ack_nack_q.get()
        if ack.msg_id == b'\x01':  # ACK-ACK
            nav = await self._nav_msg_q.get()
            hAcc = nav.__dict__["hAcc"]
            vAcc = nav.__dict__["vAcc"]
            return hAcc, vAcc
        else:  # ACK-NACK
            while not self._nav_msg_q.empty():
                await self._nav_msg_q.get()
            return None, None

    async def get_satellites_in_use(self) -> UBXMessage:
        """
        ASYNC: Get the satellites used in navigation
        ATTENTION: Method does not work yet. Uses to much heap to create NAV-SAT Message!!!!!!!!
        :return: UBXMessage NAV-SAT containing satellites with details
        :rtype: UBXMessage
        """
        gc.collect()

        msg = UBXMessage(
            "NAV",
            "NAV-SAT",
            GET
        )
        await self._msg_q.put(msg)
        ack = await self._ack_nack_q.get()
        if ack.msg_id == b'\x01':  # ACK-ACK
            nav = await self._nav_msg_q.get()
            return nav
        else:  # ACK-NACK
            while not self._nav_msg_q.empty():
                await self._nav_msg_q.get()
            return None

    async def set_minimum_nmea_msgs(self):
        """
        ASYNC: Deactivate all NMEA messages on UART1, except NMEA-GGA
        """
        for (msgid, msgname) in UBX_MSGIDS.items():
            if msgid[0] == 0xf0:  # NMEA
                if msgid[1] == 0x00:  # NMEA-GGA
                    msgnmea = UBXMessage(
                        "CFG",
                        "CFG-MSG",
                        SET,
                        msgClass=msgid[0],
                        msgID=msgid[1],
                        rateUART1=1,
                        rateUSB=0,
                    )
                else:
                    msgnmea = UBXMessage(
                        "CFG",
                        "CFG-MSG",
                        SET,
                        msgClass=msgid[0],
                        msgID=msgid[1],
                        rateUART1=0,
                        rateUSB=0,
                    )
                await self._msg_q.put(msgnmea)
                if not self._ack_nack_q.empty():
                    ack = await self._ack_nack_q.get()
                    _logger.debug("received ACK-MSG:" + str(ack))
                gc.collect()
        gc.collect()

