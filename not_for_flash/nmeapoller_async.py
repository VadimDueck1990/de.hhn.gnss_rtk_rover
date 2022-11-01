"""
nmeapoller.py

This example illustrates a simple implementation of a
'pseudo-concurrent' threaded NMEAMessage message
polling utility.

(NB: Since Python implements a Global Interpreter Lock (GIL),
threads are not truly concurrent.)

It connects to the receiver's serial port and sets up a
NMEAReader read thread. With the read thread running
in the background, it polls for a variety of NMEA
messages. The read thread reads and parses any responses
to these polls and outputs them to the terminal.

If a given NMEA message is not supported by your device,
you'll see a '<GNTXT...NMEA unknown msg>' response.

Created on 7 Mar 2021
@author: semuadmin
"""
# pylint: disable=invalid-name

import uasyncio as asyncio
from machine import UART, Pin, I2C
from pynmeagps import (
    NMEAMessage,
    NMEAReader,
    POLL,
    NMEA_MSGIDS,
)

# initialise global variables
reading = False
masterTx = Pin(0)
masterRx = Pin(1)


async def read_messages(nmeareader):
    """
    Reads, parses and prints out incoming UBX messages
    """
    # pylint: disable=unused-variable, broad-except
    while True:
        # try:
        (raw_data, parsed_data) = await nmeareader.read_uart()
        if parsed_data:
            print(parsed_data)
        if raw_data is not None:
            print(raw_data)


#         except Exception as err:
#             print(f"\n\nSomething went wrong {err}\n\n")
#             continue


async def send_message(swriter, message):
    """
    Send message to device
    """
    swriter.write(message.serialize())
    await swriter.drain()
    await asyncio.sleep(2)


async def main():
    # initialize serials
    i2c_zed_f9p = I2C(0, scl=Pin(17), sda=Pin(16))

    uart = UART(0, 115200, timeout=500)
    uart.init(bits=8, parity=None, stop=1, tx=masterTx, rx=masterRx, rxbuf=4096)

    nmr = NMEAReader(i2c=i2c_zed_f9p, uart=uart)

    print("\nStarting read task...\n")
    read_task = asyncio.create_task(read_messages(nmr))

    # DO OTHER STUFF HERE WHILE READING TASK IN BACKGROUND...
    # for msgid in NMEA_MSGIDS:
    #     print(f"\n\nSending a GNQ message to poll for an {msgid} response...\n\n")
    #     msg = NMEAMessage("EI", "GNQ", POLL, msgId=msgid)
    #     await send_message(nmr.swriter, msg)
    #     await asyncio.sleep(1)
    #
    #     print("\nPolling complete. Pausing for any final responses...\n")
    while True:
        await asyncio.sleep(1)


def test():
    asyncio.run(main())

test()
