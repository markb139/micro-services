from importlib import import_module
import inspect
import pkgutil
import logging

logger = logging.getLogger('microservices.command.loader')

MODULE_PATH = 'command.commands'

class Loader(object):
    """ Command handler loader"""
    def __init__(self):
        self.handlers = {}

    def scan(self, path = MODULE_PATH):
        """Scan the command handler package and load public functions"""
        logger.debug("scan %s" % path)
        pkg = import_module(path)
        for importer, modname, _ in pkgutil.iter_modules(pkg.__path__):
            mod = import_module(path + '.' + modname)
            for name, obj in inspect.getmembers(mod):
                if inspect.isfunction(obj) and not name.startswith('_'):
                    logger.debug("modname [%s] func [%s]" % (modname,name))
                    self.handlers.setdefault(modname + '.' + name, obj)
