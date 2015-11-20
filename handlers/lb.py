# coding: utf-8

import logging
from datetime import datetime
from retrying import retry
from flask import render_template, Blueprint, request, g, url_for, abort, redirect

from libs.clients import eru
from libs.utils import demand_login, json_api
from config import APPNAME_ERU_LB
from models.oplog import OPLog
from models.consts import OPLOG_ACTION, OPLOG_KIND, LB_IMAGE, LB_ENTRY_BETA, LB_ENV_BETA
from models.balancer import Balancer, BalanceRecord

bp = Blueprint('lb', __name__, url_prefix='/lb')


@bp.route('/')
def index():
    balancers = Balancer.get_by_user(g.user.id)
    return render_template('lb/index.html', balancers=balancers)


@json_api
def _create_lb_container(pod, host):
    if not g.user.group:
        raise ValueError('you are not in a group')

    version = LB_IMAGE.split(':')[1]
    container_id = deploy_container(g.user.group, pod, LB_ENTRY_BETA, version, LB_ENV_BETA, host)

    container = eru.get_container(container_id)
    b = Balancer.create(container['host'], g.user.group, g.user.id, container_id)

    log = OPLog.create(g.user.id, OPLOG_ACTION.create_balancer)
    log.container_id = container_id
    log.balancer_id = b.id
    log.data = {'host': host, 'pod': pod}


@bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'GET':
        images = eru.list_app_images(APPNAME_ERU_LB)
        image_names = [i['image_url'] for i in images]
        print image_names
        pods = eru.list_group_pods(g.user.group)
        envs = eru.list_app_env_names(APPNAME_ERU_LB)['data']
        return render_template('/lb/create.html', appname=APPNAME_ERU_LB,
                images=image_names, envs=envs, pods=pods)

    pod = request.form['pod']
    host = request.form['host']
    return _create_lb_container(pod, host)


@bp.route('/<int:balancer_id>/records', methods=['GET', 'POST'])
def records(balancer_id):
    balancer = Balancer.get(balancer_id)
    if not balancer:
        abort(404)

    if request.method == 'GET':
        return render_template('lb/balancer.html', b=balancer)

    appname = request.form['appname']
    domain = request.form['domain']
    entrypoint = request.form['entrypoint']

    r = balancer.add_record(appname, entrypoint, domain)

    log = OPLog.create(g.user.id, OPLOG_ACTION.create_lb_record)
    log.balancer_id = balancer_id
    log.record_id = r.id
    log.data = {'domain': domain, 'appname': appname, 'entrypoint': entrypoint}

    return redirect(url_for('lb.records', balancer_id=balancer_id))


@bp.route('/api/<int:balancer_id>', methods=['DELETE'])
@json_api
@demand_login
def delete_balancer(balancer_id):
    balancer = Balancer.get(balancer_id)
    if not balancer:
        abort(404)

    if g.user.id != balancer.user_id:
        return {'msg': 'forbidden'}, 403

    eru.remove_containers([balancer.container_id])
    balancer.delete()

    log = OPLog.create(g.user.id, OPLOG_ACTION.delete_balancer)
    log.balancer_id = balancer_id
    log.container_id = balancer.container_id


@bp.route('/api/record/<int:record_id>', methods=['DELETE'])
@json_api
@demand_login
def delete_record(record_id):
    r = BalanceRecord.get(record_id)
    if not r:
        return {'msg': 'not found'}, 404

    if g.user.id != r.balancer.user_id:
        return {'msg': 'forbidden'}, 403

    r.delete()

    log = OPLog.create(g.user.id, OPLOG_ACTION.delete_lb_record)
    log.balancer_id = r.balancer_id
    log.record_id = record_id
    log.data = {'domain': r.domain, 'appname': r.appname, 'entrypoint': r.entrypoint}


@bp.route('/oplog/')
def oplog():
    date = request.args.get('date', None)
    if date:
        date = datetime.strptime(date, '%Y-%m-%d')
    # FIXME
    date = None
    logs = OPLog.get_by_user_id(g.user.id, kind=OPLOG_KIND.balancer,
            time=date, start=g.start, limit=g.limit)
    return render_template('/lb/logs.html', logs=logs)


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
