import json
from amqp import amqpmanager, listener
from command.loader import Loader

MODULE_PATH = 'apps.manager.commands'

class ManagerApp(object):
    def __init__(self,connection):
        self.loader = Loader()
        self.loader.scan(MODULE_PATH)
        self.amqp = amqpmanager.AMQPManager(connection, self)
        self.listener = listener.AMQPListener(connection, 'manage_q', self)


    def handle_message(self, message):
        f = self.loader.handlers.get(message.routing_key,None)
        if f:
            if message.body:
                args = json.loads(message.body)
                return f(*args)
            else:
                return f()
        else:
            raise Exception("Couldn't find handler")