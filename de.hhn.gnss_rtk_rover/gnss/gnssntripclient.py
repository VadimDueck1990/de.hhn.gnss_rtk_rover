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
from pyubx2.ubxreader import UBXReader
import binascii
import uasyncio
from uasyncio import Event
from machine import UART
import time
from primitives.queue import Queue
import socket
from pyubx2.ubxtypes_core import RTCM3_PROTOCOL, ERR_IGNORE
from pyubx2.exceptions import (
    RTCMParseError,
    RTCMMessageError,
    RTCMTypeError,
)
from pynmeagps import NMEAMessage, GET
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

from gnss.helpers import find_mp_distance

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

_logger = logging.getLogger("app_manager")


class GNSSNTRIPClient:
    """
    NTRIP client class.
    """

    def __init__(self, rtcmoutput: UART, app=None):
        """
        Constructor.

        :param object app: application from which this class is invoked (None)
        :param object rtcmoutput: UART connection for rtcm data to ZED-F9P
        """

        self.__app = app  # Reference to calling application class (if applicable)
        self._ntripqueue = Queue()
        self._socket = None
        self._read_task = None
        self._connected = False
        self._stopevent = Event()
        self._output = uasyncio.StreamWriter(rtcmoutput)
        self._validargs = False
        self._last_gga = time.ticks_ms()

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
            "ggamode": GGALIVE,
            "sourcetable": [],
            "reflat": "",
            "reflon": "",
            "refalt": "",
            "refsep": "",
        }

    def __enter__(self):
        """
        Context manager enter routine.
        """

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        Context manager exit routine.
        """

        self.stop()

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

    async def run(self) -> bool:
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
        :param int ggamode: GGA pos source; 0 = live from receiver, 1 = fixed reference (0)
        :param str reflat: reference latitude ("")
        :param str reflon: reference longitude ("")
        :param str refalt: reference altitude ("")
        :param str refsep: reference separation ("")
        :param object output: writeable output medium (serial, file, socket, queue) (None)
        :returns: boolean flag 0 = terminated, 1 = Ok to stream RTCM3 data from server
        :rtype: bool
        """
        # pylint: disable=unused-variable

        # try:
        # self._settings["server"] = server = kwargs.get("server", NTRIP_SERVER)
        # self._settings["port"] = port = int(kwargs.get("port", OUTPORT_NTRIP))
        # self._settings["mountpoint"] = mountpoint = kwargs.get("mountpoint", MOUNTPOINT)
        # self._settings["version"] = kwargs.get("version", "2.0")
        # self._settings["user"] = kwargs.get("user", user)
        # self._settings["password"] = kwargs.get("password", password)
        # self._settings["ggainterval"] = int(kwargs.get("ggainterval", NOGGA))
        # self._settings["ggamode"] = int(kwargs.get("ggamode", GGALIVE))
        # self._settings["reflat"] = kwargs.get("reflat", REF_LAT)
        # self._settings["reflon"] = kwargs.get("reflon", REF_LON)
        # self._settings["refalt"] = kwargs.get("refalt", REF_ALT)
        # self._settings["refsep"] = kwargs.get("refsep", "")

        self._settings["server"] = NTRIP_SERVER
        self._settings["port"] = int(OUTPORT_NTRIP)
        self._settings["mountpoint"] = mountpoint = MOUNTPOINT
        self._settings["version"] = "2.0"
        self._settings["user"] = NTRIP_USER
        self._settings["password"] = NTRIP_PW
        self._settings["ggainterval"] = int(GGA_INTERVAL * 1000)
        self._settings["ggamode"] = int(GGALIVE)
        self._settings["reflat"] = REF_LAT
        self._settings["reflon"] = REF_LON
        self._settings["refalt"] = REF_ALT
        self._settings["refsep"] = ""

        # if server == "":
        #     raise ParameterError(f"Invalid server url {server}")
        # if port > MAXPORT or port < 1:
        #     raise ParameterError(f"Invalid port {port}")

        # except (ParameterError, ValueError, TypeError) as err:
        #     self._do_log(
        #         f"Invalid input arguments bla\n{err}\n"
        #         + "Type gnssntripclient -h for help.",
        #         VERBOSITY_LOW,
        #     )
        #     self._validargs = False

        self._validargs = True
        self._connected = True
        if self._validargs:
            await self._start_read_task(
                self._settings,
                self._stopevent,
                self._output,
            )
            if mountpoint != "":
                return False
        return True

    def stop(self):
        """
        Close NTRIP server connection.
        """

        self._stop_read_task()
        self._connected = False

    def _app_update_status(self, status: bool, msg: tuple = None):
        """
        THREADED
        Update NTRIP connection status in calling application.

        :param bool status: NTRIP server connection status
        :param tuple msg: optional (message, color)
        """

        if hasattr(self.__app, "update_ntrip_status"):
            self.__app.update_ntrip_status(status, msg)

    def _app_get_coordinates(self) -> tuple:
        """
        THREADED
        Get live coordinates from receiver, or use fixed
        reference position, depending on ggamode setting.

        :returns: tuple of (lat, lon, alt, sep)
        :rtype: tuple
        """
        print("inside app_get_coordinates")

        lat = lon = alt = sep = ""
        if self._settings["ggamode"] == GGAFIXED:  # Fixed reference position
            lat = self._settings["reflat"]
            lon = self._settings["reflon"]
            alt = self._settings["refalt"]
            sep = self._settings["refsep"]
        elif hasattr(self.__app, "get_coordinates"):  # live position from receiver
            _, lat, lon, alt, sep = self.__app.get_coordinates()

        return lat, lon, alt, sep

    def _app_notify(self):
        """
        THREADED
        If calling app is tkinter, generate event
        to notify app that data is available
        """

        if hasattr(self.__app, "appmaster"):
            if hasattr(self.__app.appmaster, "event_generate"):
                self.__app.appmaster.event_generate("<<ntrip_read>>")

    @staticmethod
    def _formatGET(settings: dict) -> str:
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
        reqline4 = f"Authorization: Basic {user.decode(encoding='utf-8')}\r\n"
        reqline5 = f"Ntrip-Version: Ntrip/{version}\r\n"
        req = reqline1 + reqline2 + reqline3 + reqline4 + reqline5 + "\r\n"  # NECESSARY!!!
        return bytes(req, 'utf-8')

    def _formatGGA(self) -> tuple:
        """
        THREADED
        Format NMEA GGA sentence using pynmeagps. The raw string
        output is suitable for sending to an NTRIP socket.

        :return: tuple of (raw NMEA message as bytes, NMEAMessage)
        :rtype: tuple
        """
        # time will default to current UTC

        # try:

        # lat, lon, alt, sep = self._app_get_coordinates()
        lat = float(50.3902802)
        lon = float(7.3161048)
        alt = float(269.9)
        sep = float(46.9)
        NS = "N"
        EW = "E"
        if lat < 0:
            NS = "S"
        if lon < 0:
            EW = "W"

        parsed_data = NMEAMessage(
            "GP",
            "GGA",
            GET,
            lat=lat,
            NS=NS,
            lon=lon,
            EW=EW,
            quality=1,
            numSV=15,
            HDOP=0,
            alt=alt,
            altUnit="M",
            sep=sep,
            sepUnit="M",
            diffAge="",
            diffStation=0,
        )

        raw_data = parsed_data.serialize()
        print(str(raw_data))
        print(str(parsed_data))
        return raw_data, parsed_data

        # except ValueError:
        #     return None, None

    async def _send_GGA(self, ggainterval: int, output: uasyncio.StreamWriter):
        """
        THREADED
        Send NMEA GGA sentence to NTRIP server at prescribed interval.
        """
        if ggainterval != NOGGA:
            _logger.info("inside _send_gga livegga")
            if time.ticks_diff(self._last_gga, time.ticks_ms()) > ggainterval:
                _logger.info("parsing gga, time interval passed")
                print("parsing gga")
                raw_data, parsed_data = self._formatGGA()
                if parsed_data is not None:
                    _logger.info("sending gga to caster...: " + str(raw_data))
                    self._socket.sendall(raw_data)
                    await self._do_write(output, raw_data)
                self._last_gga = time.ticks_ms()

    def _get_closest_mountpoint(self):
        """
        THREADED
        Find closest mountpoint in sourcetable
        if valid reference lat/lon are available.
        """

        try:

            lat, lon, _, _ = self._app_get_coordinates()
            closest_mp, dist = find_mp_distance(
                float(lat), float(lon), self._settings["sourcetable"]
            )
            if self._settings["mountpoint"] == "":
                self._settings["mountpoint"] = closest_mp
            msg = "Closest mountpoint to reference location ({}, {}) = {}, {} km".format(lat, lon, closest_mp, dist)
            _logger.info(msg)

        except ValueError:
            pass

    async def _start_read_task(
        self,
        settings: dict,
        stopevent: Event,
        output: uasyncio.StreamWriter,
    ):
        """
        Start the NTRIP reader task.
        """

        if self._connected:
            self._stopevent.clear()
            self._read_task = uasyncio.create_task(self._reading_task(settings, stopevent, output))

    def _stop_read_task(self):
        """
        Stop NTRIP reader thread.
        """

        if self._read_task is not None:
            self._stopevent.set()
            self._read_task.cancel()

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

        try:

            server = settings["server"]
            port = int(settings["port"])
            mountpoint = settings["mountpoint"]
            ggainterval = int(settings["ggainterval"])

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self._socket:
                self._socket.settimeout(TIMEOUT)
                self._socket.connect((server, port))
                self._socket.sendall(self._formatGET(settings))
                # send GGA sentence with request
                if mountpoint != "":
                    await self._send_GGA(ggainterval, output)
                while not stopevent.is_set():
                    rc = self._do_header(self._socket, stopevent)
                    if rc == "0":  # streaming RTMC3 data from mountpoint
                        _logger.info("Using mountpoint" + str(mountpoint))
                        await self._do_data(self._socket, stopevent, ggainterval, output)
                    elif rc == "1":  # retrieved sourcetable
                        stopevent.set()
                        self._connected = False
                        self._app_update_status(False)
                    else:  # error message
                        stopevent.set()
                        self._connected = False
                        self._app_update_status(False, (f"Error!: {rc}", "red"))
        except (
            socket.gaierror,
            ConnectionRefusedError,
            ConnectionAbortedError,
            ConnectionResetError,
            BrokenPipeError,
            TimeoutError,
            OverflowError,
        ):
            stopevent.set()
            self._connected = False

    async def _do_header(self, sock: socket, stopevent: Event) -> str:
        """
        THREADED
        Parse response header lines.

        :param socket sock: socket
        :param Event stopevent: stop event
        :return: return status or error message
        :rtype: str
        """

        stable = []
        data = "Initial Header"

        while data and not stopevent.is_set():
            try:

                data = sock.recv(DEFAULT_BUFSIZE)
                header_lines = data.decode(encoding="utf-8").split("\r\n")
                for line in header_lines:
                    # if sourcetable request, populate list
                    if line.find("STR;") >= 0:  # sourcetable entry
                        strbits = line.split(";")
                        if strbits[0] == "STR":
                            strbits.pop(0)
                            stable.append(strbits)
                    elif line.find("ENDSOURCETABLE") >= 0:  # end of sourcetable
                        self._settings["sourcetable"] = stable
                        self._get_closest_mountpoint()
                        _logger.info("Complete sourcetable follows...\n")
                        for lines in self._settings["sourcetable"]:
                            _logger.info(str(lines))
                        return "1"
                    elif (  # HTTP error code
                        line.find("400 Bad Request") >= 0
                        or line.find("401 Unauthorized") >= 0
                        or line.find("403 Forbidden") >= 0
                        or line.find("404 Not Found") >= 0
                        or line.find("405 Method Not Allowed") >= 0
                    ):
                        _logger.error(str(line))
                        return line
                    elif line == "":
                        break

            except UnicodeDecodeError:
                data = False

        return "0"

    async def _do_data(
        self, sock: socket, stopevent: Event, ggainterval: int, output: uasyncio.StreamWriter
    ):
        """
        ASYNC
        Read and parse incoming NTRIP RTCM3 data stream.

        :param socket sock: socket
        :param Event stopevent: stop event
        :param int ggainterval: GGA transmission interval seconds
        :param uasyncio.StreamWriter output: output stream for RTCM3 messages
        """

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

                raw_data, parsed_data = ubr.read()
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
        _logger.info("writing over uart2 to ZED. Data:" + str(raw))
        output.write(raw)
        await output.drain()



