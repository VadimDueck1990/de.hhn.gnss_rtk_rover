from app_manager import AppManager
import uasyncio


async def main():
    app_manager = AppManager()
    await app_manager.connect_wifi()
    ntrip_sync_task = uasyncio.create_task(app_manager.sync_ntrip_client())
    await uasyncio.sleep(20)
    ntrip_sync_task.cancel()
    await uasyncio.sleep(4)
    print("all finished")

uasyncio.run(main())

