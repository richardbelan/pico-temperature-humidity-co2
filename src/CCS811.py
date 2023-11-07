import time
from machine import I2C

_ADDR = 0x5A

class CCS811:
    def __init__(self, i2c: I2C):
        self._i2c = i2c
        
    def setup(self, baseline):
        print("setup CCS811")
        self.multi_write_register(0xFF, b"\x11\xE5\x72\x8A")  # RESET
        time.sleep_ms(100)

        self.check_for_status_error()
        self.app_valid()
        
        HWVersion = self.read_register(0x21)
        HWVersionMajor = (HWVersion[0] >> 4) & 0xF
        HWVersionMinor = HWVersion[0] & 0xF
        print("HW version: {}.{}".format(HWVersionMajor, HWVersionMinor))
        FWVersion = self.read_register(0x23)
        FWVersionMajor = (FWVersion[0] & 0xF0) >> 4
        FWVersionMinor = FWVersion[0] & 0xF
        print("FW version: {}.{}".format(FWVersionMajor, FWVersionMinor))
        

        self._i2c.writeto_mem(_ADDR, 0xF4, b"")  # APP_START
        time.sleep_ms(100)
        self.set_driver_mode(3)
        time.sleep_ms(100)
        if baseline is not None:
            self.writeBaseline(baseline)

    def data_available(self) -> bool:
        v = self._i2c.readfrom_mem(_ADDR, 0x00, 1)
        if v[0] & 1:
            e = self.read_register(0xE0)
            print("error register", hex(e[0]))
        return (v[0] & 1 << 3) > 0

    def check_for_status_error(self) -> bool:
        v = self.read_register(0x00)
        return (v[0] & 1 << 0) > 0

    def app_valid(self):
        v = self.read_register(0x00)
        return (v[0] & 1 << 4) > 0

    def set_driver_mode(self, mode: int):
        v = self.read_register(0x01)  # MEAS_MODE
        v = v[0]
        v &= ~(0b00000111 << 4)  # Clear DRIVE_MODE bits
        v |= mode << 4  # Mask in mode
        self.write_register(0x01, v)

    def read_algorithm_results(self):
        v = self.multi_read_register(0x02, 4)  # ALG_RESULT_DATA
        co2 = v[0] << 8 | v[1]
        t_voc = v[2] << 8 | v[3]
        return co2, t_voc

    def write_register(self, offset: int, value: int):
        return self._i2c.writeto_mem(_ADDR, offset, bytes([value]))

    def read_register(self, offset: int):
        return self._i2c.readfrom_mem(_ADDR, offset, 1)

    def multi_write_register(self, offset: int, data: bytes):
        self._i2c.writeto_mem(_ADDR, offset, data)

    def multi_read_register(self, offset: int, length: int):
        return self._i2c.readfrom_mem(_ADDR, offset, length)

    def status(self):
        b = self._i2c.readfrom(_ADDR, 1)
        return b[0]
    
    def setTempHum(self, _temp, _hum):
        hum_fraction = int(_hum * 512)
        #print("hum fraction {:.0f} {}".format(_hum, hum_fraction))
        temp_fraction = int((_temp + 25) *512)
        #print("temp fraction {} {}".format(_temp, temp_fraction))
        v1 = (hum_fraction >> 8) & 0xFF
        v2 = hum_fraction & 0xFF
        v3 = (temp_fraction >> 8) & 0xFF
        v4 = temp_fraction & 0xFF
        bt = bytes([v1, v2, v3, v4])
        print("set {} {} {} {}".format(hex(bt[0]), hex(bt[1]), hex(bt[2]), hex(bt[3])))
        
        self.multi_write_register(0x5, bt)
        #self.multi_write_register
        
    def readBaseline(self):
        baseline = self.multi_read_register(0x11, 2)
        print("baseline read from chip: {} {}".format(hex(baseline[0]), hex(baseline[1])))
        return baseline
    
    def writeBaseline(self, baseline):
        self.multi_write_register(0x11, baseline)
        print("baseline written to chip: {} {}".format(hex(baseline[0]), hex(baseline[1])))
        
        return None
