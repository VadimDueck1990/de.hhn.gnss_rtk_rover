"""
UartWriter class.

Connect the ucontroller to the GNSS Receiver.
Send messages from the Queue to the receiver


Created on 4 Sep 2022

:author: vdueck
"""
import gc
import uasyncio
import primitives.queue
import utils.logging as logging

_logger = logging.getLogger("uart_writer")


class UartWriter:
    """
    UartWriter class.
    """

    def __init__(self, app: object, swriter: uasyncio.StreamWriter, queue: primitives.queue.Queue):
        """Constructor.

        :param object app: The calling app
        :param uasyncio.StreamWriter swriter: the serial connection to the GNSS Receiver(UART1)
        :param primitives.queue.Queue queue: the queue with the incoming messages
        """

        self._app = app
        self._swriter = swriter
        self._queue = queue

    async def run(self) -> bool:
        """
        ASYNC: Send incoming messages from queue to the GNSS receiver.
        """
        while True:
            msg = await self._queue.get()
            _logger.debug("Sending message over UART1: " + str(msg))
            self._swriter.write(msg.serialize())
            await self._swriter.drain()
            gc.collect()
