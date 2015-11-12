import json
import urllib
import urllib2
from uuid import uuid4
from flask import render_template, Blueprint, request, g, redirect

from utils import json_api, demand_login
from .ext import rds, safe_rds_get, safe_rds_set
from config import DEBUG
from models.user import User

bp = Blueprint('user', __name__, url_prefix='/user')

COOKIE_AGE = int(86400 * 13.5)


@bp.route('/logout')
def logout():
    r = redirect('/')
    if 'idkey' in request.cookies:
        rds.delete('user_session:%s' % request.cookies['idkey'])
        r.set_cookie('idkey', '')
    return r


@bp.route('/me')
@demand_login
def display_my_info():
    return render_template('user/myinfo.html', who=g.user)


def _login_redirect(user_info):
    user = User.get_by_uid(user_info['uid'])
    if user is None:
        user = User(uid=user_info['uid'], realname=user_info['realname'])
        user.save()
    key = uuid4().hex
    session_key = 'user_session:%s' % key
    rds.hmset(session_key, {
        'uid': user.uid,
        'realname': user.realname,
        'admin': 't' if user.is_admin else '',
        'lb': 't' if user.is_lb_mgr else '',
    })
    rds.expire(session_key, COOKIE_AGE)
    r = redirect('/')
    r.set_cookie('idkey', key, max_age=COOKIE_AGE)
    return r


@bp.route('/login_from_openid/')
def login_from_openid():
    r = urllib2.urlopen('http://openids-web.intra.hunantv.com/oauth/profile/?'
                        + urllib.urlencode({'token': request.args['token']}))
    return _login_redirect(json.loads(r.read()))
