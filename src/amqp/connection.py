import os
from nucleon.amqp import Connection

class AMQPConnection(object):
    def __init__(self, observer):
        self.observer = observer
        self.conection = Connection(
            os.environ.get('AMQP_URL', 'amqp://guest:guest@localhost/'),
            heartbeat=100
        )
        self.conection.on_connect(self.on_connect)
        self.conection.on_error(self.on_error)

    def connect(self):
        self.conection.connect()

    def on_connect(self,connection):
        self.observer.on_connect(connection)

    def on_error(self,connection):
        pass
