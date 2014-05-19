import os
import json
import logging
import uuid
import gevent

from nucleon.amqp import Connection

logging.basicConfig()
logger = logging.getLogger('test_management_observer')
logger.setLevel(logging.DEBUG)


conn = Connection(
    os.environ.get('AMQP_URL', 'amqp://guest:guest@localhost/'),
    heartbeat=5
)

@conn.on_connect
def on_connect(conn):
    # send some test messages
    with conn.channel() as channel:
        def on_message(message):
            logger.debug(message.routing_key)
            message.ack()
            pass

        queue = channel.queue_declare(exclusive=True)
        channel.queue_bind(
            queue=queue.queue,
            exchange='manage',
            routing_key='manager.#',
        )

        channel.basic_consume( queue=queue.queue,
                                    no_local=False,
                                    no_ack=False,
                                    exclusive=False,
                                    arguments={},
                                    callback=on_message
                                    )
        while True:
            gevent.sleep(1)
    conn.close()
if __name__ == '__main__':
    conn.connect()

    try:
        conn.join()
    except KeyboardInterrupt:
        conn.close()