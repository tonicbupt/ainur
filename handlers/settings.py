# coding: utf-8

from flask import render_template, Blueprint, request, g, abort

from libs.utils import json_api
from models.image import BaseImage
from models.user import User
from models.project import Project
from models.oplog import OPLog
from models.consts import USER_ROLE, OPLOG_ACTION


bp = Blueprint('settings', __name__, url_prefix='/settings')


@bp.route('/')
def index():
    return render_template('settings/base_images.html',
                           images=BaseImage.query.all())


@bp.route('/api/add_image', methods=['POST'])
@json_api
def add_image():
    BaseImage(name=request.form['name']).save()


@bp.route('/api/del_image', methods=['POST'])
@json_api
def del_image():
    BaseImage.delete_by_id(int(request.form['id']))


@bp.route('/users/')
def list_users():
    users = User.get_all(g.start, g.limit)
    return render_template('/settings/list_users.html', users=users)


@bp.route('/users/<uid>/')
def user_detail(uid):
    user = User.get_by_uid(uid)
    if not user:
        abort(404)
    return render_template('/settings/user_detail.html', user=user)


@bp.route('/users/<uid>/projects', methods=['POST'])
@json_api
def grant_project(uid):
    user = User.get_by_uid(uid)
    if not user:
        return {'reason': '用户不存在'}, 404

    name = request.form.get('project', '')
    p = Project.get_by_name(name)
    if not p:
        return {'reason': '项目不存在'}, 404

    user.grant_project(name)
    log = OPLog.create(g.user.id, OPLOG_ACTION.grant_project)
    log.project_name = name
    log.acceptor = user.uid


@bp.route('/api/users/setting', methods=['POST'])
@json_api
def set_user():
    u = User.get_by_uid(request.form['uid'])
    if u is None:
        raise ValueError('no such user')

    group = request.form['group']
    if group:
        u.set_group(group)

    flags = request.form.getlist('privs')
    privilege = reduce(lambda x, y: x | y, [getattr(USER_ROLE, p.lower(), 0) for p in flags], 0)
    u.set_privilege(privilege)

    log = OPLog.create(g.user.id, OPLOG_ACTION.grant_privilege)
    log.privilege = privilege
    log.acceptor = u.uid


@bp.before_request
def access_control():
    if not g.user.is_admin():
        abort(403)
