from machine import Pin, PWM
#import Enum

#class LEDColor(Enum):
#    RED = 0
#    YELLOW = 1
#    GREEN = 2
#    OFF = 3

class LEDLevelPWM:
    def __init__(self, RedPin: int, YellowPin: int, GreenPin: int):
        self.RedLED = PWM(Pin(RedPin, Pin.OUT))
        self.RedLED.freq(1000)
        self.YellowLED = PWM(Pin(YellowPin, Pin.OUT))
        self.YellowLED.freq(1000)
        self.GreenLED = PWM(Pin(GreenPin, Pin.OUT))
        self.GreenLED.freq(1000)
    
    def set(self, color: int, level: int):
        if(level < 5):
            level = 5
        if(level > 100):
            level = 100
            
        intLevel = int(level/100 * 65535)
            
        if(color == 0):
            self.YellowLED.duty_u16(0)
            self.GreenLED.duty_u16(0)
            self.RedLED.duty_u16(intLevel)
        elif(color == 1):
            self.GreenLED.duty_u16(0)
            self.RedLED.duty_u16(0)
            self.YellowLED.duty_u16(intLevel)
        elif(color == 2):
            self.RedLED.duty_u16(0)
            self.YellowLED.duty_u16(0)
            self.GreenLED.duty_u16(intLevel)
        else:
            self.RedLED.duty_u16(0)
            self.YellowLED.duty_u16(0)
            self.GreenLED.Duty_u16(0)

            
            
        
        
