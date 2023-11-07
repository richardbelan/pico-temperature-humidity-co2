import time
from machine import I2C, Pin, ADC
import dht
import LEDLevelPWM
import CCS811
import math
import Calibrate
import Settings
import gc
import os

####################################################################
#use of pins
# GP pin  PWM  FNC
#      0  0A   LED R
#      1  0B   LED R
#      2  1A   LED Y
#      5  2B   LED G
#      7  3B   LED Y
#      8  4A   LED G
#     14  7A   DHT22
#     16  0A   I2C
#     17  0B   I2C
#     20  2A   LED R
#     21  2B   LED Y -> 19 (1B)
#     22  3A   LED G

class MeasureCtrl:
    def __init__(self):
        self.BaselineFileName = 'baseline.cnf'
        self.measurementLoopNo = 0
        self.XMLString = "<measurement/>"
        self.AliveLED = Pin("LED", Pin.OUT)
        self.AliveLED.value(1)
        
        #DHT sensor
        self.sensor = dht.DHT22(Pin(14))

        self.LED_CO2 = LEDLevelPWM.LEDLevelPWM(20, 19, 22)
        self.LED_HUM = LEDLevelPWM.LEDLevelPWM( 1,  7,  8)
        self.LED_TMP = LEDLevelPWM.LEDLevelPWM( 0,  2,  5)
        
        self.adcLight = ADC(Pin(26, mode=Pin.IN))
        self.adcCoreTemp = ADC(ADC.CORE_TEMP)
        self.conversionFactor = 3.3/(65535)
        
        #red
        self.LED_CO2.set(0, 100)
        self.LED_HUM.set(0, 100)
        self.LED_TMP.set(0, 100)
        
        self.i2c = I2C(0, sda=Pin(16), scl=Pin(17))
        self.co2 = CCS811.CCS811(self.i2c)
        
    def initialize(self):
        self.AliveLED.value(0)
        self.temCal = Calibrate.Calibrate(Settings.Settings.TemperatureOffset())
        self.humCal = Calibrate.Calibrate(Settings.Settings.HumidityOffset())
        
        
        gc.enable()
            
        time.sleep(1)
        
        try:
            self.sensor.measure()
            self.RegTemp = self.temCal.convert(self.sensor.temperature())
            self.RegHum = self.humCal.convert(self.sensor.humidity())
        
        except Exception:
            self.RegTemp = 25
            self.RegHum = 50
        

        #yellow
        self.AliveLED.value(1)
        self.LED_CO2.set(1, 100)
        self.LED_HUM.set(1, 100)
        self.LED_TMP.set(1, 100)
        
        setup = self.readBaseline()

        self.co2.setup(setup)
        self.co2.setTempHum(self.RegTemp, self.RegHum)

        time.sleep(1)
        
        #green
        self.LED_CO2.set(2, 100)
        self.LED_HUM.set(2, 100)
        self.LED_TMP.set(2, 100)

        self.updateRegTemHum = False
        
    def readBaseline(self):
        try:
            f = open(self.BaselineFileName, 'rb')
            if f is None:
                return None
            baseline = f.read()
            f.close()
            return bytes([baseline[0], baseline[1]])
        except Exception:
            return None
        
    def saveBaseline(self):
        try:
            baseline = self.co2.readBaseline()
            f = open(self.BaselineFileName, 'wb')
            if f is None:
                return None
            f.write(baseline)
            f.close()
            return None
        except Exception:
            return None
        
    def getData(self):
        return self.XMLString

    def measure(self):
        while True:
            #DTH22 results
            self.AliveLED.toggle()
            
            try:
                self.sensor.measure()
                self.temp = self.temCal.convert(self.sensor.temperature())
                self.hum = self.humCal.convert(self.sensor.humidity())
            except Exception:
                print("exception from DHT sensor")
            
            try:
                self.lightLevel = (100* self.adcLight.read_u16() / 65535)
                tmpReading = self.adcCoreTemp.read_u16() * self.conversionFactor
                self.coreTemp = 27 - (tmpReading - 0.706)/0.001721
            except Exception:
                print("exception from computation")

            if self.co2.data_available():
                try:
                    r = self.co2.read_algorithm_results()
                except Exception:
                    print("exception from read out out CO2 sensor")
     
                gcfree = gc.mem_free()
   
                retString = "Temp: {:.1f}C, Humidity: {:.0f}%. CO2={}, tVOC={}, light={:.1f}, coreTmp={:-0.1f} gc {}".format(self.temp, self.hum, r[0], r[1], self.lightLevel, self.coreTemp, gcfree)
                print(retString)
                self.XMLString = "<measurement><temperature>{:.1f}</temperature><humidity>{:.0f}</humidity><co2>{}</co2><tvoc>{}</tvoc><light>{:.1f}</light><core>{:-0.1f}</core><gc>{}</gc></measurement>".format(self.temp, self.hum, r[0], r[1], self.lightLevel, self.coreTemp, gcfree)
        
                if r[0] > 2200:
                    self.LED_CO2.set(0, self.lightLevel)
                else:
                    if r[0] > 1350:
                        #red
                        self.LED_CO2.set(1, self.lightLevel)
                    else:
                        #yellow
                        self.LED_CO2.set(2, self.lightLevel)
                self.measurementLoopNo = self.measurementLoopNo + 1
                
                #treatment of the baseline
                
                #save baselines at day 1, 2, 4, 6 
                if self.measurementLoopNo == 1*(60*24) or self.measurementLoopNo == 2*(60*24) or self.measurementLoopNo == 4*(60*24) or self.measurementLoopNo == 6*(60*24):
                    self.saveBaseline()
                    
                #save baseline on a weekly basis with reset
                if self.measurementLoopNo >= 14*(60*24):
                    self.saveBaseline()
                    #reset one week
                    self.measurementLoopNo = 7*(60*24)
                    
                #modify the parameters after a successfull read session
                if self.updateRegTemHum == True:
                    self.co2.setTempHum(self.temp, self.hum)
                    self.RegHum = self.hum
                    self.RegTemp = self.temp
                    self.updateRegTemHum = False


            if self.hum > 65:
                #red
                self.LED_HUM.set(0, self.lightLevel)
            else:
                if self.hum > 55 :
                    #yellow
                    self.LED_HUM.set(1, self.lightLevel)
                else:
                    #green
                    self.LED_HUM.set(2, self.lightLevel)
            
            if math.fabs(self.RegHum - self.hum) > 2:
                self.updateRegTemHum = True

            if self.temp > 28.0 or self.temp < 16.0:
                #red
                self.LED_TMP.set(0, self.lightLevel)
            else:
                if self.temp > 25.0 or self.temp < 18.0 :
                    #yellow
                    self.LED_TMP.set(1, self.lightLevel)
                else:
                    #green
                    self.LED_TMP.set(2, self.lightLevel)

            if math.fabs(self.RegTemp - self.temp) > 1:
                self.updateRegTemHum = True
        
            time.sleep(1)
            gc.collect()
            
            
