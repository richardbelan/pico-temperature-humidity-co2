import MeasureCtrl
import TempServer

import _thread, machine

MC = MeasureCtrl.MeasureCtrl()
TS = TempServer.TempServer(MC)

MC.initialize()

def core1Task():
   TS.acceptConnections()
                
TS.initialize()
if TS.connectToNetworkInfrastructure():
    if TS.listen():
        _thread.start_new_thread(core1Task, ())

MC.measure()

