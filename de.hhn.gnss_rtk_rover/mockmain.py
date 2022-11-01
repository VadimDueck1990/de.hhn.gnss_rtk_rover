import uasyncio
from machine import UART, Pin

from gnss.uart_writer import UartWriter
from primitives.queue import Queue
from gnss.uart_reader import UartReader
from pyubx2.ubxmessage import UBXMessage
from pyubx2.ubxtypes_core import POLL, SET, GET


async def main():
    masterTx = Pin(0)
    masterRx = Pin(1)

    gga_q = Queue(maxsize=5)
    cfg_q = Queue(maxsize=5)
    nav_q = Queue(maxsize=5)
    ack_q = Queue(maxsize=5)
    msg_q = Queue(maxsize=5)
    uart = UART(0, 115200, timeout=500)
    uart.init(bits=8, parity=None, stop=1, tx=masterTx, rx=masterRx, rxbuf=4096)

    sreader = uasyncio.StreamWriter(uart)
    swriter = uasyncio.StreamReader(uart)
    test = ""
    # await app_manager.connect_wifi()
    # await uasyncio.create_task(app_manager.sync_ntrip_client())
    uart_writer = UartWriter(test,
                             swriter=swriter,
                             queue=msg_q)
    uart_reader = UartReader(test,
                             sreader=sreader,
                             gga_q=gga_q,
                             cfg_resp_q=cfg_q,
                             nav_pvt_q=nav_q,
                             ack_nack_q=ack_q)

    writertask = uasyncio.create_task(uart_writer.run())
    readertask = uasyncio.create_task(uart_reader.run())

    msg = UBXMessage("CFG",
                     "CFG-RATE",
                     SET,
                     measRate=1000,
                     navRate=1,
                     timeRef=1)

    # msg = UBXMessage(
    #     "NAV",
    #     "NAV-PVT",
    #     GET
    # )

    print(str(msg))
    while True:
        await msg_q.put(msg)
        await uasyncio.sleep(4)
        print("hello")

uasyncio.run(main())

