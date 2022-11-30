from MicroWebSrv2 import *
from time         import sleep

mws2 = MicroWebSrv2()
mws2.StartManaged()

# Main program loop until keyboard interrupt,
try :
    while True :
        sleep(1)
except KeyboardInterrupt :
    mws2.Stop()