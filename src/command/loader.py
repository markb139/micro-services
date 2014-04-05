from importlib import import_module
import inspect
import pkgutil

class Loader(object):
    def __init__(self):
        self.handlers = {}

    def scan(self):
        pkg = import_module('command.commands')
        for importer, modname, ispkg in pkgutil.iter_modules(pkg.__path__):
            mod = import_module('command.commands.' + modname)
            for name, obj in inspect.getmembers(mod):
                if inspect.isfunction(obj):
                    self.handlers.setdefault(modname + '.' + name, obj)
