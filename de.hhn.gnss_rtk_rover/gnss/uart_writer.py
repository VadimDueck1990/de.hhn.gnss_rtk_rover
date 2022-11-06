"""
UartWriter class.
Connect the ucontroller to the GNSS Receiver.
Send messages from the Queue to the receiver
Created on 4 Sep 2022
:author: vdueck
"""
import gc
gc.collect()
import primitives.queue
import uasyncio
import utils.logging as logging

_logger = logging.getLogger("uart_reader")
_logger.setLevel(logging.WARNING)

class UartWriter:
    """
    UartWriter class.
    """

    _app = None
    _swriter = None
    _queue = None

    @classmethod
    def initialize(cls, app: object, swriter: uasyncio.StreamWriter, queue: primitives.queue.Queue):
        """Constructor.

        :param object app: The calling app
        :param uasyncio.StreamWriter swriter: the serial connection to the GNSS Receiver(UART1)
        :param primitives.queue.Queue queue: the queue with the incoming messages
        """

        cls._app = app
        cls._swriter = swriter
        cls._queue = queue
        gc.collect()

    @classmethod
    async def run(cls) -> bool:
        """
        ASYNC: Send incoming messages from queue to the GNSS receiver.
        """
        while True:
            gc.collect()
            msg = await cls._queue.get()
            _logger.info("Sending message over UART1")
            cls._swriter.write(msg)
            await cls._swriter.drain()

