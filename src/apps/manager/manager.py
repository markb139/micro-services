import json
import logging
from amqp import amqpmanager, listener
from command.loader import Loader

logger = logging.getLogger('microservices.apps.manager')

MODULE_PATH = 'apps.manager.commands'

class ManagerApp(object):
    def __init__(self,connection):
        self.loader = Loader()
        self.loader.scan(MODULE_PATH)
        #self.amqp = amqpmanager.AMQPManager(connection, self)
        #self.listener = listener.AMQPListener(connection, 'manage_q', self)
        self.amqp = amqpmanager.AMQPUniqueManager(connection,'manage', self)


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