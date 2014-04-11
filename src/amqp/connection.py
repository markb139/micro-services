import os
import logging
from nucleon.amqp import Connection

logger = logging.getLogger('microservices.amqp.connection')

class AMQPConnection(object):
    """
    Manage AMQP connections
    """
    connection = None
    def __init__(self, observer):
        logger.debug("observer %s" % type(observer))
        self.observer = observer
        self.connection = Connection(
            os.environ.get('AMQP_URL', 'amqp://guest:guest@localhost/'),
            heartbeat=100
        )
        self.connection.on_connect(self.on_connect)
        self.connection.on_error(self.on_error)

    def connect(self):
        logger.debug("connect")
        self.connection.connect()

    def close(self):
        try:
            self.connection.close()
        except Exception as err:
            pass


    def on_connect(self,connection):
        self.observer.on_connect(connection)

    def on_error(self,connection):
        """No error handling yet !"""
        pass
