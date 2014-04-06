from amqp import connection, amqpmanager
from command import manager

class Manager(object):
    def __init__(self):
        self.listener = None
        self.manager = None
        conn = connection.AMQPConnection(self)
        conn.connect()
        try:
            conn.conection.join()
        except KeyboardInterrupt:
            conn.conection.close()

    def on_connect(self, connection):
        self.manager = manager.CommandManager()
        self.amqp = amqpmanager.AMQPManager(connection, self.manager)


m = Manager()