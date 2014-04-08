from amqp import listener
from amqp import amqpconfiguration

class AMQPManager(object):
    def __init__(self, connection, observer):
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
        self.listener = listener.AMQPListener(connection, 'manage_q', self)
        channel.close()

    def handle_message(self, message):
        self.observer.handle_message(message,message.routing_key)