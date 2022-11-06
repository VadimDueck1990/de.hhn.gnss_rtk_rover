from machine import UART, Pin

uart0tx = Pin(0)
uart0Rx = Pin(1)

uart1tx = Pin(4)
uart1rx = Pin(5)


def initialize_uart():
    uart0 = UART(0, 115200, timeout=500)
    uart0.init(bits=8, parity=None, stop=1, tx=uart0tx, rx=uart0Rx, rxbuf=4096, txbuf=4096)

    uart1 = UART(1, 38400, timeout=500)
    uart1.init(bits=8, parity=None, stop=1, tx=uart1tx, rx=uart1rx, rxbuf=4096, txbuf=4096)


initialize_uart()
