import logging

logger = logging.getLogger('microservices.amqp.sender')


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class AMQPSender(object):
    __metaclass__ = Singleton

    def __init__(self):
        pass
    def __init__(self, connection):
        self.channel = connection.allocate_channel()

    def send(self, exchange, key, object):
        try:
            route = str(key)
            body = str(object)
            self.channel.basic_publish(
                    exchange=exchange,
                    routing_key=route,
                    body=body,
                )
        except Exception as err:
            pass

