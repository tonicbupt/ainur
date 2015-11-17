import os
from cStringIO import StringIO
from flask import Flask, g, request, render_template
from werkzeug.utils import import_string

from config import REDIS_HOST, REDIS_PORT, SQLALCHEMY_DATABASE_URI
from utils import paginator_kwargs, login_url
from .ext import rds, safe_rds_hgetall
from models.base import init_db
from models.user import User

blueprints = (
    'index',
    'user',
    'deploy',
    'lb',
    'settings',
)

def create_app():
    app = Flask('Ainur', static_url_path='/static')
    app.secret_key = os.urandom(24)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.config['REDIS_URL'] = 'redis://%s:%d/0' % (REDIS_HOST, REDIS_PORT)
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

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
    rds.init_app(app)
    init_db(app)

    for bp in blueprints:
        import_name = '%s.%s:bp' % (__package__, bp)
        app.register_blueprint(import_string(import_name))

    for fl in (max, min, paginator_kwargs, login_url):
        app.add_template_global(fl)

    @app.before_request
    def init_global_vars():
        g.page = request.args.get('page', type=int, default=0)
        g.start = request.args.get('start', type=int, default=g.page * 20)
        g.limit = request.args.get('limit', type=int, default=20)

        user_info = safe_rds_hgetall('user_session:%s' % request.cookies.get('idkey'))
        g.user = User.get_by_uid(user_info['uid']) if user_info else None

    @app.errorhandler(403)
    @app.errorhandler(401)
    def error_handler(e):
        return render_template('errors/%s.html' % e.code), e.code

    return app
