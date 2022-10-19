from seven_segment import SevenSegment
import utime

display = SevenSegment()

i = 0
while i <= 10:
    if i == 10:
        i = 0
    display.set(i)
    utime.sleep(1)
    i += 1