"""
AppManager class.

Main class, which manages and synchronizes all modules.

Manages Wi-Fi, NTRIP-CLient, serial communication and WebServer


Created on 4 Sep 2022

:author: vdueck
"""

import uasyncio
from uasyncio import Event
import utils.logging as logging
from utils.wifimanager import WiFiManager
from gnss.gnssntripclient import GNSSNTRIPClient
from utils.globals import (
    WIFI_SSID,
    WIFI_PW,
    WIFI_CHECK_TIME,
)

_logger = logging.getLogger("app_manager")


class AppManager:
    """
    AppManager class.
    """

    def __init__(self):
        """Constructor.
        """
        self._wifi = None
        self._ntrip_client = None
        self._ntripevent = Event()
        self._wifi_connected = False

    async def connect_wifi(self):
        """
        ASYNC CORO:
        Connect the ucontroller to the Wi-Fi.

        """
        _logger.info("initializing WiFiManager")
        self._ntripevent = Event()
        self._wifi = WiFiManager(WIFI_SSID, WIFI_PW)
        self._wifi_connected = await self._wifi.connect()
        _logger.info("Wi-Fi connected: " + str(self._wifi_connected))
        if self._wifi_connected:
            self._ntripevent.set()

    async def sync_ntrip_client(self):
        """
        ASYNC TASK:
        Checks periodically the Wi-Fi status
        Sets the NtripClient Synchronization Event.
        If Wi-Fi Connection is lost, the NtripClient should stop and
        if the Wi-Fi Connection is reestablished the NtripClient should resume.
        Changes of connection status are printed to console
        :raises: uasyncio.CancelledError
        """
        _logger.info("sync_ntrip_client() task initializing...")
        try:
            while True:
                current_status = self._wifi.wifi.isconnected()
                _logger.info("Connection status: " + str(current_status))
                if self._wifi_connected != current_status:
                    _logger.info("Wi-Fi connection status changed. Wi-Fi connected: " + str(current_status))
                    if current_status:
                        _logger.info("start ntrip client...")
                        self._ntripevent.set()
                    else:
                        _logger.info("stop ntrip client...")
                        self._ntripevent.clear()

                self._wifi_connected = current_status
                await uasyncio.sleep(WIFI_CHECK_TIME)

        except uasyncio.CancelledError as ex:
            self._ntripevent.clear()
            _logger.exc(ex, "sync_ntrip_client() task cancelled")
            raise
        except Exception as ex:
            self._ntripevent.clear()
            _logger.exc(ex, "sync_ntrip_client() task cancelled")
            raise
        finally:
            self._ntripevent.clear()
            _logger.exc(ex, "sync_ntrip_client() task cancelled")



