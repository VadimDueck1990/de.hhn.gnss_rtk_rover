import network
import time


def connect_wifi():

    ssid = "WLAN-L45XAB"
    password = "7334424916822832"
    wifi = network.WLAN(network.STA_IF)

    if wifi.isconnected():
        print("Wi-Fi already connected. ifconfig: " + str(wifi.ifconfig()))
        return True
    else:
        wifi.active(True)
        wifi.connect(ssid, password)
        timeout = 0
        while not wifi.isconnected():
            print("Waiting for connection...")
            time.sleep(1)
            timeout += 1
            if timeout == 10:
                print("Something went wrong, Wi-Fi connection failed...")

        print("Wi-Fi connected, ifconfig: " + str(wifi.ifconfig()))

connect_wifi()