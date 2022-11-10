"""
RequestHandler class.
Handles the web requests and manages the websocket connection
Created on 4 Sep 2022
:author: vdueck
"""
import uasyncio

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

    @classmethod
    async def initialize(cls, app: object,  queue: Queue, ntrip_stop_event: uasyncio.Event):
        """Initializes the RequestHandler
        Sets the necessary queues and starts the webserver

        :param object app: The calling app
        :param Queue queue: the queue with the incoming postion messages
        """

        cls._app = app
        cls._position_q = queue
        cls._ntrip_stop_event = ntrip_stop_event
        _route_handlers = [("/rate", "GET", cls._getUpdateRate),
                           ("/rate", "POST", cls._setUpdateRate),
                           ("/precision", "GET", cls._getPrecision),
                           ("/ntrip", "POST", cls._enableNTRIP)]

        srv = MicroWebSrv(routeHandlers=_route_handlers, webPath='/www/')
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
        response = await http_client.ReadRequestContentAsJSON()
        try:
            rate = response["updateRate"]
            result = await GnssHandler.set_update_rate(rate)
            rate = await GnssHandler.get_update_rate()
            response = {"updateRate": rate}
            await http_response.WriteResponseJSONOk(response)
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
    async def _enableNTRIP(cls, http_client, http_response):
        print("set update rate triggered")
        response = await http_client.ReadRequestContentAsJSON()
        try:
            enable = response["enable"]
            if enable == 1:
                cls._ntrip_stop_event.clear()
            if enable == 0:
                cls._ntrip_stop_event.set()
            await http_response.WriteResponseJSONOk(response)
        except Exception as ex:
            await http_response.WriteResponseJSONError(400)
