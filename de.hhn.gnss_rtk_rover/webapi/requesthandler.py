"""
RequestHandler class.
Handles the web requests and manages the websocket connection
Created on 4 Sep 2022
:author: vdueck
"""

import ujson
import uasyncio
import utime
from pyubx2.ubxtypes_core import FIXTYPES
from gnss.gnss_handler import GnssHandler
from webapi.microWebSrv import MicroWebSrv
from primitives.queue import Queue


class RequestHandler:
    """
    RequestHandler class.
    """

    _app = None
    _position_q = None
    _route_handlers = None
    _srv = None
    _ntrip_stop_event = None
    _rtcm_lock = None
    _last_pos = None
    _acc_interval = None

    # data cache to save on UART reads/writes
    _position_data = None

    @classmethod
    async def initialize(cls,
                         app: object,
                         queue: Queue,
                         ntrip_stop_event: uasyncio.Event,
                         rtcm_lock: uasyncio.Lock):
        """Initializes the RequestHandler
        Sets the necessary queues and starts the webserver

        :param object app: The calling app
        :param Queue queue: the queue with the incoming postion messages
        """

        cls._app = app
        cls._position_q = queue
        cls._ntrip_stop_event = ntrip_stop_event
        cls._rtcm_lock = rtcm_lock

        cls._position_data = GnssHandler.get_position()
        cls._last_pos = utime.ticks_ms()

        _route_handlers = [("/rate", "GET", cls._getUpdateRate),
                           ("/rate", "POST", cls._setUpdateRate),
                           ("/precision", "GET", cls._getPrecision),
                           ("/position", "GET", cls._getPosition),
                           ("/ntrip", "POST", cls._enableNTRIP),
                           ("/ntrip", "GET", cls._getNtripStatus),
                           ("/satsystems", "GET", cls._getSatSystems),
                           ("/satsystems", "POST", cls._setSatSystems),
                           ("/event-stream/position", "GET", cls._getPositionSSE),
                           ("/event-stream/precision", "GET", cls._getPrecisionSSE),
                           ("/event-stream/time", "GET", cls._getTime),
                           ("/event-stream/lat", "GET", cls._getLat),
                           ("/event-stream/lon", "GET", cls._getLon),
                           ("/event-stream/elev", "GET", cls._getElev),
                           ("/event-stream/fix", "GET", cls._getFixType)]

        srv = MicroWebSrv(routeHandlers=_route_handlers, webPath='/webapi/www/')
        srv.MaxWebSocketRecvLen = 256
        srv.AcceptWebSocketCallback = cls.cb_accept_ws
        await srv.Start()

    @classmethod
    async def _getUpdateRate(cls, http_client, http_response):
        try:
            rate = await GnssHandler.get_update_rate()
            response = {"updateRate": rate}
            await http_response.WriteResponseJSONOk(response)
        except Exception as ex:
            await http_response.WriteResponseJSONError(400)

    @classmethod
    async def _setUpdateRate(cls, http_client, http_response):
        print("set update rate triggered")
        payload = await http_client.ReadRequestContentAsJSON()
        try:
            rate = payload["updateRate"]
            result = await GnssHandler.set_update_rate(rate)
            await http_response.WriteResponseOk()
        except Exception as ex:
            await http_response.WriteResponseJSONError(400)

    @classmethod
    async def _getPrecision(cls, http_client, http_response):
        try:
            hAcc, vAcc = await GnssHandler.get_precision()
            response = {"hAcc": hAcc, "vAcc": vAcc}
            await http_response.WriteResponseJSONOk(response)
        except Exception as ex:
            await http_response.WriteResponseJSONError(400)

    @classmethod
    async def _getPrecisionSSE(cls, http_client, http_response):
        try:
            hAcc, vAcc = await GnssHandler.get_precision()
            precision = {"hAcc": hAcc, "vAcc": vAcc}
            data = ujson.dumps(precision)
        except Exception:
            data = "Attempting to get data from receiver..."
        await http_response.WriteResponseOk(headers=({'Cache-Control': 'no-cache'}),
                                            contentType='text/event-stream',
                                            contentCharset='UTF-8',
                                            content='data: {0}\n\n'.format(data))

    @classmethod
    async def _enableNTRIP(cls, http_client, http_response):
        payload = await http_client.ReadRequestContentAsJSON()
        try:
            enable = payload["enable"]
            if enable == 1:
                cls._ntrip_stop_event.clear()
            if enable == 0:
                cls._ntrip_stop_event.set()
            await http_response.WriteResponseOk()
        except Exception as ex:
            await http_response.WriteResponseJSONError(400)

    @classmethod
    async def _getSatSystems(cls, http_client, http_response):
        try:
            sat_systems = await GnssHandler.get_satellite_systems()
            await http_response.WriteResponseJSONOk(sat_systems)
        except Exception as ex:
            await http_response.WriteResponseJSONError(400)

    @classmethod
    async def _setSatSystems(cls, http_client, http_response):
        payload = await http_client.ReadRequestContentAsJSON()
        try:
            gps = payload["gps"]
            glo = payload["glo"]
            gal = payload["gal"]
            bds = payload["bds"]
            resume_ntrip = False
            if not cls._ntrip_stop_event.is_set():  # if ntrip was running, stop ntrip and set a flag
                cls._ntrip_stop_event.set()
                resume_ntrip = True
            result = await GnssHandler.set_satellite_systems(gps, gal, glo, bds)
            await http_response.WriteResponseOk()
            if resume_ntrip:  # if flag was set, resume ntrip
                cls._ntrip_stop_event.clear()
        except Exception as ex:
            await http_response.WriteResponseJSONError(400)

    @classmethod
    async def _getNtripStatus(cls, http_client, http_response):
        try:
            enabled = None
            async with cls._rtcm_lock:
                if GnssHandler.rtcm_enabled:
                    enabled = True
                else:
                    enabled = False
            response = {"enabled": enabled}
            await http_response.WriteResponseJSONOk(response)
        except Exception as ex:
            await http_response.WriteResponseJSONError(400)

    @classmethod
    async def _getPosition(cls, http_client, http_response):
        try:
            position = await GnssHandler.get_position()
            await http_response.WriteResponseJSONOk(position)
        except Exception as ex:
            await http_response.WriteResponseJSONError(400)

    @classmethod
    async def _getPositionSSE(cls, http_client, http_response):
        try:
            if utime.ticks_diff(utime.ticks_ms(), cls._last_pos) > 5000:
                print("difference: " + str(utime.ticks_diff(utime.ticks_ms(), cls._last_pos)))
                print("polling new position data")
                cls._position_data = await GnssHandler.get_position()
                cls._last_pos = utime.ticks_ms()
            position = ujson.dumps(cls._position_data)
        except Exception:
            position = "Attempting to get data from receiver..."
        await http_response.WriteResponseOk(headers=({'Cache-Control': 'no-cache'}),
                                            contentType='text/event-stream',
                                            contentCharset='UTF-8',
                                            content='data: {0}\n\n'.format(position))
    @classmethod
    async def _getTime(cls, http_client, http_response):
        try:
            if utime.ticks_diff(utime.ticks_ms(), cls._last_pos) > 5000:
                print("difference: " + str(utime.ticks_diff(utime.ticks_ms(), cls._last_pos)))
                print("polling new position data")
                cls._position_data = await GnssHandler.get_position()
                cls._last_pos = utime.ticks_ms()
            time = cls._position_data["time"]
        except Exception:
            time = "Attempting to get data from receiver..."
        await http_response.WriteResponseOk(headers = ({'Cache-Control': 'no-cache'}),
                                            contentType = 'text/event-stream',
                                            contentCharset = 'UTF-8',
                                            content = 'data: {0}\n\n'.format(time))

    @classmethod
    async def _getLat(cls, http_client, http_response):
        try:
            lat = cls._position_data["lat"]
        except Exception:
            lat = "Attempting to get data from receiver..."
        await http_response.WriteResponseOk(headers=({'Cache-Control': 'no-cache'}),
                                            contentType='text/event-stream',
                                            contentCharset='UTF-8',
                                            content='data: {0}\n\n'.format(lat))

    @classmethod
    async def _getLon(cls, http_client, http_response):
        try:
            lon = cls._position_data["lon"]
        except Exception:
            lon = "Attempting to get data from receiver..."
        await http_response.WriteResponseOk(headers=({'Cache-Control': 'no-cache'}),
                                            contentType='text/event-stream',
                                            contentCharset='UTF-8',
                                            content='data: {0}\n\n'.format(lon))

    @classmethod
    async def _getElev(cls, http_client, http_response):
        try:
            elev = cls._position_data["elev"]
        except Exception:
            elev = "Attempting to get data from receiver..."
        await http_response.WriteResponseOk(headers=({'Cache-Control': 'no-cache'}),
                                            contentType='text/event-stream',
                                            contentCharset='UTF-8',
                                            content='data: {0}\n\n'.format(elev))

    @classmethod
    async def _getFixType(cls, http_client, http_response):
        try:
            fixtype = cls._position_data["fixType"]
            fixtype_string = FIXTYPES[int(fixtype)]
        except Exception:
            fixtype_string = "Attempting to get data from receiver..."
        await http_response.WriteResponseOk(headers=({'Cache-Control': 'no-cache'}),
                                            contentType='text/event-stream',
                                            contentCharset='UTF-8',
                                            content='data: {0}\n\n'.format(fixtype_string))

    # Websocket
    #--------------------------------------------------------------------------------------------

    @classmethod
    async def cb_receive_text(cls, webSocket, msg):
        print("WS RECV TEXT : %s" % msg)
        await webSocket.SendText("Reply for %s" % msg)

    @classmethod
    async def cb_receive_binary(cls, webSocket, data):
        print("WS RECV DATA : %s" % data)
        await uasyncio.sleep(1)

    @classmethod
    async def cb_closed(cls, webSocket):
        print("WS CLOSED")
        await uasyncio.sleep(1)

    @classmethod
    async def cb_send_position(cls, websocket):

        position = await GnssHandler.get_position() # Store data in dict
        await websocket.SendText(str(ujson.dumps(position)))  # Convert data to JSON and send

    @classmethod
    async def cb_accept_ws(cls, webSocket, httpClient):
        print("WS ACCEPT")
        webSocket.RecvTextCallback = cls.cb_receive_text
        webSocket.RecvBinaryCallback = cls.cb_receive_binary
        webSocket.ClosedCallback = cls.cb_closed
        while not webSocket.IsClosed():
            await cls.cb_send_position(webSocket)
