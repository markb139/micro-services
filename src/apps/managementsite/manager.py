from amqp.appmanager import AppManager
from gevent import Greenlet
from amqp import connection, listener
from gevent.event import Event
import gevent
import json
from .site import Site
import logging

logger = logging.getLogger('microservices.apps.managementsite')
MODULE_PATH = 'apps.managementsite.commands'

class Managers(object):
    def __init__(self):
        self.managers = {}
        self.observer = None

    def observe(self, observer):
        self.observer = observer

    def append(self, manager):
        id = manager.get('id','NOID')
        self.managers[id] = manager
        self.observer.update()

managers = Managers()

class ManagerSite(AppManager):
    """ amqp manager for the pinger app
    sets up an exclusive queue for an instance and binds it to the pinger exchange
    """
    def __init__(self,connection):
        super(ManagerSite, self).__init__(MODULE_PATH, connection)
        bindings = [
        {
            'observer': self,
            'exchange': 'manage',
            'key' : 'manager.#'
        }]
        self.amqp.bind('manage', bindings)
        pass

    def handle_message(self, message):
        logger.debug("handle_message %s : %s" % (message.routing_key,message.body))
        data = json.loads(message.body)
        managers.append(data)
        pass

    def close(self):
        self.listener.close()
        self.channel.close()


class CommandHandler(Greenlet):
    """ Very simple test 'app'
    """
    def __init__(self, id):
        super(CommandHandler,self).__init__()
        self.event = Event()
        self.conn = None
        self.id = id

    def _run(self):
        self.conn = connection.AMQPConnection(self)
        self.conn.connect()
        # blocked after this until exit command
        self.event.wait()
        self.amqp.close()
        self.conn.close()

    def on_connect(self, connection):
        try:
            self.amqp = ManagerSite(connection)
        except Exception as err:
            logger.error(err)
            pass

def start():
    g = CommandHandler()
    g.start()
    site = Site(managers)
    site.start()

class Application(Greenlet):
    def __init__(self, id):
        super(Application,self).__init__()
        self.handler = CommandHandler(id)
        self.site= Site(managers)
        self.exit_exceptions = []

    def _run(self):
        # start the handler and site
        self.handler.link(self.app_handler)
        self.site.link(self.app_handler)
        self.handler.start()
        self.site.start()
        # wait for apps to exit
        gevent.joinall([self.handler,self.site])
        if self.exit_exceptions:
            raise self.exit_exceptions[0]

    def app_handler(self, source):
        if source.exception:
            self.exit_exceptions.append(source.exception)
        if not self.handler.dead:
            self.handler.kill()
        if not self.site.dead:
            self.site.kill()
        pass

def greenlet(id):
    # get the owning greenlet
    return Application(id)