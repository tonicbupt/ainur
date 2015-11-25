# coding: utf-8

from flask import Flask, g, request, render_template, abort, session
from werkzeug.utils import import_string

from libs.ext import rds, db
from libs.utils import paginator_kwargs, login_url
from models.user import User

blueprints = (
    'lb',
    'user',
    'index',
    'deploy',
    'settings',
    # ajax blueprints
    'ajax.lb',
)

def create_app():
    app = Flask('Ainur', static_url_path='/static')
    app.config.from_object('config')
    app.secret_key = app.config['SECRET']

    db.init_app(app)
    db.app = app
    db.create_all()
    rds.init_app(app)

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

        if request.path == '/user/login_from_openid/' or request.path.startswith('/ajax'):
            return

        if 'uid' not in session:
            abort(401)
        g.user = User.get_by_uid(session['uid'])

    @app.errorhandler(403)
    @app.errorhandler(401)
    def error_handler(e):
        return render_template('errors/%s.html' % e.code), e.code

    return app
