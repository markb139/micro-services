import os
from nucleon.amqp import Connection

class AMQPConnection(object):
    """
    Manage AMQP connections
    """
    def __init__(self, observer):
        self.observer = observer
        self.connection = Connection(
            os.environ.get('AMQP_URL', 'amqp://guest:guest@localhost/'),
            heartbeat=100
        )
        self.connection.on_connect(self.on_connect)
        self.connection.on_error(self.on_error)

    def connect(self):
        self.connection.connect()

    def on_connect(self,connection):
        self.observer.on_connect(connection)

    def on_error(self,connection):
        """No error handling yet !"""
        pass
