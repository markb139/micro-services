def list():
    apps = ['pinger','site']
    return apps
# {"application": "apps.pinger.pinger"}
def launch(application):
    from ..manager import ManagerApp
    manager = ManagerApp()
    manager.launch(application)