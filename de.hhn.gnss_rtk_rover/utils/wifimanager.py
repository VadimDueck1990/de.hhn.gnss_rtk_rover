"""
WiFiManager class.

Connects the ucontroller to an Access Point.

Manages connection of NTRIPClient to the caster.
If a Wi-Fi connection is established: enable NTRIPClient,
otherwise disable the NTRIPClient


Created on 4 Sep 2022

:author: vdueck
"""

import network
import uasyncio as asyncio
import utils.logging as logging

_logger = logging.getLogger("wifi_manager")
# _logger.setLevel(logging.WARNING)

class WiFiManager:
    """
    WiFiManager class.
    """

    def __init__(self, ssid: str, password: str):
        """Constructor.

        :param str ssid: SSID of the Wi-Fi access point
        :param str password: Password of the Wi-Fi access point
        """

        self._ssid = ssid
        self._password = password
        self._wifi = network.WLAN(network.STA_IF)

    # Read-only field accessors
    @property
    def wifi(self):
        """WLAN object"""
        return self._wifi

    async def connect(self) -> bool:
        """
        ASYNC: Connect the ucontroller to the Wi-Fi.

        :return: True if connected, False if connection failed
        :rtype: bool
        """

        if self._wifi.isconnected():
            _logger.info("Wi-Fi already connected. ifconfig: " + str(self._wifi.ifconfig()))
            return True
        else:
            self._wifi.active(True)
            self._wifi.connect(self._ssid, self._password)
            timeout = 0
            while not self._wifi.isconnected():
                _logger.info("Waiting for connection...")
                await asyncio.sleep(1)
                timeout += 1
                if timeout == 10:
                    _logger.info("Something went wrong, Wi-Fi connection failed...")
                    return False

            _logger.info("Wi-Fi connected, ifconfig: " + str(self._wifi.ifconfig()))
            return True

