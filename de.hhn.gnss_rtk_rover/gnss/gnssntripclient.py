"""
NTRIP Client class

Transmits client position from ZED-F9P to NTRIP caster
at specified interval
Retrievessourcetable and RTCM3
correction data from NTRIP caster and sending the
correction data to the ZED-F9P over UART

Created on 10 Oct 2022

:author: vdueck
"""
import primitives.queue
from pyubx2.ubxreader import UBXReader
import binascii
import uasyncio
from uasyncio import Event
from machine import UART
import time
from primitives.queue import Queue
import usocket
from pyubx2.ubxtypes_core import RTCM3_PROTOCOL, ERR_IGNORE
from pyubx2.exceptions import (
    RTCMParseError,
    RTCMMessageError,
    RTCMTypeError,
)
import utils.logging as logging
from utils.globals import (
    DEFAULT_BUFSIZE,
    NOGGA,
    OUTPORT_NTRIP,
    NTRIP_USER,
    NTRIP_PW,
    NTRIP_SERVER,
    MOUNTPOINT,
    GGA_INTERVAL,
    REF_LAT,
    REF_LON,
    REF_ALT,
)

# from gnss.helpers import find_mp_distance

TIMEOUT = 10
VERSION = "0.1.0"
USERAGENT = f"HHN BW NTRIP Client/{VERSION}"
NTRIP_HEADERS = {
    "Ntrip-Version": "Ntrip/2.0",
    "User-Agent": USERAGENT,
}
FIXES = {
    "3D": 1,
    "2D": 2,
    "RTK FIXED": 4,
    "RTK FLOAT": 5,
    "RTK": 5,
    "DR": 6,
    "NO FIX": 0,
}
GGALIVE = 0
GGAFIXED = 1

_logger = logging.getLogger("ntrip_client")


class GNSSNTRIPClient:
    """
    NTRIP client class.
    """

    def __init__(self,
                 rtcmoutput: UART,
                 app: object,
                 gga_q: primitives.queue.Queue,
                 stopevent: uasyncio.Event,
                 ggaevent: uasyncio.Event):
        """
        Constructor.

        :param object app: application from which this class is invoked (None)
        :param object rtcmoutput: UART connection for rtcm data to ZED-F9P
        """
        print("ntrip begin init" + str(time.ticks_ms()))
        self.__app = app  # Reference to calling application class (if applicable)
        self._ntripqueue = Queue()
        self._socket = None
        self._swriter = None
        self._sreader = None
        self._read_task = None
        self._connected = False
        self._stopevent = stopevent
        self._read_gga_event = ggaevent
        self._output = uasyncio.StreamWriter(rtcmoutput)
        self._validargs = False
        self._last_gga = time.ticks_ms()
        self._gga_queue = gga_q
        self._first_start = True

        # persist settings to allow any calling app to retrieve them
        self._settings = {
            "server": "",
            "port": "2101",
            "mountpoint": "",
            "distance": "",
            "version": "2.0",
            "user": "anon",
            "password": "password",
            "ggainterval": "None",
            "sourcetable": [],
            "reflat": "",
            "reflon": "",
            "refalt": "",
            "refsep": "",
        }
        print("ntrip end init" + str(time.ticks_ms()))

    def __enter__(self):
        """
        Context manager enter routine.
        """

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        Context manager exit routine.
        """

        # self.stop()

    @property
    def settings(self):
        """
        Getter for NTRIP settings.
        """

        return self._settings

    @property
    def connected(self):
        """
        Connection status getter.
        """

        return self._connected

    async def run(self):
        print("ntrip begin run " + str(time.ticks_ms()))
        """
        Open NTRIP server connection.

        If calling application implements a "get_coordinates" method to
        obtain live coordinates (i.e. from GNSS receiver), the method will
        use these instead of fixed reference coordinates.

        User login credentials can be obtained from environment variables
        NTRIP_USER and NTRIP_PASSWORD, or passed as kwargs.

        :param str server: NTRIP server URL ("")
        :param int port: NTRIP port (2101)
        :param str mountpoint: NTRIP mountpoint ("", leave blank to get sourcetable)
        :param str version: NTRIP protocol version ("2.0")
        :param str user: login user ("anon" or env variable NTRIP_USER)
        :param str password: login password ("password" or env variable NTRIP_PASSWORD)
        :param int ggainterval: GGA sentence transmission interval (-1 = None)
        :param str reflat: reference latitude ("")
        :param str reflon: reference longitude ("")
        :param str refalt: reference altitude ("")
        :param str refsep: reference separation ("")
        :param object output: writeable output medium (serial, file, socket, queue) (None)
        :returns: boolean flag 0 = terminated, 1 = Ok to stream RTCM3 data from server
        :rtype: bool
        """

        self._settings["server"] = NTRIP_SERVER
        self._settings["port"] = int(OUTPORT_NTRIP)
        self._settings["mountpoint"] = mountpoint = MOUNTPOINT
        self._settings["version"] = "2.0"
        self._settings["user"] = NTRIP_USER
        self._settings["password"] = NTRIP_PW
        self._settings["ggainterval"] = int(GGA_INTERVAL * 1000)
        self._settings["reflat"] = REF_LAT
        self._settings["reflon"] = REF_LON
        self._settings["refalt"] = REF_ALT
        self._settings["refsep"] = ""
        self._validargs = True
        self._connected = True
        while self._stopevent.is_set():
            await uasyncio.sleep_ms(500)
        print("ntrip end run " + str(time.ticks_ms()))
        _logger.info("STARTING NTRIP READING TASK")
        await self._reading_task(self._settings, self._stopevent, self._output)

    def _app_update_status(self, status: bool, msg: tuple = None):
        """
        THREADED
        Update NTRIP connection status in calling application.

        :param bool status: NTRIP server connection status
        :param tuple msg: optional (message, color)
        """

        if hasattr(self.__app, "update_ntrip_status"):
            self.__app.update_ntrip_status(status, msg)

    @staticmethod
    def _formatGET(settings: dict) -> bytes:
        """
        THREADED
        Format HTTP GET Request.

        :param dict settings: settings dictionary
        :return: formatted HTTP GET request
        :rtype: str
        """

        host = f"{settings['server']}:{settings['port']}"
        mountpoint = settings["mountpoint"]
        version = settings["version"]
        user = settings["user"]
        password = settings["password"]

        mountpoint = "/" + mountpoint  # sourcetable request
        user = user + ":" + password
        user = bytes(user, 'utf-8')
        user = binascii.b2a_base64(user)

        reqline1 = f"GET {mountpoint} HTTP/1.1\r\n"
        reqline2 = f"User-Agent: {USERAGENT}\r\n"
        reqline3 = f"Host: {host}\r\n"
        reqline4 = f"Authorization: Basic {user.decode('utf-8')}\r\n"
        reqline5 = f"Ntrip-Version: Ntrip/{version}\r\n"
        req = reqline1 + reqline2 + reqline3 + reqline4 + reqline5 + "\r\n"  # NECESSARY!!!
        return bytes(req, 'utf-8')

    #     # lat, lon, alt, sep = self._app_get_coordinates()

    async def _send_GGA(self, ggainterval: int, output: uasyncio.StreamWriter):
        """
        THREADED
        Send NMEA GGA sentence to NTRIP server at prescribed interval.
        """
        diff = time.ticks_diff(self._last_gga, time.ticks_ms())
        # _logger.info("difference: " + str(diff))
        if time.ticks_diff(time.ticks_ms(), self._last_gga) > ggainterval or self._first_start:
            # _logger.info("parsing gga, time interval passed")
            self._read_gga_event.set()
            raw_data = await self._gga_queue.get()
            self._read_gga_event.clear()
            if raw_data is not None:
                # _logger.info("sending gga to caster...: " + str(raw_data))
                await uasyncio.sleep_ms(10)
                self._socket.sendall(raw_data)
                await self._do_write(output, raw_data)
                print("Sending gga to caster: " + str(raw_data))
            self._last_gga = time.ticks_ms()
            self._first_start = False
        await uasyncio.sleep_ms(1)

    async def _reading_task(
        self,
        settings: dict,
        stopevent: Event,
        output: uasyncio.StreamWriter,
    ):
        """
        THREADED
        Opens socket to NTRIP server and reads incoming data.

        :param dict settings: settings as dictionary
        :param Event stopevent: stop event
        :param uasyncio.StreamWriter output: output stream for RTCM3 data
        """

        # try:
        _logger.info("inside ntrip reading task")
        server = settings["server"]
        port = int(settings["port"])
        mountpoint = settings["mountpoint"]
        ggainterval = int(settings["ggainterval"])

        # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self._socket:
        self._socket = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
        self._socket.settimeout(TIMEOUT)
        addr = usocket.getaddrinfo(server, port)[0][-1]
        self._socket.connect(addr)
        msg = self._formatGET(settings)
        print(str(msg))
        self._swriter = uasyncio.StreamWriter(self._socket)
        self._sreader = uasyncio
        self._socket.sendall(msg)
        # send GGA sentence with request
        if mountpoint != "":
            await self._send_GGA(ggainterval, output)
        while not stopevent.is_set():
            await self._do_data(self._socket, stopevent, ggainterval, output)
        # except (
        #     socket.gaierror,
        #     ConnectionRefusedError,
        #     ConnectionAbortedError,
        #     ConnectionResetError,
        #     BrokenPipeError,
        #     TimeoutError,
        #     OverflowError,
        # ):
        #     stopevent.set()
        #     self._connected = False

    async def _do_data(
        self, sock: usocket, stopevent: Event, ggainterval: int, output: uasyncio.StreamWriter
    ):
        """
        ASYNC
        Read and parse incoming NTRIP RTCM3 data stream.

        :param socket sock: socket
        :param Event stopevent: stop event
        :param int ggainterval: GGA transmission interval seconds
        :param uasyncio.StreamWriter output: output stream for RTCM3 messages
        """
        print("ntrip begin do_data " + str(time.ticks_ms()))
        # UBXReader will wrap socket as SocketStream
        ubr = UBXReader(
            sock,
            protfilter=RTCM3_PROTOCOL,
            quitonerror=ERR_IGNORE,
            bufsize=DEFAULT_BUFSIZE,
            labelmsm=True,
        )

        while not stopevent.is_set():
            try:
                print("start ubr.read: " + str(time.ticks_ms()))
                await uasyncio.sleep_ms(10)
                raw_data, parsed_data = await ubr.read()
                print("end ubr.read: " + str(time.ticks_ms()))
                if raw_data is not None:
                    await self._do_write(output, raw_data)
                await self._send_GGA(ggainterval, output)
            except (
                RTCMMessageError,
                RTCMParseError,
                RTCMTypeError,
            ) as err:
                _logger.exc(err, "Error parsing rtcm stream")
                continue

    async def _do_write(self, output: uasyncio.StreamWriter, raw: bytes):
        """
        ASYNC
        Send RTCM3 data to designated output medium.


        :param uasyncio.Streamwriter output: writeable output medium for RTCM3 data
        :param bytes raw: raw data
        """
        await uasyncio.sleep_ms(10)
        output.write(raw)
        await output.drain()



