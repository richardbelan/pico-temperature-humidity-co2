class LogFile:
    def __init__(self, fileName):
        self.fileName = fileName
        
    def write(self, txt):
        try:
            f = open(self.fileName, 'a+')
            f.write(txt)
            f.write('\n')
            f.close()
        except:
            print("err")