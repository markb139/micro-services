import logging
from amqp.appmanager import AppManager
from info import info
import socket

logger = logging.getLogger('microservices.apps.manager')

MODULE_PATH = 'apps.manager.commands'

class ManagerApp(AppManager):
    def __init__(self,connection):
        super(ManagerApp, self).__init__(MODULE_PATH, connection)
        info['id'] = self.amqp.id
        info['hostname'] = socket.gethostname()
        bindings = [{
            'observer': self,
            'exchange': 'manage',
            'key' : self.amqp.id + '.#'
        },
        {
            'observer': self,
            'exchange': 'manage',
            'key' : 'all.#'
        }]
        self.amqp.bind('manage', bindings)
        self.amqp.channel.basic_publish(
                exchange='manage',
                routing_key='manager.' + self.amqp.id + '.online',
                body='',
            )

