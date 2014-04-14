import logging

logger = logging.getLogger('microservices.apps.settings')

_settings = {}

def set(key,value):
    logger.debug("set key [%s] value [%s]" % (key,value))
    _settings[key] = value

def get(key):
    return {'value': _settings[key] }