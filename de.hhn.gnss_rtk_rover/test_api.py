import uasyncio
import network
from webapi.requesthandler import RequestHandler
from primitives.queue import Queue
test = ""
pos_q = Queue()

WIFI_SSID = "WLAN-L45XAB"
WIFI_PW = "7334424916822832"
# WIFI_SSID = "huawei_p30_lite"
# WIFI_PW = "99999999"
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PW)
print(wifi.ifconfig())

async def printtest():
    count = 0
    while True:
        # print("Task is working and counting: ", count)
        count += 1
        await uasyncio.sleep_ms(100)


async def main():
    task1 = uasyncio.create_task(printtest())
    print("starting web server...")
    webserver = uasyncio.create_task(RequestHandler.initialize(test, pos_q))
    count2 = 0
    while True:
        # print("main task running: " + str(count2))
        count2 += 1
        await uasyncio.sleep_ms(100)

uasyncio.run(main())
