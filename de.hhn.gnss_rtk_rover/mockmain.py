from appmanager import AppManager
import uasyncio
from gnss.gnssntripclient import GNSSNTRIPClient


async def main():
    # app_manager = AppManager()
    # await app_manager.connect_wifi()
    # await uasyncio.create_task(app_manager.sync_ntrip_client())
    while True:
        await uasyncio.sleep(1)
        print("hello")

uasyncio.run(main())

