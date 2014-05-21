import os
import json
import logging
import uuid
import gevent

from nucleon.amqp import Connection

logging.basicConfig()
logger = logging.getLogger('test_app')
logger.setLevel(logging.DEBUG)


conn = Connection(
    os.environ.get('AMQP_URL', 'amqp://guest:guest@localhost/'),
    heartbeat=5
)

@conn.on_connect
def on_connect(conn):
    # send some test messages
    with conn.channel() as channel:
        channel.basic_publish(
                exchange='manage',
                routing_key='all.apps.launch',
                body='{"application": "apps.pinger.pinger"}',
            )

    gevent.sleep(3.0)
    conn.close()

if __name__ == '__main__':
    conn.connect()

    try:
        conn.join()
    except KeyboardInterrupt:
        conn.close()