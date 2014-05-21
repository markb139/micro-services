from gevent import Greenlet
from gevent.event import Event
import gevent
from flask import Flask
from flask import render_template, jsonify
from gevent.wsgi import WSGIServer
import time

import logging

logger = logging.getLogger('microservices.apps.managementsite.site')

class Site(Greenlet):
    def __init__(self, managers):
        super(Site,self).__init__()
        self.event = Event()
        self.event.clear()
        self.managers = managers
        self.managers.observe(self)

    def update(self):
        self.event.set()

    def _run(self):
        logger.debug("Site started")
        app = Flask(__name__)

        @app.route('/', methods=['GET'])
        def index():
            return render_template('index.html')

        @app.route('/data', methods=['GET'])
        def data():
            now = time.time()
            d = {'contents':[]}

            apps = [value for key,value in self.managers.managers.iteritems() if value['running']]
            d['contents'] = apps
            return jsonify(d)

        @app.route('/updated', methods=['GET'])
        def updated():
            self.event.wait(5.0)
            self.event.clear()
            return 'changed!'

        self.new_data = False
        http_server = WSGIServer(('', 5000), app)
        http_server.serve_forever()
