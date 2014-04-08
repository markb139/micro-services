import json

class AMQPListener(object):
    def __init__(self, connection, queue, observer):
        self.observer = observer
        self.channel = connection.allocate_channel()
        self.channel.basic_consume( queue=queue,
                                    no_local=False,
                                    no_ack=False,
                                    exclusive=False,
                                    arguments={},
                                    callback=self.on_message)

    def on_message(self, message):
        try:
            ret = self.observer.handle_message(message)
            if message.headers.get('reply_to',None):
                self.channel.basic_publish(exchange='',
                    routing_key = message.headers.get('reply_to',None),
                    body = json.dumps(ret),
                    headers={
                    'correlation_id': message.headers.get('correlation_id',None)
                }
            )

            message.ack()
        except Exception as err:
            message.reject(requeue=False)
