import machine
import utime
from pynmeagps.nmeatypes_core import NMEA_HDR, VALCKSUM

# Create I2C object
i2c_oled = machine.I2C(1, scl=machine.Pin(3), sda=machine.Pin(2))
i2c_gnss = machine.I2C(0, scl=machine.Pin(17), sda=machine.Pin(16))
i2c_address = None
# Print out any addresses found
gnss = i2c_gnss.scan()
oled = i2c_oled.scan()


if(gnss):
    for d in gnss:
        i2c_address = hex(d)

        
# print(b"\x24")
# print(b"\x0d\x0a")
# print(b"\x24\x47")
# print(b"\x24\x50")
# print(i2c_address)
# print(i2c_address)
# utime.sleep(100)

def read() -> bytes:
    
    reading = True
    raw_data = None

    while reading:  # loop until end of valid NMEA message or EOF
        byte1 = i2c_gnss.readfrom_mem(0x42, 0xFF, 1) # read 1st byte
        if len(byte1) < 1: #EOF
            break
        if byte1 != b"\x24":  # not NMEA, discard and continue
            continue
        byte2 = i2c_gnss.readfrom_mem(0x42, 0xFF, 1)  # read 2nd byte to confirm protocol
        if len(byte2) < 1:  # EOF
            break
        bytehdr = byte1 + byte2
        if bytehdr in NMEA_HDR:  # it's a NMEA message
            byte_payload = i2c_gnss.readfrom_mem(0x42, 0xFF, 2)
            while byte_payload[-2:] != b"\x0d\x0a": # NMEA protocol is CRLF terminated
                byte_payload += i2c_gnss.readfrom_mem(0x42, 0xFF, 1)
            
            raw_data = bytehdr + byte_payload
            reading = False
            
    return raw_data






while True:
    raw_data = read()
    if "GGA" in str(raw_data):
        print(raw_data)