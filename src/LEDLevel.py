from machine import Pin
#import Enum

#class LEDColor(Enum):
#    RED = 0
#    YELLOW = 1
#    GREEN = 2
#    OFF = 3

class LEDLevel:
    def __init__(self, RedPin: int, YellowPin: int, GreenPin: int):
        self.RedLED = Pin(RedPin, Pin.OUT)
        self.YellowLED = Pin(YellowPin, Pin.OUT)
        self.GreenLED = Pin(GreenPin, Pin.OUT)
    
    def set(self, color: int):
        if(color == 0):
            self.YellowLED(0)
            self.GreenLED(0)
            self.RedLED(1)
        elif(color == 1):
            self.GreenLED(0)
            self.RedLED(0)
            self.YellowLED(1)
        elif(color == 2):
            self.RedLED(0)
            self.YellowLED(0)
            self.GreenLED(1)
        else:
            self.RedLED(0)
            self.YellowLED(0)
            self.GreenLED(0)

            
            
        
        
