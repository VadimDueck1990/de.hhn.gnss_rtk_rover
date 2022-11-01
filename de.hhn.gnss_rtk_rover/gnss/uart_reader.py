"""
UartReader class.

Connects the ucontroller to the GNSS Receiver

Read messages from the receiver and put it on the corresponding Queue


Created on 4 Sep 2022

:author: vdueck
"""

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
                _logger.info("nmea sentence received: " + str(raw_data))
                # if the queue is full then skip. The gga consumer needs to handle messages fast enough otherwise
                # rxBuffer will overflow
                if self._gga_q.full():
                    continue
                await self._gga_q.put(raw_data)
            # if it's a UBX message (b'\xb5\x62')
            if bytehdr in ubt.UBX_HDR:
                msg = await self._parse_ubx(bytehdr)
                _logger.info("ubx message parsed: " + str(msg))

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

        msgmode = ubt.GET
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
            raise ube.UBXParseError(
                """Unknown message type clsid, msgid, mode.\n
                Check 'msgmode' keyword argument is appropriate for message category"""
            ) from err
