import os
import json
import uuid
import gevent

from nucleon.amqp import Connection


conn = Connection(
    os.environ.get('AMQP_URL', 'amqp://guest:guest@localhost/'),
    heartbeat=5
)

@conn.on_connect
def on_connect(conn):
    # send some test messages
    with conn.channel() as channel:
        msg = {
            'filter': []
        }
        def on_rpc_message(message):
            pass
        corr_id = str(uuid.uuid4())
        rpc_queue = channel.queue_declare(exclusive=True)
        channel.basic_consume( queue=rpc_queue.queue,
                                    no_local=False,
                                    no_ack=False,
                                    exclusive=False,
                                    arguments={},
                                    callback=on_rpc_message
                                    )

        # settings = {
        #     'key': 'test_key',
        #     'value': 'hello, world'
        # }
        # settingsObj = json.dumps(settings)
        # channel.basic_publish(
        #         exchange='settings',
        #         routing_key='all.setting.set',
        #         body=settingsObj,
        #         headers={
        #             'delivery_mode': 2,
        #         }
        #     )

        settings = {
            'key': 'test_key',
        }
        settingsObj = json.dumps(settings)
        channel.basic_publish(
                exchange='settings',
                routing_key='all.setting.get',
                body=settingsObj,
                headers={
                    'delivery_mode': 2,
                    'reply_to': rpc_queue.queue,
                    'correlation_id': corr_id
                }
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