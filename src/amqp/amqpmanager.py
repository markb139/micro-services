import logging
from amqp import amqpconfiguration, listener
import uuid

logger = logging.getLogger('microservices.amqp.manager')

class AMQPManager(object):
    def __init__(self, connection, observer):
        logger.debug("observer %s" % type(observer))
        self.observer = observer
        channel = connection.allocate_channel()
        exchanges = [{
                'name' : 'manage',
                'type' : 'topic',
                'durable': True,
                'alternate-exchange': 'error'
            },
            {
                'name' : 'error',
                'type' : 'topic',
                'durable': True,
            },
        ]
        amqpconfiguration.ensure_exchanges(channel,exchanges)
        queues = [{
                'name': 'manage_q',
                'durable': True,
                'x-dead-letter-exchange': 'error'
            },
            {
                'name': 'error_q',
                'durable': True
            }
        ]
        amqpconfiguration.ensure_queues(channel, queues)

        bindings = [{
                'queue': 'manage_q',
                'exchange': 'manage',
                'key': '#'
            },
            {
                'queue': 'error_q',
                'exchange': 'error',
                'key': '#'
            },
            {
                'queue': 'error_q',
                'exchange': 'error',
                'key': '#'
            }
        ]

        amqpconfiguration.ensure_bindings(channel, bindings)
        # start listening to the manage_q queue for management commands
        channel.close()

class AMQPUniqueManager(object):
    """ amqp manager for the pinger app
    sets up an exclusive queue for an instance and binds it to the pinger exchange
    """
    def __init__(self, connection):
        self.id = str(uuid.uuid4())
        self.connection = connection
        self.channel = connection.allocate_channel()

    def bind(self,exchange, bindings):
        exchanges = [{
                'name' : exchange,
                'type' : 'topic',
                'durable': True,
                'alternate-exchange': 'error'
            },
        ]
        amqpconfiguration.ensure_exchanges(self.channel,exchanges)
        for binding in bindings:
            queue = self.channel.queue_declare(exclusive=True)
            binding['queue'] = queue.queue
            amqpconfiguration.ensure_bindings(self.channel, [binding])
            self.listener = listener.AMQPListener(self.connection, queue.queue, binding['observer'])

    def close(self):
        self.channel.close()

