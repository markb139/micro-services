def ensure_exchanges(channel, exchanges):
    """Create exchanges based on incoming dictionary objects"""
    for exchange in exchanges:
        if exchange.get('alternate-exchange',None):
            arguments= {
                'alternate-exchange': exchange.get('alternate-exchange',None)
            }
        else:
            arguments= {}

        channel.exchange_declare(
            exchange = exchange['name'],
            type = exchange['type'],
            durable = True,
            arguments = arguments
        )

def ensure_queues(channel, queues):
    """Create queues based on incoming dictionary objects"""
    for queue in queues:
        if queue.get('x-dead-letter-exchange',None):
            arguments= {
                'x-dead-letter-exchange': queue.get('x-dead-letter-exchange',None)
            }
        else:
            arguments= {}

        channel.queue_declare(
                queue = queue['name'],
                durable = queue['durable'],
                arguments = arguments
        )

def ensure_bindings(channel, bindings):
    """Create exchange bindings based on incoming disctionary objects"""
    for binding in bindings:
        channel.queue_bind(
            queue=binding['queue'],
            exchange=binding['exchange'],
            routing_key=binding['key'],
        )

