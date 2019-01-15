#
# Flask-Browsersync
#
# Copyright (C) 2019 Boris Raicheff
# All rights reserved
#


import functools
import logging
import threading
import time
import urllib.request


logger = logging.getLogger('Flask-Browsersync')


class Browsersync(object):
    """
    Flask-Browsersync

    https://pypi.python.org/pypi/flask-browsersync

    https://flask-browsersync.readthedocs.io

    :param app: Flask app to initialize with. Defaults to `None`
    """

    # https://browsersync.io/docs/http-protocol
    # https://github.com/lepture/python-livereload

    scheme = None

    host = None

    port = None

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        config = tuple(
            app.config.get(name) for name in ('PREFERRED_URL_SCHEME', 'SERVER_NAME', 'BROWSERSYNC_PORT')
        )
        if not all(config):
            logger.debug('Flask-Browsersync not configured')
            return
        self.scheme, self.host, self.port = config
        app.add_template_global(functools.partial(_render_browsersync, self.port), 'browsersync')
        app.url_defaults(_timestamp_static_file)
        app.extensions['browsersync'] = self

    def reload(self):
        threading.Thread(target=_issue_request, args=(self.scheme, self.host, self.port)).start()


def _render_browsersync(port):
    from flask import request
    return f'<script src="//{request.host}:{port}/browser-sync/browser-sync-client.js" async defer></script>'


def _timestamp_static_file(endpoint, values):
    # http://flask.pocoo.org/snippets/40/
    # http://www.subdimension.co.uk/2012/05/31/Flask_Response_headers_and_IEs_cache.html
    # https://gist.github.com/iximiuz/f16779933ceee3a9d181
    # https://stackoverflow.com/questions/11997051/flask-url-for-no-cache
    if 'static' == endpoint:
        values['ts'] = int(time.time())


def _issue_request(scheme, host, port):
    urllib.request.urlopen(f'{scheme}://{host}:{port}/__browser_sync__?method=reload')


# EOF
