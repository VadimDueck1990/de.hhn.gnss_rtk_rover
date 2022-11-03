import micropython
import gc
import uasyncio
from machine import UART, Pin

from gnss.gnss_handler import GnssHandler
from gnss.uart_writer import UartWriter
from primitives.queue import Queue
from gnss.uart_reader import UartReader
# from gnss.gnssntripclient import GNSSNTRIPClient


async def main():
    gc.collect()
    print("start main")
    micropython.mem_info()
    masterTx = Pin(0)
    masterRx = Pin(1)

    gga_q = Queue(maxsize=5)
    cfg_q = Queue(maxsize=5)
    nav_q = Queue(maxsize=5)
    ack_q = Queue(maxsize=20)
    msg_q = Queue(maxsize=5)

    uart = UART(0, 115200, timeout=500)
    uart.init(bits=8, parity=None, stop=1, tx=masterTx, rx=masterRx, rxbuf=4096, txbuf=4096)

    sreader = uasyncio.StreamWriter(uart)
    swriter = uasyncio.StreamReader(uart)
    test = ""

    UartWriter.initialize(app=test,
                          swriter=swriter,
                          queue=msg_q)
    UartReader.initialize(app=test,
                          sreader=sreader,
                          gga_q=gga_q,
                          cfg_resp_q=cfg_q,
                          nav_pvt_q=nav_q,
                          ack_nack_q=ack_q)

    GnssHandler.initialize(app=test,
                           ack_nack_q=ack_q,
                           nav_pvt_q=nav_q,
                           cfg_resp_q=cfg_q,
                           msg_q=msg_q,
                           gga_q=gga_q)

    writertask = uasyncio.create_task(UartWriter.run())
    readertask = uasyncio.create_task(UartReader.run())

    await GnssHandler.set_minimum_nmea_msgs()
    await uasyncio.sleep(5)
    # await GnssHandler.set_update_rate(1000)
    gc.collect()
    while True:
        navsat = await GnssHandler.get_satellites_in_use()
        print("fix type: ", str(navsat))
        # await uasyncio.sleep(2)
        # micropython.mem_info()
        # result = await GnssHandler.set_satellite_systems(1, 0, 0, 0)
        # print("set sat systems: ", result)
        # await uasyncio.sleep(2)
        # micropython.mem_info()
        # satsys = await GnssHandler.get_satellite_systems()
        # print("get sat systems: ", str(satsys))
        # # await uasyncio.sleep(2)
        # # micropython.mem_info()
        # (hacc, vacc) = await GnssHandler.get_precision()
        # print("hacc vacc: " + str(hacc) + " " + str(vacc))
        # await uasyncio.sleep_ms(500)
        micropython.mem_info()
        print("hello")

uasyncio.run(main())

