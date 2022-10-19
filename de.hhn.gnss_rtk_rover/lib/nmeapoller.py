"""
nmeapoller.py

This example illustrates a simple implementation of a
Micropython NMEAMessage message
polling utility.

It connects to the receiver's serial port over i2c
and reads all incoming messages

If a given NMEA message is not supported by your device,
you'll see a '<GNTXT...NMEA unknown msg>' response.

Created on 7 Mar 2021
@author: semuadmin

Edited and adapted to upython on 9 Sep 2022
@author: vdueck
"""
# pylint: disable=invalid-name

import machine
from time import sleep
from pynmeagps import (
    NMEAMessage,
    NMEAReader,
    POLL,
    NMEA_MSGIDS,
)

reading = False


def read_messages(nmeareader):
    """
    Reads, parses and prints out incoming NMEA messages
    """
    # pylint: disable=unused-variable, broad-except

    while reading:
        # try:
        (raw_data, parsed_data) = nmeareader.read_i2c()
        if parsed_data:
            print(parsed_data)
#            print(raw_data)
#         if raw_data is not None:
#             print(raw_data)
#            sleep(1)
#         except Exception as err:
#             print(f"\n\nSomething went wrong {err}\n\n")
#             continue


if __name__ == "__main__":

    i2c_zed_f9p = machine.I2C(0, scl=machine.Pin(17), sda=machine.Pin(16))

    # create NMEAReader instance
    nmr = NMEAReader(i2c=i2c_zed_f9p)

    print("\nStarting reading...\n")
    reading = True
    read_messages(nmr)

    print("\nPolling complete. Pausing for any final responses...\n")
    sleep(1)
    print("\nProcessing Complete")