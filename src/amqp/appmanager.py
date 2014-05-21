import json
from command.loader import Loader
from amqp import amqpmanager
import logging

logger = logging.getLogger('microservices.appmanager')

class AppManager(object):
    def __init__(self, path, connection):
        self.loader = Loader()
        self.loader.scan(path)
        self.amqp = amqpmanager.AMQPUniqueManager(connection)

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