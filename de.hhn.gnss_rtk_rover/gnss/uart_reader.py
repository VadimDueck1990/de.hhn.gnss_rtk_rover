"""
UartReader class.

Connects the ucontroller to the GNSS Receiver

Read messages from the receiver and put it on the corresponding Queue


Created on 4 Sep 2022

:author: vdueck
"""
import gc
import uasyncio

import primitives.queue
import utils.logging as logging
import pyubx2.ubxtypes_core as ubt
import pyubx2.exceptions as ube
from pyubx2.ubxmessage import UBXMessage
from pyubx2.ubxhelpers import calc_checksum, bytes2val

_logger = logging.getLogger("uart_reader")
# _logger.setLevel(logging.WARNING)
gc.collect()

class UartReader:
    """
    UartReader class.
    """

    _app = None
    _sreader = None
    _gga_q = None
    _cfg_resp_q = None
    _nav_pvt_q = None
    _ack_nack_q = None

    @classmethod
    def initialize(cls,
                  app: object,
                  sreader: uasyncio.StreamReader,
                  gga_q: primitives.queue.Queue,
                  cfg_resp_q: primitives.queue.Queue,
                  nav_pvt_q: primitives.queue.Queue,
                  ack_nack_q: primitives.queue.Queue):
        """Initialize class variables.

        :param object app: The calling app
        :param uasyncio.StreamReader sreader: the serial connection to the GNSS Receiver(UART1)
        :param primitives.queue.Queue gga_q: queue for gga messages
        :param primitives.queue.Queue cfg_resp_q: queue for ubx responses to configuration messages
        :param primitives.queue.Queue nav_pvt_q: queue for ubx NAV-PVT get messaged
        :param primitives.queue.Queue ack_nack_q: queue for ubx ACK-NACK messages
        """

        cls._app = app
        cls._sreader = sreader
        cls._gga_q = gga_q
        cls._cfg_resp_q = cfg_resp_q
        cls._nav_pvt_q = nav_pvt_q
        cls._ack_nack_q = ack_nack_q
        gc.collect()

    @classmethod
    async def run(cls):
        """
        ASYNC: Read incoming data from UART1 and pass it to the corresponding queue
        """

        while True:
            byte1 = await cls._sreader.read(1)
            # if not UBX, NMEA or RTCM3, discard and continue
            if byte1 not in (b"\xb5", b"\x24", b"\xd3"):
                continue
            byte2 = await cls._sreader.read(1)
            bytehdr = byte1 + byte2
            # if it's an NMEA message ('$G' or '$P')
            if bytehdr in ubt.NMEA_HDR:
                # read the rest of the NMEA message from the buffer
                byten = await cls._sreader.readline()  # NMEA protocol is CRLF-terminated
                raw_data = bytehdr + byten
                # calculate checksum
                if not cls._isvalid_cksum(raw_data):
                    _logger.warn("NMEA Sentence corrupted, invalid checksum")
                    gc.collect()
                    continue
                _logger.info("nmea sentence received" + str(raw_data))
                # if the queue is full then skip. The gga consumer needs to handle messages fast enough otherwise
                # rxBuffer will overflow
                if cls._gga_q.full():
                    gc.collect()
                    continue
                await cls._gga_q.put(raw_data)
            # if it's a UBX message (b'\xb5\x62')
            if bytehdr in ubt.UBX_HDR:
                msg = await cls._parse_ubx(bytehdr)
                _logger.info("ubx message received")
                if msg.msg_cls == b"\x05":  # ACK-ACK or ACK-NACK message
                    _logger.info("parsed ACK/NACK message")
                    if cls._ack_nack_q.full():
                        gc.collect()
                        continue
                    await cls._ack_nack_q.put(msg)
                    gc.collect()
                if msg.msg_cls == b"\x06":  # CFG message
                    _logger.info("Parsed CFG Message")
                    if cls._cfg_resp_q.full():
                        gc.collect()
                        continue
                    await cls._cfg_resp_q.put(msg)
                    gc.collect()
                if msg.msg_cls == b"\x01":  # NAV message
                    _logger.info("Parsed NAV Message: ")
                    if cls._cfg_resp_q.full():
                        gc.collect()
                        continue
                    await cls._nav_pvt_q.put(msg)
                    gc.collect()

    @classmethod
    async def _parse_ubx(cls, hdr: bytes) -> UBXMessage:
        """
        Parse remainder of UBX message.

        :param bytes hdr: UBX header (b'\xb5\x62')
        :return: tuple of (raw_data as bytes, parsed_data as UBXMessage or None)
        :rtype: tuple
        """

        # read the rest of the UBX message from the buffer
        byten = await cls._sreader.read(4)
        clsid = byten[0:1]
        msgid = byten[1:2]
        lenb = byten[2:4]
        leni = int.from_bytes(lenb, "little", False)
        byten = await cls._sreader.read(leni + 2)
        plb = byten[0:leni]
        cksum = byten[leni: leni + 2]
        raw_data = hdr + clsid + msgid + lenb + plb + cksum
        parsed_data = cls.parse(
            raw_data
        )
        gc.collect()
        return parsed_data

    @staticmethod
    def parse(message: bytes) -> UBXMessage:
        """
        Parse UBX byte stream to UBXMessage object.

        Includes option to validate incoming payload length and checksum
        (the UBXMessage constructor can calculate and assign its own values anyway).

        :param bytes message: binary message to parse
        :return: UBXMessage object
        :rtype: UBXMessage
        :raises: UBXParseError (if data stream contains invalid data or unknown message type)

        """

        msgmode = 0
        validate = ubt.VALCKSUM
        parsebf = True
        scaling = True

        lenm = len(message)
        hdr = message[0:2]
        clsid = message[2:3]
        msgid = message[3:4]
        lenb = message[4:6]
        if lenb == b"\x00\x00":
            payload = None
            leni = 0
        else:
            payload = message[6: lenm - 2]
            leni = len(payload)
        ckm = message[lenm - 2: lenm]
        if payload is not None:
            ckv = calc_checksum(clsid + msgid + lenb + payload)
        else:
            ckv = calc_checksum(clsid + msgid + lenb)
        if validate & ubt.VALCKSUM:
            if hdr != ubt.UBX_HDR:
                raise ube.UBXParseError(
                    ("Invalid message header {} - should be {}".format(hdr, ubt.UBX_HDR))
                )
            if leni != bytes2val(lenb, ubt.U2):
                raise ube.UBXParseError(
                    (
                        "Invalid payload length {}.".format(lenb)
                    )
                )
            if ckm != ckv:
                raise ube.UBXParseError(
                    ("Message checksum {} invalid - should be {}".format(ckm, ckv))
                )
        try:
            gc.collect()
            if payload is None:
                return UBXMessage(clsid, msgid, msgmode)
            return UBXMessage(
                clsid,
                msgid,
                msgmode,
                payload=payload,
                parsebitfield=parsebf,
                scaling=scaling,
            )
        except KeyError as err:
            gc.collect()
            modestr = ["GET", "SET", "POLL"][msgmode]
            raise ube.UBXParseError(
                """Unknown message type clsid {}, msgid {}, mode {}.\n
                Check 'msgmode' keyword argument is appropriate for message category""".format(clsid, msgid, modestr)
            ) from err

    @staticmethod
    def _int2hexstr(val: int) -> str:
        """
        Convert integer to hex string representation.

        :param int val: integer < 255 e.g. 31
        :return: hex representation of integer e.g. '1F'
        :rtype: str
        """
        raw_hex = str(hex(val)).upper()
        final_hex = raw_hex[2:]
        if len(final_hex) < 2:
            gc.collect()
            return "0" + final_hex
        gc.collect()
        return final_hex

    @staticmethod
    def _get_content(message: object) -> str:
        """
        Get content of raw NMEA message (everything between "$" and "*").

        :param object message: entire message as bytes or string
        :return: content as str
        :rtype: str
        """

        if isinstance(message, bytes):
            message = message.decode("utf-8")
        content, _ = message.strip("$\r\n").split("*", 1)
        gc.collect()
        return content

    @classmethod
    def _calc_checksum(cls, message: object) -> str:
        """
        Calculate checksum for raw NMEA message.

        :param object message: entire message as bytes or string
        :return: checksum as hex string
        :rtype: str
        """

        content = cls._get_content(message)
        cksum = 0
        for sub in content:
            cksum ^= ord(sub)
            gc.collect()
        return cls._int2hexstr(cksum)

    @classmethod
    def _isvalid_cksum(cls, message: object) -> bool:
        """
        Validate raw NMEA message checksum.

        :param bytes message: entire message as bytes or string
        :return: checksum valid flag
        :rtype: bool
        """
        _, _, _, cksum = cls._get_parts(message)
        gc.collect()
        return cksum == cls._calc_checksum(message)

    @staticmethod
    def _get_parts(message: object) -> tuple:
        """
        Get talker, msgid, payload and checksum of raw NMEA message.

        :param object message: entire message as bytes or string
        :return: tuple of (talker as str, msgID as str, payload as list, checksum as str)
        :rtype: tuple
        :raises: NMEAMessageError (if message is badly formed)
        """

        try:
            if isinstance(message, bytes):
                message = message.decode("utf-8")
            content, cksum = message.strip("$\r\n").split("*", 1)

            hdr, payload = content.split(",", 1)
            payload = payload.split(",")
            if hdr[0:1] == "P":  # proprietary
                talker = "P"
                msgid = hdr[1:]
            else:  # standard
                talker = hdr[0:2]
                msgid = hdr[2:]
                gc.collect()
            return talker, msgid, payload, cksum
        except Exception as err:
            gc.collect()
            raise ube.NMEAMessageError(f"Badly formed message {message}") from err
