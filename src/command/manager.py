import json
from command.loader import Loader
class CommandManager(object):
    def __init__(self):
        self.loader = Loader()
        self.loader.scan()

    def handle_message(self, message):
        f = self.loader.handlers.get(message.routing_key,None)
        if f:
            if message.body:
                args = json.loads(message.body)
                return f(*args)
            else:
                return f()
        else:
            raise Exception("Couldn't handle handler")