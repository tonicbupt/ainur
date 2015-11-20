# coding: utf-8

from flask import render_template, Blueprint, request, g, abort

from libs.ext import rds
from libs.utils import json_api
from models.image import BaseImage
from models.user import User
from models.project import Project
import models.user

bp = Blueprint('settings', __name__, url_prefix='/settings')


@bp.route('/')
def index():
    return render_template('settings/base_images.html',
                           images=BaseImage.query.all())


def _reset_images_cache():
    rds.delete('base_images')
    rds.lpush('base_images', *[i.name for i in BaseImage.query.all()])


@bp.route('/api/add_image', methods=['POST'])
@json_api
def add_image():
    BaseImage(name=request.form['name']).save()
    _reset_images_cache()


@bp.route('/api/del_image', methods=['POST'])
@json_api
def del_image():
    BaseImage.delete_by_id(int(request.form['id']))
    _reset_images_cache()


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


@bp.route('/api/users/setting', methods=['POST'])
@json_api
def set_user():
    u = User.get_by_uid(request.form['uid'])
    if u is None:
        raise ValueError('no such user')
    u.group = request.form['group']
    u.priv_flags = reduce(
        lambda x, y: x | y,
        [getattr(models.user, 'PRIV_' + p.upper())
         for p in request.form.getlist('privs')],
        0)
    u.save()


@bp.before_request
def access_control():
    if not g.user.is_admin():
        abort(403)
