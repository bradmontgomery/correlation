''' This module defines a Timer class that 
    can be used to time code execution.

    This module uses python's time.time() 
    function which returns a float representing 
    UTC time in seconds since the epoch 

    Example:
        t = Timer()
        t.start()
        ...
        t.end()
        print t.diff()
'''
import time
class Timer(object):
    def __init__(self):
        self.s = 0.0
        self.e = 0.0
        self.d = 0.0
    def start(self):
        self.s = time.time()
    def end(self):
        self.e = time.time()
    def stop(self):
        self.e = time.time()
    def diff(self):
        self.d = self.e - self.s
        return self.d
