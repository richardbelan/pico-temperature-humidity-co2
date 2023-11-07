import network
import socket
import time
import rp2
import MeasureCtrl

class TempServer:
    def __init__(self, measCtrl):
        try:
            self.ssid = '963bzpgn'
            self.password = '7grn6tkm'
            #self.webContent = """<!DOCTYPE html>
            #                     <html>
            #                        <head> <title>Temp Humidity CO2 server</title> </head>
            #                        <body>
            #                            <h1>Temperature, Humidity and CO2 sensor</h1>
            #                            <p>%s</p>
            #                        </body>
            #                     </html>
            #                  """
            self.webContent = """<?xml version="1.0" encoding="UTF-8"?>
                             %s
                          """
            #Denmark
            rp2.country('DK')
            self.MC = measCtrl
            
        except:
            print('execption upon start-up')

        
    def initialize(self):
        try:
            self.wlan = network.WLAN(network.STA_IF)
            self.wlan.active(True)
            return True
        except:
            print('exception during initializing')
            return False
        
    def connectToNetworkInfrastructure(self):
        try:
            print('Initializing connection to infrastructure...')
            #if self.wlan.isconnected():
            #    self.wlan.disconnect()
            
            self.wlan.connect(self.ssid, self.password)
        
            # Wait for connect or fail
            max_wait = 10
            while max_wait > 0:
                if self.wlan.status() < 0 or self.wlan.status() >= 3:
                    break
            max_wait -= 1
            print('waiting for connection...')
            time.sleep(1)

            # Handle connection error
            if self.wlan.status() != 3:
                raise RuntimeError('network connection failed')
            else:
                print('connected')
                status = self.wlan.ifconfig()
                print( 'ip = ' + status[0] )
            return True
        except:
            print('exception during infrastructire connection')
            return False

    def listen(self):
        try:
            addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
            self.s = socket.socket()
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.s.bind(addr)
            self.s.listen(1)

            print('listening on', addr)
            return True
        except:
            print('exception during listening')
            return False
        
    def acceptConnections(self):
        # Listen for connections
        while True:
            try:
                cl, addr = self.s.accept()
                cl.setblocking(False)
                time.sleep(1) # 1s
                
                request = cl.recv(2048)
                print('client connected from', addr)
                
                if request:
                    print('client connected from', addr)
                
                    print(request)
                #request = str(request)
                
                #findCmd = request.find('/measurement')
                #stateis = "--"
                
                #if findCmd >= 0:
                #    print("measurement request")
                    stateis = self.MC.getData()

                    response = self.webContent % stateis
                    cl.send('HTTP/1.1 200 OK\r\nContent-type: application/xml\r\n\r\n')
                    cl.send(response)
                    
                cl.close()
        
            except:
                cl.close()
                print('connection closed')
                time.sleep(5) # 5s
    