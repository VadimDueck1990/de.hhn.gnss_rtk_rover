import machine
import uasyncio

# Settings
led = machine.Pin('LED', machine.Pin.OUT)

# Coroutine: blink on a timer
async def blink(delay):
    while True:
        led.toggle()
        await uasyncio.sleep(delay)
        
async def main():
    uasyncio.create_task(blink(0.2))
    
    while True:
        print("done!")
        uasyncio.sleep_ms(1000)
        
uasyncio.run(main())