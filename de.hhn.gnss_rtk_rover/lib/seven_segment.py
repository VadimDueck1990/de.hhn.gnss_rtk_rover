"""
7 Segment Display Control Class

Created on 04 Mar 2021

:author: vdueck 198909
"""

from machine import Pin

pins = [
    Pin(7, Pin.OUT), # middle
    Pin(6, Pin.OUT), # top left
    Pin(1, Pin.OUT), # top
    Pin(2, Pin.OUT), # top right
    Pin(3, Pin.OUT), # bottom right
    Pin(4, Pin.OUT), # bottom
    Pin(5, Pin.OUT), # bottom left
    Pin(8, Pin.OUT), # dot
    ]

# common anode 7 segment
chars = [
    [0, 1, 1, 1, 1, 1, 1, 1], #0
    [0, 0, 0, 1, 1, 0, 0, 1], #1
    [1, 0, 1, 1, 0, 1, 1, 1], #2
    [1, 0, 1, 1, 1, 1, 0, 1], #3
    [1, 1, 0, 1, 1, 0, 0, 1], #4
    [1, 1, 1, 0, 1, 1, 0, 1], #5
    [1, 1, 1, 0, 1, 1, 1, 1], #6
    [0, 0, 1, 1, 1, 0, 0, 1], #7
    [1, 1, 1, 1, 1, 1, 1, 1], #8
    [1, 1, 1, 1, 1, 1, 0, 1], #9
    ]

class SevenSegment:
    """
    SevenSegment class.
    """
    
    def __init__(self):
        """
        Constructor
        If everything is correct, the dot on the display
        should light up
        """
        self.clear()
        
        
    def clear(self):
        """
        Clears the display, except the dot
        """
        for i in pins:
            i.value(0)
        pins[7].value(1)
        
    def set(self, digit: int):
        """
        Sets the display to number between 0 and 9
        """
        if 0 <= digit <= 9:
            self.clear()
            for i in range(len(pins)):
                pins[i].value(chars[digit][i])
        else:
            print("Invalid input: number must be between 0 and 9")
    