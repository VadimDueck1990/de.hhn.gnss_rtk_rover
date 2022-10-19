from machine import Pin
import utime

led = Pin('LED', Pin.OUT)


def blink_led():
    while True:
        led.toggle()
        utime.sleep_ms(500)


if __name__ == "__main__":
    blink_led()