import uuid
from gevent import Greenlet
from amqp import connection, listener
from amqp import amqpconfiguration

class PingerAMQPManager(object):
    """ amqp manager for the pinger app
    sets up an exclusive queue for an instance and binds it to the pinger exchange
    """
    def __init__(self, connection, observer):
        self.id = str(uuid.uuid4())
        channel = connection.allocate_channel()
        self.rpc_queue = self.rpc_queue = channel.queue_declare(exclusive=True)
        exchanges = [{
                'name' : 'pinger',
                'type' : 'topic',
                'durable': True,
                'alternate-exchange': 'error'
            },
        ]
        amqpconfiguration.ensure_exchanges(channel,exchanges)
        bindings = [{
                'queue': self.rpc_queue.queue,
                'exchange': 'pinger',
                'key': self.id + '.#'
            },
        ]
        amqpconfiguration.ensure_bindings(channel, bindings)
        self.listener = listener.AMQPListener(connection, self.rpc_queue.queue, observer)
        channel.close()


class Pinger(Greenlet):
    """ Very simple test 'app'
    """
    def __init__(self):
        super(Pinger,self).__init__()
        self.conn = None
    def _run(self):
        self.conn = connection.AMQPConnection(self)
        self.conn.connect()
        self.conn.conection.join()
        self.conn.conection.close()

    def on_connect(self, connection):
        self.amqp = PingerAMQPManager(connection, self)

    def handle_message(self, message):
        pass
    
def start():
    g = Pinger()
    g.start()
