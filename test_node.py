from amqp import connection
from apps.manager import manager
import logging

logging.basicConfig()

logger = logging.getLogger('microservices')
logger.setLevel(logging.DEBUG)

class Manager(object):
    manager = None
    def __init__(self):
        self.manager = None
        conn = connection.AMQPConnection(self)
        conn.connection.connect()
        try:
            conn.connection.join()
        except KeyboardInterrupt:
            conn.connection.close()

    def on_connect(self, connection):
        apps_to_start = []
        self.manager = manager.ManagerApp(connection, apps_to_start)

if __name__ == '__main__':
    logger.debug("Starting")
    m = Manager()