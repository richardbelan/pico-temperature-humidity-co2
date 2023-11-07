
class Calibrate:
    def __init__(self, offset):
        self.Offset = offset
    
    def convert(self, val):
        return val + self.Offset

            
            
        
        
