"""
UBXReader class.

Reads and parses individual UBX, NMEA or RTCM3 messages from any stream
which supports a read(n) -> bytes method.

Returns both the raw binary data (as bytes) and the parsed data
(as a UBXMessage, NMEAMessage or RTCMMessage object).

'protfilter' governs which protocols (NMEA, UBX or RTCM3) are processed
'quitonerror' governs how errors are handled

Created on 2 Oct 2020

:author: semuadmin
:copyright: SEMU Consulting © 2020
:license: BSD 3-Clause
"""

import uasyncio
import pyubx2.ubxtypes_core as ubt
import pyubx2.exceptions as ube


class UBXReader:
    """
    UBXReader class.
    """

    def __init__(self, datastream: uasyncio.StreamReader, **kwargs):
        """Constructor.

        :param datastream stream: input data stream
        :param int quitonerror: (kwarg) 0 = ignore errors,  1 = log errors and continue, 2 = (re)raise errors (1)
        :param int protfilter: (kwarg) protocol filter 1 = NMEA, 2 = UBX, 4 = RTCM3 (3)
        :param int validate: (kwarg) 0 = ignore invalid checksum, 1 = validate checksum (1)
        :param int msgmode: (kwarg) 0=GET, 1=SET, 2=POLL (0)
        :param bool parsebitfield: (kwarg) 1 = parse bitfields, 0 = leave as bytes (1)
        :param bool scaling: (kwarg) 1 = apply scale factors, 0 = do not apply (1)
        :param bool labelmsm: (kwarg) whether to label RTCM3 MSM NSAT and NCELL attributes (1)
        :param int bufsize: (kwarg) socket recv buffer size (1024)
        :raises: UBXStreamError (if mode is invalid)

        """

        self._stream = datastream
        self._protfilter = int(
            kwargs.get("protfilter", ubt.NMEA_PROTOCOL | ubt.UBX_PROTOCOL)
        )
        self._quitonerror = int(kwargs.get("quitonerror", ubt.ERR_LOG))
        self._validate = int(kwargs.get("validate", ubt.VALCKSUM))
        self._parsebf = int(kwargs.get("parsebitfield", True))
        self._scaling = int(kwargs.get("scaling", True))
        self._labelmsm = int(kwargs.get("labelmsm", True))
        self._msgmode = int(kwargs.get("msgmode", 0))

        if self._msgmode not in (0, 1, 2):
            raise ube.UBXStreamError(
                f"Invalid stream mode {self._msgmode} - must be 0, 1 or 2"
            )

    def __iter__(self):
        """Iterator."""

        return self

    def __next__(self) -> tuple:
        """
        Return next item in iteration.

        :return: tuple of (raw_data as bytes, parsed_data as UBXMessage)
        :rtype: tuple
        :raises: StopIteration

        """

        (raw_data, parsed_data) = self.read()
        if raw_data is not None:
            return raw_data, parsed_data
        raise StopIteration

    async def read(self) -> bytes:
        """
        Read a single NMEA, UBX or RTCM3 message from the stream buffer
        and return both raw and parsed data.

        'protfilter' determines which protocols are parsed.
        'quitonerror' determines whether to raise, log or ignore parsing errors.

        :return: tuple of (raw_data as bytes, parsed_data as UBXMessage, NMEAMessage or RTCMMessage)
        :rtype: tuple
        :raises: UBXStreamError (if unrecognised protocol in data stream)
        """

        parsing = True

        try:
            while parsing:  # loop until end of valid message or EOF
                raw_data = None
                byte1 = await self._read_bytes(1)  # read the first byte
                # if not UBX, NMEA or RTCM3, discard and continue
                if byte1 not in (b"\xb5", b"\x24", b"\xd3"):
                    continue
                byte2 = await self._read_bytes(1)
                bytehdr = byte1 + byte2
                if byte1 == b"\xd3" and (byte2[0] & ~0x03) == 0:
                    raw_data = await self._read_rtcm3(bytehdr)
                    # if protocol filter passes RTCM, return message,
                    # otherwise discard and continue
                    # if self._protfilter & ubt.RTCM3_PROTOCOL:
                    parsing = False
                    # else:
                    #     continue
                # unrecognised protocol header
                else:
                    if self._quitonerror == ubt.ERR_RAISE:
                        raise ube.UBXStreamError("Unknown protocol {}.".format(bytehdr))
                    if self._quitonerror == ubt.ERR_LOG:
                        return bytehdr
                    continue

        except EOFError:
            return None

        return raw_data

    async def _read_rtcm3(self, hdr: bytes, **kwargs) -> bytes:
        """
        Parse any RTCM3 data in the stream (using pyrtcm library).

        :param bytes hdr: first 2 bytes of RTCM3 header
        :param bool validate: (kwarg) validate crc Y/N
        :return: tuple of (raw_data as bytes, parsed_stub as RTCMMessage)
        :rtype: tuple
        """

        hdr3 = await self._read_bytes(1)
        size = hdr3[0] | (hdr[1] << 8)
        payload = await self._read_bytes(size)
        crc = await self._read_bytes(3)
        raw_data = hdr + hdr3 + payload + crc
        return raw_data

    async def _read_bytes(self, size: int) -> bytes:
        """
        Read a specified number of bytes from stream.

        :param int size: number of bytes to read
        :return: bytes
        :rtype: bytes
        :raises: EOFError if stream ends prematurely
        """

        data = await self._stream.read(size)
        if len(data) < size:  # EOF
            raise EOFError()
        return data

    @property
    def datastream(self) -> object:
        """
        Getter for stream.
        :return: data stream
        :rtype: object
        """
        return self._stream
