import gevent
from gevent import Greenlet

class Pinger(Greenlet):
    def __init__(self):
        super(Pinger,self).__init__()

    def _run(self):
        while True:
            gevent.sleep(1)

def start():
    g = Pinger()
    g.start()
