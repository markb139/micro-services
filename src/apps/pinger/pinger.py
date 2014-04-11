import uuid
import gevent
from gevent import Greenlet
from amqp import connection, listener
from amqp import amqpconfiguration
from gevent.event import Event

class PingerAMQPManager(object):
    """ amqp manager for the pinger app
    sets up an exclusive queue for an instance and binds it to the pinger exchange
    """
    def __init__(self, connection, observer):
        self.id = str(uuid.uuid4())
        self.channel = connection.allocate_channel()
        self.rpc_queue = self.rpc_queue = self.channel.queue_declare(exclusive=True)
        exchanges = [{
                'name' : 'pinger',
                'type' : 'topic',
                'durable': True,
                'alternate-exchange': 'error'
            },
        ]
        amqpconfiguration.ensure_exchanges(self.channel,exchanges)
        bindings = [{
                'queue': self.rpc_queue.queue,
                'exchange': 'pinger',
                #'key': self.id + '.#'
                'key' : '#'
            },
        ]
        amqpconfiguration.ensure_bindings(self.channel, bindings)
        self.listener = listener.AMQPListener(connection, self.rpc_queue.queue, observer)


    def close(self):
        #self.listener.close()
        #self.rpc_queue.close()
        self.channel.close()

class Pinger(Greenlet):
    """ Very simple test 'app'
    """
    def __init__(self):
        super(Pinger,self).__init__()
        self.event = Event()
        self.conn = None
    def _run(self):
        self.conn = connection.AMQPConnection(self)
        self.conn.connect()
        #self.conn.connection.join()
        self.event.wait()
        self.amqp.close()
        self.conn.close()

    def on_connect(self, connection):
        self.amqp = PingerAMQPManager(connection, self)

    def handle_message(self, message):
        if message.routing_key == 'pinger.exit':
            #self.conn.connection.close()
            self.event.set()

def start():
    g = Pinger()
    g.start()
