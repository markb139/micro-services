from gevent import Greenlet
from amqp import connection, listener
from amqp import amqpconfiguration
from gevent.event import Event
import gevent

import logging

logger = logging.getLogger('microservices.apps.pinger')

class PingerAMQPManager(object):
    """ amqp manager for the pinger app
    sets up an exclusive queue for an instance and binds it to the pinger exchange
    """
    def __init__(self, connection, observer, id):
        self.id = id
        self.channel = connection.allocate_channel()
        self.observer = observer
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
                'key': self.id + '.#'
            },
            {
                'queue': self.rpc_queue.queue,
                'exchange': 'pinger',
                'key': 'all.#'
            }
        ]
        amqpconfiguration.ensure_bindings(self.channel, bindings)
        self.listener = listener.AMQPListener(connection, self.rpc_queue.queue, self.observer)


    def close(self):
        self.listener.close()
        self.channel.close()

class Pinger(Greenlet):
    """ Very simple test 'app'
    """
    def __init__(self, id):
        super(Pinger,self).__init__()
        self.event = Event()
        self.conn = None
        self.id = id

    def _run(self):
        logger.debug("Pinger starting")
        self.conn = connection.AMQPConnection(self)
        self.conn.connect()
        #self.conn.connection.join()
        self.event.wait()
        logger.debug("Pinger exiting")
        self.amqp.close()
        self.conn.close()

    def on_connect(self, connection):
        self.amqp = PingerAMQPManager(connection, self, self.id)

    def handle_message(self, message):
        if message.routing_key.endswith('pinger.exit'):
            #self.conn.connection.close()
            self.event.set()

def start():
    g = Pinger()
    g.start()

class Application(Greenlet):
    def __init__(self, id):
        super(Application,self).__init__()
        self.pinger = Pinger(id)
        self.exit_exceptions = []

    def _run(self):
        # start the handler and site
        #self.pinger.link(self.app_handler)
        self.pinger.start()
        # wait for apps to exit
        gevent.joinall([self.pinger], raise_error=True)
        if self.exit_exceptions:
            raise self.exit_exceptions[0]

    def app_handler(self, source):
        if source.exception:
            self.exit_exceptions.append(source.exception)
        if not self.pinger.dead:
            self.pinger.kill()
        pass

def greenlet(id):
    # get the owning greenlet
    return Application(id)