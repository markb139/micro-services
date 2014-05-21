def ping():
    from apps.pinger import pinger
    pinger.start()

def settings():
    from apps.settings import settings
    settings.start()

def site():
    from apps.managementsite import manager
    manager.start()
    pass