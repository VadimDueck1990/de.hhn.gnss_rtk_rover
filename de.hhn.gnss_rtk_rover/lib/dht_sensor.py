# Bibliotheken laden
from machine import Pin
from utime import sleep
from dht import DHT11

# Initialisierung GPIO und DHT11
sleep(1)
dht11_sensor = DHT11(Pin(0, Pin.IN, Pin.PULL_UP))

# Wiederholung (Endlos-Schleife)
while True:
    # Messung durchführen
    dht11_sensor.measure()
    # Werte lesen
    temp = dht11_sensor.temperature()
    humi = dht11_sensor.humidity()
    # Werte ausgeben
    print('      Temperatur:', temp, '°C')
    print('Luftfeuchtigkeit:', humi, '%')
    print()
    sleep(3)