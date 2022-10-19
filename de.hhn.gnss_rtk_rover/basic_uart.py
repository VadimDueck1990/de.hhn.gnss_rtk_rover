from machine import Pin, UART


masterTx = Pin(0)
masterRx = Pin(1)

uart = UART(0, 38400)
uart.init(baudrate=38400, bits=8, parity=None, stop=1, tx=masterTx, rx=masterRx)

while True:
    if uart.any() > 0:
        data = uart.read(1)
        print(str(data))
