# created:  26.05.2022
# by PA0DEV
#
# version: 1.0.0
# designed and tested on ESP32 TTGO and ESP8266

""" 
MIT License
Copyright (c) [2022] [PA0DEV]
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE. 
"""


import machine, neopixel
try:
    from uasyncio import sleep
except:
    from asyncio import sleep

### LED addresses ###
# Segments
#      __ __ __        __ __ __          __ __ __        12 13 14  
#    __        __    __        __      __        __    11        15
#    __        __    __        __      __        __    10        16
#    __        __    __        __  42  __        __    _9        17
#      __ __ __        __ __ __          __ __ __        20 19 18  
#    __        65    __        44  43  __        21    _8        _0
#    __        __    __        __      __        __    _7        _1
#    __        __    __        __      __        __    _6        _2
#       __ __ __       __ __ __           __ __ __       _5 _4 _3   



# address segment number / symbol
#      __ _4 __  
#    __        __
#    _3        _5
#    __        __
#      __ _6 __  
#    __        __
#    _2        _0
#    __        __
#       __ _1 __   

segmentNumbers = {
    "0": [0, 1, 2, 3, 4, 5],
    "1": [0, 5],
    "2": [1, 2, 4, 5, 6],
    "3": [0, 1, 4, 5, 6],
    "4": [0, 3, 5, 6],
    "5": [0, 1, 3, 4, 6],
    "6": [0, 1, 2, 3, 4, 6],
    "7": [0, 4, 5],
    "8": [0, 1, 2, 3, 4, 5, 6],
    "9": [0, 1, 3, 4, 5, 6],
    "°": [3, 4, 5, 6],
    "C": [1, 2, 3, 4],
    "F": [2, 3, 4, 6],
    "E": [1, 2, 3, 4, 6],
    "U": [0, 1, 2, 3, 5],
    "P": [2, 3, 4, 5, 6],
    "-": [6]
}

class Segments:
    def __init__(self, pin, addrOfset=0, ledPerSegment=3, ledPerDot=1, numDisplay=4):
        """
        7-Segment Display

            :param pin: the Pin the display is connected to
            :param addrOffset: Offset to the first Segment LED
            :param ledPerSegment: number of LEDs per Segment
            :param ledPerDot: number of LEDs per dot
            :param numDisplay: number of 7-Segment display in the display
            :return: returns nothing
        """       
        global LedPerSegment
        LedPerSegment = ledPerSegment
        # calc the total number of LEDs
        ledCnt = (numDisplay*ledPerSegment*7)+((numDisplay-1)//2*ledPerDot)
        
        # calc starting addr for each segment
        global segStart
        segStart = []
        for i in range(numDisplay):
            segStart.append(addrOfset + i * (7*ledPerSegment) + (2*(i//2)*ledPerDot))

        # clac segment number addresses
        global numAddr
        numAddr = {}
        for name in segmentNumbers:
            listAddr = []
            for addr in segmentNumbers[name]:
                for i in range(ledPerSegment): 
                    listAddr.append(addr*ledPerSegment + i)
            numAddr[name] = listAddr
        
        # calc addr for each dot LED
        global dotAddr
        dotAddr = []
        for i in range((numDisplay-1)//2):
            for led in range(2*ledPerDot):
                dotAddr.append(addrOfset+(14*ledPerSegment)+led + i * ledPerSegment * 24)
        
        global np
        np = neopixel.NeoPixel(machine.Pin(pin), ledCnt+1)
        # Init all leds OFF (R=0, G=0, B=0)
        for i in range(ledCnt):
            np[i] = (0, 0, 0)
        np.write()


    def setDots(self, display, dotColor=(0, 0, 100)):
        """
        Method to turn the dots of the Display off / on

        :param display: True-> dots ON / False -> dots OFF
        :param dotColor: color of the dots (R, G, B)
        :return: returns nothing
        """ 
        for addr in dotAddr:
            if display == True:
                np[addr] = dotColor
                np.write()
            else:
                np[addr] = (0, 0, 0)
                np.write()
    
    def setSegment(self, num, value, color=(0, 0, 100)):
        """
        Method to write one segment

        :param num: index of the display
        :param value: value to write (str / int)
        :param color: color of the number (R, G, B) Max 100
        :return: returns nothing
        """ 
        if value == None:
            for i in range(7*LedPerSegment):
                np[segStart[num]+i] = (0, 0, 0)
            np.write()
        
        else:
            if isinstance(value, int):
                str(value)
            if value in numAddr:

                for i in range(7*LedPerSegment):
                    np[segStart[num]+i] = (0, 0, 0)

                color = tuple([int(i / 2.55) for i in color])

                for addr in numAddr[value]:
                    np[addr + segStart[num]] = color
                np.write()
            else:
                print("[Segment] invalid Value. Cannot display " + value)

    def setDoubleSegment(self, num, value, color=(0, 0, 100)):
        """
        Method to write one double digit Display

            :param num: index of the starting display
            :param value: the value to write to the display (str or int (0-99))
            :param color: color of the number (R, G, B)
            :return: returns nothing
        """

        if isinstance(value, str):
            try:
                value = int(value)
            except:
                print("[Segment] invalid Value. Cannot display " + value)
                return
        elif not (isinstance(value, int) and 0<= value < 100):
            print("[Segment] invalid Value. Cannot display " + value)
            return
        digit0 = value %10
        digit1 = value // 10
        self.setSegment(num, str(digit0), color=color)
        self.setSegment(num+1, str(digit1), color=color)

    async def demo(self, num, delay, color=(0, 0, 100)):
        """
        Method to demonstrate all Display values

        :param delay: delay
        :param color: color of the numbers
        :return: returns nothing
        """ 
        
        
        self.setSegment(num, "0", color=color)
        await sleep(delay)
        self.setSegment(num, "1", color=color)
        await sleep(delay)
        self.setSegment(num, "2", color=color)
        await sleep(delay)
        self.setSegment(num, "3", color=color)
        await sleep(delay)
        self.setSegment(num, "4", color=color)
        await sleep(delay)
        self.setSegment(num, "5", color=color)
        await sleep(delay)
        self.setSegment(num, "6", color=color)
        await sleep(delay)
        self.setSegment(num, "7", color=color)
        await sleep(delay)
        self.setSegment(num, "8", color=color)
        await sleep(delay)
        self.setSegment(num, "9", color=color)
        await sleep(delay)
        self.setSegment(num,  "°", color=color)
        await sleep(delay)
        self.setSegment(num, "C", color=color)
        await sleep(delay)
        self.setSegment(num, "F", color=color)
        await sleep(delay)
        self.setSegment(num, "U", color=color)
        await sleep(delay)
        self.setSegment(num, "E", color=color)
        await sleep(delay)
        self.setSegment(num, "P", color=color)
        await sleep(delay)
        self.setSegment(num, "-", color=color)
        await sleep(delay)
        self.setSegment(num, None)
        await sleep(delay)
        print("Error Test")
        self.setSegment(0, "aaa", color=color)