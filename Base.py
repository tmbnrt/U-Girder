'''
Base class "grandfather class"
'''
from datetime import datetime as time

class Base:

    #class properties
    _log = "profile.log"
    _counter = 0            #count instances

    # constructor
    def __init__(self,log = ""):
        if len(log)>0: Base._log = log


        Base._counter += 1
        self.appendLog("%d instances available." % Base._counter)

    # destructor
    def __del__(self):
        self.appendLog("delete object %d...."% Base._counter)
        Base._counter -= 1

    # write something to the log
    def appendLog(self,text):
        t = time.now()
        tstamp = "%2.2d.%2.2d.%2.2d " % (t.hour,t.minute,t.second)
        message = tstamp + text

        f = open(Base._log,"a")
        f.write(message + "\n")
        print message
