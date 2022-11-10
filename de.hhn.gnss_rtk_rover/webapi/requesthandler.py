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

    @classmethod
    async def initialize(cls, app: object,  queue: Queue):
        """Initializes the RequestHandler
        Sets the necessary queues and starts the webserver

        :param object app: The calling app
        :param Queue queue: the queue with the incoming postion messages
        """

        cls._app = app
        cls._position_q = queue

        _route_handlers = [("/rate", "GET", _getUpdateRate),
                           ("/rate", "POST", _setUpdateRate),
                           ("/precision", "GET", _getPrecision)]

        srv = MicroWebSrv(routeHandlers=_route_handlers, webPath='/www/')
        await srv.Start()


async def _setUpdateRate(http_client, http_response):
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


async def _getUpdateRate(http_client, http_response):
    try:
        rate = await GnssHandler.get_update_rate()
        response = {"updateRate": rate}
        await http_response.WriteResponseJSONOk(response)
    except Exception as ex:
        await http_response.WriteResponseJSONError(400)


async def _getPrecision(http_client, http_response):
    try:
        hAcc, vAcc = await GnssHandler.get_precision()
        response = {"hAcc": hAcc, "vAcc": vAcc}
        await http_response.WriteResponseJSONOk(response)
    except Exception as ex:
        await http_response.WriteResponseJSONError(400)
