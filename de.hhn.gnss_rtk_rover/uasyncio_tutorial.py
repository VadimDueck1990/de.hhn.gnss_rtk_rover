
from machine import UART, Pin
import utime
import uasyncio as asyncio
from primitives.delay_ms import Delay_ms

masterTx = Pin(0)
masterRx = Pin(1)

class Master():
    def __init__(self, uart_no = 0, timeout=4000):
        self.uart = UART(uart_no, 38400)
        self.uart.init(baudrate=38400, bits=8, parity=None, stop=1, tx=masterTx, rx=masterRx)
        
        self.timeout = timeout
        self.swriter = asyncio.StreamWriter(self.uart, {})
        self.sreader = asyncio.StreamReader(self.uart)
        self.delay = Delay_ms()
        self.response = []
        print("in Master init")
        asyncio.create_task(self._recv())
        print("passed receive Task")

    async def _recv(self):
        print("in _recv")
        while True:
            res = await self.sreader.read(1)
            self.response.append(res)  # Append to list of lines
            print(res)
            self.delay.trigger(self.timeout)  # Got something, retrigger timer

    async def send_command(self, command):
        self.response = []  # Discard any pending messages
        if command is None:
            print('Timeout test.')
        else:
            await self.swriter.awrite("{}\r\n".format(command))
            print('Command sent:', command)
        self.delay.trigger(self.timeout)  # Re-initialise timer
        while self.delay.running():
            await asyncio.sleep(1)  # Wait for 4s after last msg received
        return self.response

async def main():
    print('This test takes 10s to complete.')
    master = Master()
    while True:
        await asyncio.sleep(1)

def test():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Interrupted')
    finally:
        asyncio.new_event_loop()
        print('as_demos.auart_hd.test() to run again.')

test()