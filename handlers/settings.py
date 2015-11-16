from flask import render_template, Blueprint, request, g

from utils import json_api, demand_login, forbid
from models.base import db
from models.base_image import BaseImage
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


@bp.before_request
@demand_login
def access_control():
    if not g.user['admin']:
        return forbid()
