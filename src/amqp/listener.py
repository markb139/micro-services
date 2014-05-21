import json
import logging
import nucleon.amqp.exceptions
from nucleon.amqp import channels

logger = logging.getLogger('microservices.amqp.listener')

class AMQPListener(object):
    """Listen to an AMQP queue"""
    def __init__(self, connection, queue, observer):
        logger.debug("listen to [%s] for [%s]" % (queue,type(observer)))
        self.observer = observer
        self.channel = connection.allocate_channel()
        self.channel.basic_consume( queue=queue,
                                    no_local=False,
                                    no_ack=False,
                                    exclusive=False,
                                    arguments={},
                                    callback=self.on_message)

    def close(self):
        self.channel.close()

    def on_message(self, message):
        if type(message) == nucleon.amqp.exceptions.ConnectionError:
            return
        elif type(message) == nucleon.amqp.exceptions.ChannelClosed:
            return
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
            logger.error(err)
            message.reject(requeue=False)
