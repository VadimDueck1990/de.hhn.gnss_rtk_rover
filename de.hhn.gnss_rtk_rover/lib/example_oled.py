
"""
OLED1306 Control Class

Created on 10 Sep 2022

:author: vdueck 198909
"""

from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import framebuf
import utime

class Oled:
    """
    Oled class.
    """
    
    WIDTH = 128
    HEIGHT =64
    SCL_PIN = 3
    SDA_PIN = 2

    txtlines = [0, 8, 22, 30, 44, 52]
    
    @classmethod
    def initialize(cls):
        """
        Initializes the oled
        If everything is correct, the oled should display a satellite icon
        should light up
        """
        cls.i2c = I2C(1, scl = Pin(cls.SCL_PIN), sda = Pin(cls.SDA_PIN))
        cls.oled = SSD1306_I2C(cls.WIDTH, cls.HEIGHT, cls.i2c)
        cls.prepare()
        
        
    @classmethod
    def prepare(cls):
        cls.oled.fill(0)
        cls.oled.text("Fix:", 0, cls.txtlines[0])
        cls.oled.text("", 0, cls.txtlines[1])
        cls.oled.text("Lat:", 0, cls.txtlines[2])
        cls.oled.text("", 0, cls.txtlines[3])
        cls.oled.text("Lon:", 0, cls.txtlines[4])
        cls.oled.text("", 0, cls.txtlines[5])
        cls.oled.show()
    
    
    @classmethod
    def updateLat(cls, lat: str):
        cls.oled.text(lat, 0, cls.txtlines[3])
        cls.oled.show()
        
    
    @classmethod
    def updateLon(cls, lon: str):
        cls.oled.text(lon, 0, cls.txtlines[5])
        cls.oled.show()
        
        
    @classmethod
    def updateFix(cls, fix: str):
        cls.oled.text(fix, 0, cls.txtlines[1])
        cls.oled.show()
Oled.initialize()

i = 0
while True:
    fix = i % 5
    Oled.prepare()
    Oled.updateFix(str(fix))
    Oled.updateLat(str(i + 1) + "." + str(i + 4) + str(i + 3) + str(i + 1) + str(i + 2))
    Oled.updateLon(str(i + 3) + "." + str(i) + str(i + 1) + str(i + 2) + str(i + 3))
    i += 1
    i = i % 6
    utime.sleep(1)

        
        