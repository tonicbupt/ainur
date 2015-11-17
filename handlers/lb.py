# coding: utf-8

from flask import render_template, Blueprint, request, g, url_for, abort, redirect

from utils import demand_login
from models.balancer import Balancer, update_record

bp = Blueprint('lb', __name__, url_prefix='/lb')


@bp.route('/')
def index():
    balancers = Balancer.get_by_user(g.user.id)
    return render_template('lb/index.html', balancers=balancers)


@bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'GET':
        return 'get create page'

    # TODO create container
    container_id = 'xxx'
    Balancer.create(g.user.group, g.user.id, container_id)
    return redirect(url_for('lb.index'))


@bp.route('/<int:balancer_id>/records', methods=['GET', 'POST'])
def records(balancer_id):
    balancer = Balancer.get(balancer_id)
    if not balancer:
        abort(404)

    if request.method == 'GET':
        return 'get records page'

    appname = request.form['appname']
    domain = request.form['domain']
    entrypoint = request.form['entrypoint']

    record = balancer.add_record(appname, entrypoint, domain)
    update_record(balancer, record)
    return redirect(url_for('lb.records', balancer_id=balancer_id))


@bp.before_request
@demand_login
def access_control():
    if not g.user.is_lb_mgr():
        abort(403)
