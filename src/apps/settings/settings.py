import logging
import json
from gevent import Greenlet
from amqp import connection, amqpmanager
from amqp import amqpconfiguration
from gevent.event import Event
from command.loader import Loader

logger = logging.getLogger('microservices.apps.settings')

MODULE_PATH = 'apps.settings.commands'

class Settings(Greenlet):
    """ Very simple test 'app'
    """
    conn = None
    loader = None
    def __init__(self):
        super(Settings,self).__init__()
        self.event = Event()
        self.conn = None

    def _run(self):
        self.loader = Loader()
        self.loader.scan(MODULE_PATH)

        self.conn = connection.AMQPConnection(self)
        self.conn.connect()
        #self.conn.connection.join()
        self.event.wait()
        self.amqp.close()
        self.conn.close()

    def on_connect(self, connection):
        self.amqp = amqpmanager.AMQPUniqueManager(connection,'settings', self)


    def handle_message(self, message):
        logger.debug("message key [%s] body [%s]" % (message.routing_key,message.body))
        keys = message.routing_key.split('.')
        if keys[0] == 'all' or keys[0] == self.amqp.id:
            route = ".".join(keys[1:])
        else:
            raise Exception("route not found [%s]" % message.routing_key.split)
        f = self.loader.handlers.get(route,None)
        if f:
            if message.body:
                args = json.loads(message.body)
                return f(**args)
            else:
                return f()
        else:
            raise Exception("Couldn't find handler")

def start():
    g = Settings()
    g.start()
