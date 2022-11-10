import gc
import uasyncio
from machine import UART, Pin
from uasyncio import Event
from utils.wifimanager import WiFiManager
from utils.globals import WIFI_SSID, WIFI_PW
from utils.mem_debug import debug_gc
from gnss.gnss_handler import GnssHandler
from gnss.uart_writer import UartWriter
from primitives.queue import Queue
from gnss.uart_reader import UartReader
from gnss.gnssntripclient import GNSSNTRIPClient
from webapi.requesthandler import RequestHandler
gc.collect()

ntrip_stop_event = Event()
ggaevent = Event()


async def main():
    masterTx = Pin(0)
    masterRx = Pin(1)

    rtcmTx = Pin(4)
    rtcmRx = Pin(5)

    gga_q = Queue(maxsize=1)
    cfg_q = Queue(maxsize=5)
    nav_q = Queue(maxsize=5)
    ack_q = Queue(maxsize=20)
    msg_q = Queue(maxsize=5)
    pos_q = Queue(maxsize=1)

    ntrip_stop_event.set()

    uart_rtcm = UART(1, 38400, timeout=500)
    uart_rtcm.init(bits=8, parity=None, stop=1, tx=rtcmTx, rx=rtcmRx, rxbuf=4096, txbuf=4096)

    uart_ubx_nmea = UART(0, 115200, timeout=500)
    uart_ubx_nmea.init(bits=8, parity=None, stop=1, tx=masterTx, rx=masterRx, rxbuf=8192, txbuf=4096)

    sreader = uasyncio.StreamWriter(uart_ubx_nmea)
    swriter = uasyncio.StreamReader(uart_ubx_nmea)
    test = ""

    UartWriter.initialize(app=test,
                          swriter=swriter,
                          queue=msg_q)
    UartReader.initialize(app=test,
                          sreader=sreader,
                          gga_q=gga_q,
                          cfg_resp_q=cfg_q,
                          nav_pvt_q=nav_q,
                          ack_nack_q=ack_q,
                          ggaevent=ggaevent,
                          position_q=pos_q)

    GnssHandler.initialize(app=test,
                           ack_nack_q=ack_q,
                           nav_pvt_q=nav_q,
                           cfg_resp_q=cfg_q,
                           msg_q=msg_q,
                           gga_q=gga_q,
                           pos_q=pos_q)

    writertask = uasyncio.create_task(UartWriter.run())
    readertask = uasyncio.create_task(UartReader.run())

    await GnssHandler.set_minimum_nmea_msgs()
    await uasyncio.sleep(5)

    wifi = WiFiManager(WIFI_SSID, WIFI_PW)
    await wifi.connect()
    await GnssHandler.set_update_rate(2000)
    enabled = await GnssHandler.set_high_precision_mode(1)
    print("main -> high precision mode enabled: " + str(enabled))
    gc.collect()

    fix = 0
    while fix < 1:
        fix = await GnssHandler.get_fixtype()

    print("main -> got position, starting ntrip client")
    ntripclient = GNSSNTRIPClient(uart_rtcm, test, gga_q, ntrip_stop_event, ggaevent)
    ntrip_stop_event.clear()
    ntriptask = uasyncio.create_task(ntripclient.run())
    gc.collect()
    gccount = 0
    webserver = uasyncio.create_task(RequestHandler.initialize(test, pos_q))
    while wifi.wifi.isconnected():
        gccount += 1
        # hacc, vacc = await GnssHandler.get_precision()
        # print("hacc: " + str(hacc) + " vacc: " + str(vacc))
        # if gccount > 5:
        #     debug_gc()
        #     gccount = 0
        await uasyncio.sleep(1)


uasyncio.run(main())

