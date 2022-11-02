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
from pyubx2.ubxhelpers import calc_checksum, val2bytes, bytes2val

_logger = logging.getLogger("uart_reader")


class UartReader:
    """
    UartReader class.
    """

    def __init__(self, app: object,
                 sreader: uasyncio.StreamReader,
                 gga_q: primitives.queue.Queue,
                 cfg_resp_q: primitives.queue.Queue,
                 nav_pvt_q: primitives.queue.Queue,
                 ack_nack_q: primitives.queue.Queue):
        """Constructor.

        :param object app: The calling app
        :param uasyncio.StreamReader sreader: the serial connection to the GNSS Receiver(UART1)
        :param primitives.queue.Queue gga_q: queue for gga messages
        :param primitives.queue.Queue cfg_resp_q: queue for ubx responses to configuration messages
        :param primitives.queue.Queue nav_pvt_q: queue for ubx NAV-PVT get messaged
        :param primitives.queue.Queue ack_nack_q: queue for ubx ACK-NACK messages
        """

        self._app = app
        self._sreader = sreader
        self._gga_q = gga_q
        self._cfg_resp_q = cfg_resp_q
        self._nav_pvt_q = nav_pvt_q
        self._ack_nack_q = ack_nack_q

    async def run(self):
        """
        ASYNC: Read incoming data from UART1 and pass it to the corresponding queue
        """

        while True:
            byte1 = await self._sreader.read(1)
            # if not UBX, NMEA or RTCM3, discard and continue
            if byte1 not in (b"\xb5", b"\x24", b"\xd3"):
                continue
            byte2 = await self._sreader.read(1)
            bytehdr = byte1 + byte2
            # if it's an NMEA message ('$G' or '$P')
            if bytehdr in ubt.NMEA_HDR:
                # read the rest of the NMEA message from the buffer
                byten = await self._sreader.readline() # NMEA protocol is CRLF-terminated
                raw_data = bytehdr + byten
                # calculate checksum
                if not _isvalid_cksum(raw_data):
                    _logger.warn("NMEA Sentence corrupted, invalid checksum")
                    gc.collect()
                    continue
                _logger.info("nmea sentence received: " + str(raw_data))
                # if the queue is full then skip. The gga consumer needs to handle messages fast enough otherwise
                # rxBuffer will overflow
                if self._gga_q.full():
                    gc.collect()
                    continue
                await self._gga_q.put(raw_data)
            # if it's a UBX message (b'\xb5\x62')
            if bytehdr in ubt.UBX_HDR:
                msg = await self._parse_ubx(bytehdr)
                _logger.info("ubx message received: " + str(msg))
                if msg.msg_cls == b"\x05":  # ACK-ACK or ACK-NACK message
                    _logger.info("Parsed ACK/NACK Message")
                    _logger.info("msgid: " + str(msg.msg_id))
                    if self._ack_nack_q.full():
                        gc.collect()
                        continue
                    await self._ack_nack_q.put(msg)
                    gc.collect()
                if msg.msg_cls == b"\x06":  # CFG message
                    _logger.info("Parsed CFG Message")
                    _logger.info("msgid: " + str(msg.msg_id))
                    if self._cfg_resp_q.full():
                        gc.collect()
                        continue
                    await self._cfg_resp_q.put(msg)
                    gc.collect()
                if msg.msg_cls == b"\x01":  # NAV message
                    _logger.info("Parsed NAV Message")
                    _logger.info("msgid: " + str(msg.msg_id))
                    if self._cfg_resp_q.full():
                        gc.collect()
                        continue
                    await self._nav_pvt_q.put(msg)
                    gc.collect()

    async def _parse_ubx(self, hdr: bytes) -> UBXMessage:
        """
        Parse remainder of UBX message.

        :param bytes hdr: UBX header (b'\xb5\x62')
        :return: tuple of (raw_data as bytes, parsed_data as UBXMessage or None)
        :rtype: tuple
        """

        # read the rest of the UBX message from the buffer
        byten = await self._sreader.read(4)
        clsid = byten[0:1]
        msgid = byten[1:2]
        lenb = byten[2:4]
        leni = int.from_bytes(lenb, "little", False)
        byten = await self._sreader.read(leni + 2)
        plb = byten[0:leni]
        cksum = byten[leni: leni + 2]
        raw_data = hdr + clsid + msgid + lenb + plb + cksum
        parsed_data = self.parse(
            raw_data
        )
        return parsed_data

    def parse(self, message: bytes) -> UBXMessage:
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
            modestr = ["GET", "SET", "POLL"][msgmode]
            raise ube.UBXParseError(
                """Unknown message type clsid {}, msgid {}, mode {}.\n
                Check 'msgmode' keyword argument is appropriate for message category""".format(clsid, msgid, modestr)
            ) from err


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
        return "0" + final_hex
    return final_hex


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
    return content


def _calc_checksum(message: object) -> str:
    """
    Calculate checksum for raw NMEA message.

    :param object message: entire message as bytes or string
    :return: checksum as hex string
    :rtype: str
    """

    content = _get_content(message)
    cksum = 0
    for sub in content:
        cksum ^= ord(sub)
    return _int2hexstr(cksum)


def _isvalid_cksum(message: object) -> bool:
    """
    Validate raw NMEA message checksum.

    :param bytes message: entire message as bytes or string
    :return: checksum valid flag
    :rtype: bool
    """
    _, _, _, cksum = _get_parts(message)
    return cksum == _calc_checksum(message)


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
        return talker, msgid, payload, cksum
    except Exception as err:
        raise ube.NMEAMessageError(f"Badly formed message {message}") from err
