# coding: utf-8

import logging
import json
from datetime import date, datetime
from retrying import retry
from flask import render_template, Blueprint, request, g, url_for, abort, redirect

from config import APPNAME_ERU_LB
from clients import eru
from utils import demand_login, json_api, SIX_MONTHS
from models.balancer import Balancer, BalanceRecord
from .ext import rds

bp = Blueprint('lb', __name__, url_prefix='/lb')


@bp.route('/')
def index():
    balancers = Balancer.get_by_user(g.user.id)
    return render_template('lb/index.html', balancers=balancers)


def _push_to_today_task(act, args):
    task_key = date.today().strftime('lbaudit:%Y-%m-%d')
    rds.lpush(task_key, json.dumps({
        'time': datetime.now().strftime('%H:%M:%S'),
        'user': g.user.uid,
        'act': act,
        'args': args,
    }))
    rds.expire(task_key, SIX_MONTHS)


@json_api
def _create_lb_container(args):
    if g.user.group is None:
        raise ValueError('you are not in a group')
    container_id = deploy_container(
        g.user.group, args['pod'], args['entrypoint'], args['version'],
        args['env'], args['host'])

    container = eru.get_container(container_id)
    Balancer.create(container['host'], g.user.group, g.user.id, container_id)
    _push_to_today_task('create', request.form)


@bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'GET':
        images = eru.list_app_images(APPNAME_ERU_LB)
        image_names = [i['image_url'] for i in images]
        return render_template(
            'lb/create.html', appname=APPNAME_ERU_LB, images=image_names,
            envs=eru.list_app_env_names(APPNAME_ERU_LB)['data'],
            pods=eru.list_pods())
    return _create_lb_container(request.form)


@bp.route('/<int:balancer_id>/records', methods=['GET', 'POST'])
def records(balancer_id):
    balancer = Balancer.query.get_or_404(balancer_id)
    if request.method == 'GET':
        return render_template('lb/balancer.html', b=balancer)

    appname = request.form['appname']
    domain = request.form['domain']
    entrypoint = request.form['entrypoint']
    logging.debug('Add record for %s:%s @ %s', appname, entrypoint, domain)

    balancer.add_record(appname, entrypoint, domain)
    _push_to_today_task('add_record', request.form)
    return redirect(url_for('lb.records', balancer_id=balancer_id))


@bp.route('/api/<int:balancer_id>', methods=['DELETE'])
@json_api
@demand_login
def delete_balancer(balancer_id):
    balancer = Balancer.query.get_or_404(balancer_id)
    if g.user.id != balancer.user_id:
        return {'msg': 'forbidden'}, 403

    eru.remove_containers([balancer.container_id])
    _push_to_today_task('delete', {'balancer': balancer.id,
                                   'container': balancer.container_id})
    balancer.delete()


@bp.route('/api/record/<int:record_id>', methods=['DELETE'])
@json_api
@demand_login
def delete_record(record_id):
    record = BalanceRecord.get(record_id)
    if not record:
        return {'msg': 'not found'}, 404

    if g.user.id != record.balancer.user_id:
        return {'msg': 'forbidden'}, 403

    record.delete()


@bp.route('/audit/')
def audit_logs():
    dt = request.query_string or date.today().strftime('%Y-%m-%d')
    return render_template('lb/audit.html', date=dt, logs=[
        json.loads(x) for x in rds.lrange('lbaudit:%s' % dt, 0, -1)])


@bp.before_request
@demand_login
def access_control():
    if not g.user.is_lb_mgr():
        abort(403)


@retry(stop_max_attempt_number=64, wait_fixed=500)
def poll_task_for_container_id(task_id):
    r = eru.get_task(task_id)
    if r['result'] != 1:
        raise ValueError('task not finished: %s' % r)
    try:
        return r['props']['container_ids'][0]
    except LookupError:
        raise ValueError('Eru returns invalid container info task<%d>: %s' %
                         (task_id, r))


def deploy_container(group, pod, entrypoint, version, env, host):
    r = eru.deploy_private(
        group_name=group,
        pod_name=pod,
        app_name=APPNAME_ERU_LB,
        ncore=1.0,
        ncontainer=1,
        version=version,
        entrypoint=entrypoint,
        env=env,
        network_ids=[],
        host_name=host,
    )
    try:
        task_id = r['tasks'][0]
        logging.info('Task created: %s', task_id)
    except LookupError:
        raise ValueError('eru fail to create a task ' + str(r))
    return poll_task_for_container_id(task_id)
