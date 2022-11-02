import uasyncio
import micropython
from machine import UART, Pin

from gnss.gnss_handler import GnssHandler
from gnss.uart_writer import UartWriter
from primitives.queue import Queue
from gnss.uart_reader import UartReader
from gnss.gnssntripclient import GNSSNTRIPClient


async def main():
    masterTx = Pin(0)
    masterRx = Pin(1)

    gga_q = Queue(maxsize=5)
    cfg_q = Queue(maxsize=5)
    nav_q = Queue(maxsize=5)
    ack_q = Queue(maxsize=20)
    msg_q = Queue(maxsize=5)
    uart = UART(0, 115200, timeout=500)
    uart.init(bits=8, parity=None, stop=1, tx=masterTx, rx=masterRx, rxbuf=4096)

    sreader = uasyncio.StreamWriter(uart)
    swriter = uasyncio.StreamReader(uart)
    test = ""
    # await app_manager.connect_wifi()
    # await uasyncio.create_task(app_manager.sync_ntrip_client())
    uart_writer = UartWriter(app=test,
                             swriter=swriter,
                             queue=msg_q)
    uart_reader = UartReader(app=test,
                             sreader=sreader,
                             gga_q=gga_q,
                             cfg_resp_q=cfg_q,
                             nav_pvt_q=nav_q,
                             ack_nack_q=ack_q)

    gnss_handler = GnssHandler(app=test,
                               ack_nack_q=ack_q,
                               nav_pvt_q=nav_q,
                               cfg_resp_q=cfg_q,
                               msg_q=msg_q,
                               gga_q=gga_q)

    writertask = uasyncio.create_task(uart_writer.run())
    readertask = uasyncio.create_task(uart_reader.run())

    await gnss_handler.set_minimum_nmea_msgs()
    await uasyncio.sleep(5)
    await gnss_handler.set_update_rate(100)
    while True:
        await uasyncio.sleep(4)
        micropython.mem_info()
        print("hello")

uasyncio.run(main())

