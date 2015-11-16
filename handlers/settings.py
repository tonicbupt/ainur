from flask import render_template, Blueprint, request, g

from utils import json_api, demand_login, forbid
from models.base import db
from models.base_image import BaseImage
from models.user import User
import models.user
from .ext import rds

bp = Blueprint('settings', __name__, url_prefix='/settings')


@bp.route('/')
def images():
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
    BaseImage.delete(int(request.form['id']))
    _reset_images_cache()


@bp.route('/users/')
def list_users():
    return render_template('settings/list_users.html',
                           users=User.list(g.start, g.limit, User.uid.asc()))


@bp.route('/users/<uid>/')
def user_detail(uid):
    return render_template('settings/user_detail.html',
                           who=User.query.filter_by(uid=uid).first_or_404())


@bp.route('/api/users/setting', methods=['POST'])
@json_api
def set_user():
    u = User.query.filter_by(uid=request.form['uid']).one()
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
@demand_login
def access_control():
    if not g.user.is_admin():
        return forbid()
