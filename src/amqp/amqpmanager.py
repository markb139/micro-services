import uuid
from amqp import listener

class AMQPManager(object):
    def __init__(self, connection, observer):
        self.observer = observer
        self.id = str(uuid.uuid4())

        self.rpc_queue = None
        channel = connection.allocate_channel()
        self.ensure_exchanges(channel)
        self.ensure_queues(channel)
        self.ensure_bindings(channel)
        self.listener = listener.AMQPListener(connection,self)
        channel.close()

    def handle_message(self, message):
        if message.routing_key.startswith(self.id):
            self.observer.handle_message(message, message.routing_key[len(self.id) + 1:])
        else:
            self.observer.handle_message(message,message.routing_key)

    def ensure_exchanges(self, channel):
        channel.exchange_declare(
                exchange='manage',
                type='topic',
                durable=True,
                arguments= {
                    'alternate-exchange': 'error'
                }
        )
        channel.exchange_declare(
                exchange='error',
                type='topic',
                durable=True,
        )

    def ensure_queues(self, channel):
        channel.queue_declare(
            queue='manage_q',
            durable=True,
            arguments={
                'x-dead-letter-exchange': 'error'
            }
        )
        channel.queue_declare(
            queue='error_q',
            durable=True
        )
        self.rpc_queue = channel.queue_declare(exclusive=True)

    def ensure_bindings(self, channel):
        channel.queue_bind(
            queue='manage_q',
            exchange='manage',
            routing_key='#'
        )
        channel.queue_bind(
            queue='error_q',
            exchange='error',
            routing_key='#'
        )
        channel.queue_bind(
            queue=self.rpc_queue.queue,
            exchange='manage',
            routing_key='%s.#' % self.id
        )
