from importlib import import_module
import inspect
import pkgutil

MODULE_PATH = 'command.commands'

class Loader(object):
    """ Command handler loader"""
    def __init__(self):
        self.handlers = {}

    def scan(self):
        """Scan the command handler package and load public functions"""
        pkg = import_module(MODULE_PATH)
        for importer, modname, _ in pkgutil.iter_modules(pkg.__path__):
            mod = import_module(MODULE_PATH + '.' + modname)
            for name, obj in inspect.getmembers(mod):
                if inspect.isfunction(obj) and not name.startswith('_'):
                    self.handlers.setdefault(modname + '.' + name, obj)
