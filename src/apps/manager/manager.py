import logging
from amqp.appmanager import AppManager
import socket
import json
from importlib import import_module
import gevent
import uuid

logger = logging.getLogger('microservices.apps.manager')

MODULE_PATH = 'apps.manager.commands'

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class ManagerApp(AppManager):
    __metaclass__ = Singleton

    def __init__(self,connection, apps_to_start):
        super(ManagerApp, self).__init__(MODULE_PATH, connection)
        self.running = []
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
        info = {}
        info['id'] = self.amqp.id
        info['name'] = 'apps.manager.manager'
        info['running'] = True
        info['hostname'] = socket.gethostname()
        info['commands'] =[]
        for handler in self.loader.handlers:
            info['commands'].append(handler)

        self.build_startup_apps(apps_to_start)
        self.launch_apps()
        # broadcast this management app's status
        self.broadcast_app_status(info)

    def greenlet_exit(self, greenlet):
        try:
            for app in self.running:
                if app['greenlet'] == greenlet:
                    logger.debug("found greenlet")
                    app['running'] = False
                    self.broadcast_app_status(app)
        except Exception as err:
            logger.error("Error marking app closed %s" % err)


    def build_startup_apps(self, apps_to_start):
        # find the apps to start
        for app in apps_to_start:
            self.build_start_app(app)

    def build_start_app(self, app):
        pkg = import_module(app)
        try:
            greenlet_func = getattr(pkg,'greenlet')
            if greenlet_func:
                id = str(uuid.uuid4())
                greenlet = greenlet_func(id)
                new_app = {
                    'greenlet': greenlet,
                    'name': app,
                    'id': id
                }
                self.running.append(new_app)
        except Exception as err:
            logger.error("Getting greenlet %s" % err)

    def launch_apps(self):
        # start the apps
        for app in self.running:
            if not app.get('running', False):
                greenlet = app['greenlet']
                greenlet.link(self.greenlet_exit)
                greenlet.start()
                app['running'] = True
                gevent.sleep(1)
                self.broadcast_app_status(app)

    def launch(self, app):
        pkg = import_module(app)
        try:
            greenlet_func = getattr(pkg,'greenlet')
            if greenlet_func:
                id = str(uuid.uuid4())
                greenlet = greenlet_func(id)
                new_app = {
                    'greenlet': greenlet,
                    'name': app,
                    'id': id
                }
                self.running.append(new_app)
                self.launch_apps()
        except Exception as err:
            logger.error("Getting greenlet %s" % err)


    def broadcast_app_status(self,app):
        info = {
            'name': app['name'],
            'id': app['id'],
            'running': app['running']
        }
        self.amqp.channel.basic_publish(
                exchange='manage',
                routing_key='manager.app.status',
                body=json.dumps(info)
            )
