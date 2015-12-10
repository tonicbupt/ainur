# coding: utf-8

import requests
from flask import render_template, Blueprint, request, g, redirect, session

from config import OPENID_PROFILE_URL
from models.user import User

bp = Blueprint('user', __name__, url_prefix='/user')


@bp.route('/logout/')
def logout():
    session.pop('uid', None)
    return redirect('/')


@bp.route('/me')
def display_my_info():
    return render_template('user/myinfo.html', who=g.user)


@bp.route('/login_from_openid/')
def login_from_openid():
    r = requests.get(OPENID_PROFILE_URL, params={'token': request.args['token']})
    user_info = r.json()

    uid = user_info.get('uid', '') or user_info.get('name', '')
    if not uid:
        return redirect('/')

    realname = user_info.get('realname', '')
    user = User.get_or_create(uid, realname)
    session['uid'] = user.uid
    return redirect('/')
