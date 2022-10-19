
# Test of uasyncio stream I/O using UART
# Author: Peter Hinch
# Copyright Peter Hinch 2017-2022 Released under the MIT license
# Link X1 and X2 to test.

import uasyncio as asyncio
from machine import UART, Pin

masterTx = Pin(4)
masterRx = Pin(5)

uart = UART(1, 9600, timeout=0)
uart.init(baudrate=38400, bits=8, parity=None, stop=1, tx=masterTx, rx=masterRx)

async def sender():
    swriter = asyncio.StreamWriter(uart, {})
    while True:
        swriter.write('Hello uart\n')
        await swriter.drain()
        await asyncio.sleep(2)

async def receiver():
    print("in receiver")
    sreader = asyncio.StreamReader(uart)
    while True:
        res = await sreader.readline()
        print('Received', res)

async def main():
    # asyncio.create_task(sender())
    asyncio.create_task(receiver())
    while True:
        await asyncio.sleep(1)

def test():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Interrupted')
    finally:
        asyncio.new_event_loop()
        print('as_demos.auart.test() to run again.')

test()