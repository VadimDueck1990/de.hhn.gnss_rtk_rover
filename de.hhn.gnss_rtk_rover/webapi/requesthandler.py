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
    def initialize(cls, app: object,  queue: Queue):
        """Initializes the RequestHandler
        Sets the necessary queues and starts the webserver

        :param object app: The calling app
        :param Queue queue: the queue with the incoming postion messages
        """

        cls._app = app
        cls._position_q = queue

        _route_handlers = [("/rate", "GET", cls._getUpdateRate),
                           ("/rate", "POST", cls._setUpdateRate)]

        srv = MicroWebSrv(routeHandlers=_route_handlers, webPath='/www/')
        srv.Start()

    @classmethod
    def _getUpdateRate(cls, http_client, http_response):
        # rate = GnssHandler.get_update_rate()
        response = {"updateRate": 200}
        print(str(response))
        http_response.WriteResponseJSONOk(response)

    @classmethod
    def _setUpdateRate(cls, http_client, http_response):
        # rate = GnssHandler.get_update_rate()
        print("set update rate triggered")
        response = http_client.ReadRequestContentAsJSON()
        print(str(response))
        http_response.WriteResponseOk()