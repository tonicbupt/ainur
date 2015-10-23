import os
from cStringIO import StringIO
from flask import Flask
from werkzeug.utils import import_string

from utils import paginator_kwargs

blueprints = (
    'index',
    'deploy',
)

def create_app():
    app = Flask('Ainur', static_url_path='/static')
    app.secret_key = os.urandom(24)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    # http://stackoverflow.com/a/11163649
    class _WSGICopyBody(object):
        def __init__(self, application):
            self.application = application

        def __call__(self, environ, start_response):
            try:
                length = int(environ.get('CONTENT_LENGTH', '0'))
            except ValueError:
                length = 0

            body = environ['wsgi.input'].read(length)
            environ['body_copy'] = body
            environ['wsgi.input'] = StringIO(body)

            return self.application(environ, self._sr_callback(start_response))

        def _sr_callback(self, start_response):
            def callback(status, headers, exc_info=None):
                start_response(status, headers, exc_info)
            return callback

    app.wsgi_app = _WSGICopyBody(app.wsgi_app)

    for bp in blueprints:
        import_name = '%s.%s:bp' % (__package__, bp)
        app.register_blueprint(import_string(import_name))

    for fl in (max, min, paginator_kwargs):
        app.add_template_global(fl)

    return app
