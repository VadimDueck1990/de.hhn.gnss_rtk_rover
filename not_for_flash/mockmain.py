import micropython
import gc
print("start import")
micropython.mem_info()
import uasyncio
from machine import UART, Pin
print("imported uasyncio and machine")
micropython.mem_info()
from gnss.gnss_handler import GnssHandler
print("imported GnssHandler")
micropython.mem_info()
from gnss.uart_writer import UartWriter
print("imported UartWriter")
micropython.mem_info()
from primitives.queue import Queue
print("imported Queue")
micropython.mem_info()
from gnss.uart_reader import UartReader
print("imported UartReader")
micropython.mem_info()
# from gnss.gnssntripclient import GNSSNTRIPClient
gc.collect()
async def main():
    print("start main")
    micropython.mem_info()
    masterTx = Pin(0)
    masterRx = Pin(1)

    gga_q = Queue(maxsize=5)
    cfg_q = Queue(maxsize=5)
    nav_q = Queue(maxsize=5)
    ack_q = Queue(maxsize=20)
    msg_q = Queue(maxsize=5)
    print("Queues created")
    micropython.mem_info()
    uart = UART(0, 115200, timeout=500)
    uart.init(bits=8, parity=None, stop=1, tx=masterTx, rx=masterRx, rxbuf=4096)

    swriter = uasyncio.StreamWriter(uart)
    print("StreamWriter created")
    micropython.mem_info()
    sreader = uasyncio.StreamReader(uart)
    print("StreamReader created")
    micropython.mem_info()
    test = ""

    uart_writer = UartWriter(app=test,
                             swriter=swriter,
                             queue=msg_q)
    print("UartWriter created")
    micropython.mem_info()
    uart_reader = UartReader(app=test,
                             sreader=sreader,
                             gga_q=gga_q,
                             cfg_resp_q=cfg_q,
                             nav_pvt_q=nav_q,
                             ack_nack_q=ack_q)
    print("UartReader created")
    micropython.mem_info()
    gnss_handler = GnssHandler(app=test,
                               ack_nack_q=ack_q,
                               nav_pvt_q=nav_q,
                               cfg_resp_q=cfg_q,
                               msg_q=msg_q,
                               gga_q=gga_q)
    print("GnssHandler created")
    micropython.mem_info()
    writertask = uasyncio.create_task(uart_writer.run())
    readertask = uasyncio.create_task(uart_reader.run())
    print("tasks created")
    micropython.mem_info()
    await gnss_handler.set_minimum_nmea_msgs()
    print("set_minimum_nmea_msgs() called")
    micropython.mem_info()
    await uasyncio.sleep(5)
    await gnss_handler.set_update_rate(1000)
    print("set_set_update_rate(1000) called")
    micropython.mem_info()
    while True:
        await uasyncio.sleep(5)
        micropython.mem_info()
        print("hello")

uasyncio.run(main())

